# kb-skeleton

A minimal, self-contained Copilot plugin and stdio MCP server for checking
platform-specific launcher and MCP behavior. The Unix launcher is intended for
macOS; the Windows config and launcher are retained for parity.

## Set up and check

Python 3.12 or newer is required. Create the default virtual environment and
install this package (including the public `mcp` dependency):

```sh
python3 scripts/setup_plugin.py
```

Use a Python 3.12+ executable to run setup (for example, `python3.12` on
macOS or `py -3.12` on Windows). The MCP bootstrap itself can run with the
system `python3` and then dispatches to the installed venv interpreter.

The default environment is
`${XDG_DATA_HOME:-$HOME/.local/share}/kb-skeleton/venv`. To choose another
location, pass `--venv-dir /path/to/venv`. Existing complete environments are
reused rather than recreated.

Run the launcher checks with:

```sh
python3 -m pip install pytest
scripts/check.sh
```

The check script reports each result, then prints OS, architecture, Python,
shell, filesystem case-sensitivity, and Rosetta diagnostics. The MCP handshake
test uses only local stdio; setup is the only step that may access the network,
and only to install public Python packages.

## Install in VS Code

Use **Chat: Open Customizations** > **Plugins** > **Browse Marketplace** and
add `sagasthy/agent-marketplace`. Install `kb-skeleton` after reviewing the
plugin and approving the marketplace trust prompt. For a local checkout, run
**Chat: Install Plugin from Source** and select this folder.

Before using the MCP tools, run `python3 scripts/setup_plugin.py` from the
installed plugin folder in a terminal. Python 3.12 or newer is required. The
script creates the default user-level environment and installs the public MCP
SDK; `--venv-dir` selects a different location.

The portable Agent Plugins manifest declares `mcp.json`, which invokes the
cross-platform `scripts/kb_launcher.py` through `python3`. The launcher selects
the platform-specific executable inside the configured venv (`bin/python` on
macOS, `Scripts/python.exe` on Windows). Make sure the Python 3.12+ installation
is available as `python3` on `PATH`. `scripts/kb.sh`, `scripts/kb.cmd`,
`.mcp.unix.json`, and `.mcp.json` remain as platform-specific launcher/config
fixtures; VS Code uses the portable `mcp.json`.

In **Chat: Open Customizations** > **MCP Servers**, confirm `skeleton-bundle`
shows as running. Its `ping`, `env_info`, `path_check`, and `echo_args` tools
should be callable from Copilot Chat.
