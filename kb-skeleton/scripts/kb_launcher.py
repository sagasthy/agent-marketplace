#!/usr/bin/env python3
"""Select the platform-specific venv interpreter and launch the MCP module."""

import os
import subprocess
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def is_executable(path: Path) -> bool:
    return path.is_file() and (os.name == "nt" or os.access(path, os.X_OK))


def interpreter_candidates() -> list[Path]:
    candidates: list[Path] = []
    override = os.environ.get("KNOWLEDGE_BUNDLE_PYTHON")
    if override:
        candidates.append(Path(override).expanduser())

    data_home = os.environ.get("XDG_DATA_HOME") or str(
        Path.home() / ".local" / "share"
    )
    candidates.append(venv_python(Path(data_home).expanduser() / "kb-skeleton" / "venv"))
    candidates.append(venv_python(PLUGIN_ROOT / ".venv"))
    return candidates


def main() -> int:
    interpreter = next(
        (candidate for candidate in interpreter_candidates() if is_executable(candidate)),
        None,
    )
    if interpreter is None:
        print(
            f"No Python environment found. Run: python \"{PLUGIN_ROOT / 'scripts' / 'setup_plugin.py'}\"",
            file=sys.stderr,
        )
        return 1

    return subprocess.call([str(interpreter), *sys.argv[1:]], cwd=PLUGIN_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
