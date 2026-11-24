#!/usr/bin/env python3
"""Create and validate the kb-skeleton Python environment."""

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path
from typing import Mapping


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def default_venv_dir(environ: Mapping[str, str] | None = None) -> Path:
    environment = os.environ if environ is None else environ
    data_home = environment.get("XDG_DATA_HOME") or str(
        Path(environment.get("HOME", Path.home())) / ".local" / "share"
    )
    return Path(data_home).expanduser() / "kb-skeleton" / "venv"


def python_in(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    if sys.version_info < (3, 12):
        parser.error("Python 3.12 or newer is required to set up kb-skeleton")

    parser.add_argument(
        "--venv-dir",
        type=Path,
        help="use this virtual environment directory instead of the XDG default",
    )
    args = parser.parse_args()
    venv_dir = (args.venv_dir or default_venv_dir()).expanduser().resolve()
    interpreter = python_in(venv_dir)

    if not interpreter.is_file():
        if venv_dir.exists() and any(venv_dir.iterdir()):
            parser.error(f"existing environment is incomplete; leaving it untouched: {venv_dir}")
        venv.create(venv_dir, with_pip=True)

    if not interpreter.is_file():
        parser.error(f"virtual environment Python was not created: {interpreter}")

    subprocess.run(
        [str(interpreter), "-m", "pip", "install", "-e", str(PLUGIN_ROOT)],
        check=True,
    )
    subprocess.run([str(interpreter), "-m", "pip", "check"], check=True)
    print(f"Environment ready: {venv_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
