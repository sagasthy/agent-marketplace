# Agent Marketplace

This repository contains the `kb-skeleton` Copilot Chat plugin.

## Install in VS Code

Use VS Code with Copilot Agent Plugins enabled
(`chat.plugins.enabled: true`). To install directly from this GitHub marketplace,
open this link in VS Code:

[Install kb-skeleton](vscode://chat-plugin/install?source=sagasthy%2Fagent-marketplace&plugin=kb-skeleton)

VS Code will ask you to register the marketplace and install the plugin. Review
the source and approve the trust prompt. You can also install it manually:

1. Run **Chat: Open Customizations** from the Command Palette.
2. Open **Plugins**, then **Browse Marketplace** (or **Browse** and choose
   **Plugin Marketplaces** as the source).
3. Add `sagasthy/agent-marketplace` as a marketplace and install `kb-skeleton`.

To install from a local checkout, run **Chat: Install Plugin from Source** and
select the `kb-skeleton` folder.

After installation, run the plugin's setup script from the installed plugin
folder in a terminal:

```sh
python3.12 scripts/setup_plugin.py
```

Python 3.12 or newer is required (`py -3.12 scripts/setup_plugin.py` on
Windows). The script creates the user-level virtual environment and installs
the public MCP SDK. Start a new Copilot Chat session,
then open **Chat: Open Customizations** > **MCP Servers** and confirm
`skeleton-bundle` is running. The `ping`, `env_info`, `path_check`, and
`echo_args` tools should be available to Chat. Ensure Python is available as
`python3` on `PATH`; on Windows, configure the Python 3 app execution alias or
add the Python 3.12+ install directory to `PATH`. The same portable MCP config
works on Windows and macOS.

See [kb-skeleton/README.md](./kb-skeleton/README.md) for setup options,
diagnostics, Windows parity, and test instructions. Plugins can run code on
your machine; inspect the plugin before trusting it.
