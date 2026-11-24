"""stdio MCP server exposing diagnostics for the kb-skeleton plugin."""

import json
import os
import platform
import sys
import tempfile
from pathlib import Path

from mcp.server import MCPServer


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
mcp = MCPServer("skeleton-bundle")


def _case_sensitive_filesystem(path: Path) -> bool:
    with tempfile.TemporaryDirectory(dir=path) as temp_dir:
        probe = Path(temp_dir) / "caseprobe"
        probe.touch()
        return not (Path(temp_dir) / "CASEPROBE").exists()


@mcp.tool()
def ping() -> str:
    """Return a simple health-check response."""
    return "pong"


@mcp.tool()
def env_info() -> str:
    """Return runtime and platform details without exposing secret values."""
    plugin_environment = {}
    for name, value in os.environ.items():
        if "PLUGIN" not in name.upper():
            continue
        upper_name = name.upper()
        plugin_environment[name] = (
            name
            if any(marker in upper_name for marker in ("KEY", "TOKEN", "SECRET"))
            else value
        )

    details = {
        "executable": sys.executable,
        "version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cwd": os.getcwd(),
        "plugin_environment": plugin_environment,
        "filesystem_case_sensitive": _case_sensitive_filesystem(Path.cwd()),
    }
    return json.dumps(details)


@mcp.tool()
def path_check(name: str) -> str:
    """Check a path contained within the plugin root."""
    path = (PLUGIN_ROOT / name).resolve()
    try:
        path.relative_to(PLUGIN_ROOT)
    except ValueError as exc:
        raise ValueError("path must remain within the plugin root") from exc

    return json.dumps(
        {
            "path": str(path),
            "exists": path.exists(),
            "is_file": path.is_file(),
            "is_executable": os.access(path, os.X_OK),
        }
    )


@mcp.tool()
def echo_args() -> str:
    """Return the process argument vector as JSON."""
    return json.dumps(sys.argv)


if __name__ == "__main__":
    mcp.run(transport="stdio")
