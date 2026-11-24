"""Focused launcher, MCP, and platform checks for kb-skeleton."""

import asyncio
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
IS_WINDOWS = os.name == "nt"
POSIX_ONLY = pytest.mark.skipif(IS_WINDOWS, reason="POSIX launcher check")


def copy_plugin(destination: Path) -> Path:
    target = destination / "kb-skeleton"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        PLUGIN_ROOT,
        target,
        ignore=shutil.ignore_patterns(".venv", "__pycache__", "*.egg-info"),
    )
    return target


def launcher_env(**updates: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "HOME": str(Path.cwd()),
            "XDG_DATA_HOME": str(Path.cwd() / "missing-xdg"),
            "KNOWLEDGE_BUNDLE_PYTHON": "",
        }
    )
    environment.update(updates)
    return environment


def run_launcher(
    root: Path,
    *arguments: str,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(root / "scripts" / "kb.sh"), *arguments],
        cwd=cwd or root,
        env=env or launcher_env(),
        capture_output=True,
        text=True,
        check=False,
    )


def load_setup_module():
    module_path = PLUGIN_ROOT / "scripts" / "setup_plugin.py"
    spec = importlib.util.spec_from_file_location("kb_skeleton_setup", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@POSIX_ONLY
def test_launcher_mode_and_line_endings() -> None:
    launcher = PLUGIN_ROOT / "scripts" / "kb.sh"
    content = launcher.read_bytes()
    assert os.access(launcher, os.X_OK)
    assert b"\r\n" not in content
    assert content.endswith(b"\n")


@POSIX_ONLY
def test_missing_environment_shows_setup_message(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path)
    environment = launcher_env(
        HOME=str(tmp_path / "home"),
        XDG_DATA_HOME=str(tmp_path / "xdg"),
        KNOWLEDGE_BUNDLE_PYTHON=str(tmp_path / "not-python"),
    )
    result = run_launcher(root, "-c", "print('unexpected')", env=environment)
    assert result.returncode == 1
    assert "Run:" in result.stderr and "setup_plugin.py" in result.stderr


@POSIX_ONLY
def test_python_override_is_used(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path)
    result = run_launcher(
        root,
        "-c",
        "import sys; print(sys.executable)",
        env=launcher_env(KNOWLEDGE_BUNDLE_PYTHON=sys.executable),
    )
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == Path(sys.executable).resolve()


@POSIX_ONLY
def test_custom_xdg_path_is_used(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path)
    xdg_home = tmp_path / "custom-xdg"
    interpreter = xdg_home / "kb-skeleton" / "venv" / "bin" / "python"
    interpreter.parent.mkdir(parents=True)
    interpreter.symlink_to(sys.executable)

    result = run_launcher(
        root,
        "-c",
        "import sys; print(sys.executable)",
        env=launcher_env(
            HOME=str(tmp_path / "home"),
            XDG_DATA_HOME=str(xdg_home),
        ),
    )
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == Path(sys.executable).resolve()

    setup = load_setup_module()
    setup_path = setup.default_venv_dir(
        {"HOME": str(tmp_path / "home"), "XDG_DATA_HOME": str(xdg_home)}
    )
    assert setup_path == xdg_home / "kb-skeleton" / "venv"


@POSIX_ONLY
def test_symlink_and_other_working_directory(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path)
    link_dir = tmp_path / "links"
    link_dir.mkdir()
    symlink = link_dir / "kb.sh"
    symlink.symlink_to(root / "scripts" / "kb.sh")
    other_cwd = tmp_path / "elsewhere"
    other_cwd.mkdir()
    result = subprocess.run(
        [str(symlink), "-c", "import os; print(os.getcwd())"],
        cwd=other_cwd,
        env=launcher_env(KNOWLEDGE_BUNDLE_PYTHON=sys.executable),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == root.resolve()


@POSIX_ONLY
def test_path_with_spaces(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path / "directory with spaces")
    result = run_launcher(
        root,
        "-c",
        "print('space-ok')",
        env=launcher_env(KNOWLEDGE_BUNDLE_PYTHON=sys.executable),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "space-ok"


@POSIX_ONLY
def test_legacy_venv_fallback(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path)
    interpreter = root / ".venv" / "bin" / "python"
    interpreter.parent.mkdir(parents=True)
    interpreter.symlink_to(sys.executable)
    result = run_launcher(root, "-c", "print('legacy-ok')")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "legacy-ok"


@POSIX_ONLY
def test_portable_launcher_uses_custom_xdg_venv(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path)
    xdg_home = tmp_path / "custom-xdg"
    interpreter = xdg_home / "kb-skeleton" / "venv" / "bin" / "python"
    interpreter.parent.mkdir(parents=True)
    interpreter.symlink_to(sys.executable)
    environment = launcher_env(
        HOME=str(tmp_path / "home"),
        XDG_DATA_HOME=str(xdg_home),
        KNOWLEDGE_BUNDLE_PYTHON="",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "kb_launcher.py"),
            "-c",
            "print('portable-ok')",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "portable-ok"


def test_portable_mcp_config_targets_cross_platform_launcher() -> None:
    manifest = json.loads((PLUGIN_ROOT / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert manifest["name"] == "kb-skeleton"

    config_path = PLUGIN_ROOT / "mcp.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["$schema"] == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    server = config["mcpServers"]["skeleton-bundle"]
    assert server["type"] == "stdio"
    assert server["command"] == "python3"
    launcher_path = server["args"][0].replace("${PLUGIN_ROOT}", str(PLUGIN_ROOT))
    assert Path(launcher_path).is_file()
    assert Path(launcher_path).name == "kb_launcher.py"


def test_marketplace_catalog_references_plugin() -> None:
    catalog = json.loads(
        (PLUGIN_ROOT.parent / "marketplace.json").read_text(encoding="utf-8")
    )
    entry = next(
        plugin for plugin in catalog["plugins"] if plugin["name"] == "kb-skeleton"
    )
    assert entry["source"] == "./kb-skeleton"
    plugin_manifest = json.loads(
        (PLUGIN_ROOT / "plugin.json").read_text(encoding="utf-8")
    )
    assert entry["version"] == plugin_manifest["version"]


def test_stdio_mcp_handshake_and_tools() -> None:
    from mcp import Client, StdioServerParameters

    async def verify() -> None:
        environment = os.environ.copy()
        environment["KNOWLEDGE_BUNDLE_PYTHON"] = sys.executable
        existing_pythonpath = environment.get("PYTHONPATH")
        source_path = str(PLUGIN_ROOT / "src")
        environment["PYTHONPATH"] = os.pathsep.join(
            item for item in (source_path, existing_pythonpath) if item
        )
        parameters = StdioServerParameters(
            command=str(PLUGIN_ROOT / "scripts" / "kb.sh"),
            args=["-m", "skeleton_mcp"],
            env=environment,
            cwd=str(PLUGIN_ROOT),
        )
        async with Client(parameters, mode="legacy") as client:
            tools = await client.list_tools()
            names = {tool.name for tool in tools.tools}
            assert {"ping", "env_info", "path_check", "echo_args"} <= names
            result = await client.call_tool("ping", arguments={})
            assert result.is_error is not True
            assert result.content[0].text == "pong"

            info_result = await client.call_tool("env_info", arguments={})
            info = json.loads(info_result.content[0].text)
            assert {
                "executable",
                "version",
                "platform",
                "machine",
                "cwd",
                "plugin_environment",
                "filesystem_case_sensitive",
            } <= info.keys()

            path_result = await client.call_tool(
                "path_check", arguments={"name": "plugin.json"}
            )
            path_info = json.loads(path_result.content[0].text)
            assert path_info["exists"] and path_info["is_file"]

    asyncio.run(verify())


def test_portable_mcp_config_starts_server() -> None:
    from mcp import Client, StdioServerParameters

    config = json.loads((PLUGIN_ROOT / "mcp.json").read_text(encoding="utf-8"))
    server = config["mcpServers"]["skeleton-bundle"]
    environment = os.environ.copy()
    environment["KNOWLEDGE_BUNDLE_PYTHON"] = sys.executable
    environment["PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    args = [
        argument.replace("${PLUGIN_ROOT}", str(PLUGIN_ROOT))
        for argument in server["args"]
    ]
    parameters = StdioServerParameters(
        command=server["command"],
        args=args,
        env=environment,
        cwd=str(PLUGIN_ROOT),
    )

    async def verify() -> None:
        async with Client(parameters, mode="legacy") as client:
            result = await client.call_tool("ping", arguments={})
            assert result.is_error is not True
            assert result.content[0].text == "pong"

    asyncio.run(verify())


def test_platform_diagnostics() -> None:
    assert sys.version
    assert sys.platform
    assert os.name


@pytest.mark.skipif(not IS_WINDOWS, reason="Windows command launcher only")
def test_windows_launcher_uses_python_override(tmp_path: Path) -> None:
    root = copy_plugin(tmp_path)
    result = subprocess.run(
        [
            "cmd.exe",
            "/d",
            "/c",
            str(root / "scripts" / "kb.cmd"),
            "-c",
            "print('windows-ok')",
        ],
        env={**os.environ, "KNOWLEDGE_BUNDLE_PYTHON": sys.executable},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "windows-ok" in result.stdout
