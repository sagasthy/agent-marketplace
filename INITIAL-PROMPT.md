Create a minimal, self-contained skeleton VS Code/Copilot plugin called "kb-skeleton" in the current folder, to verify macoS-specific launcher and MCP behavior. Use only public, generic code. Do not fetch or reference any internal repositories.
Layout:
kb-skeleton/ plugin. json
(name, version, mcp reference; minimal)
.mcp.json
(Windows variant: cmd.exe /d /c ${PLUGIN_ROOT}\scripts\kb.cmd -m skeleton_mcp
- kept for parity, expected NOT to start on macos)
.mcp.unix.json
(command: ${PLUGIN_ROOT}/scripts/kb.sh, args: ["-m","skeleton_mcp"], type
stdio, server name "skeleton-bundle")
. gitattributes
(*.sh text eol=lf)
pyproject. toml
(setuptools, requires-python >=3.12, src layout, no dependencies except "mcp")
src/skeleton_mcp/__init__.py
src/skeleton_mcp/__main__.py (stdio MCP server using the officialimcp' package, with tools:
ping() > "pong";
env_info) > JSON of sys.executable, sys.version, platform.platform(), platform.machine(), os.getcwd(), PLUGIN-related env vars (names only for anything containing KEY/TOKEN/SECRET), and whether the filesystem is case-sensitive;
path_check(name) > exists/is-file/is-executable for a path relative to the plugin root;
echo_args () > sys.argv)
scripts/kb.sh
(POSIX sh launcher; exact same logic as below)
scripts/setup_plugin.py
(creates venv at $fXDG_DATA_HOME:-~/.local/share}/kb-skeleton/venv, pip
installs -e., runs pip check; --venv-dir option; leaves existing venv alone)
scripts/check.sh
(self-test script, see below)
tests/test_launcher.py
(pytest)
README. md
(how to run the checks)
kb.sh logic to mirror:
kb_pvthon="${KNOWLEDGE_BUNDLE_PYTHON:-$fXDG_DATA_HOМЕ:-$HOME/.local/share?/kb-skeleton/venv/bin/pvthon?"
fall back to "$(dirname "$0")/../.venv/bin/python" if the first is not executable if still not executable: print a setup message to stderr and exit 1
Make kb.sh executable (chmod +x).
scripts/check.sh must run and report PASS/FAIL for each:
1. kb.sh is executable, has LF endings, no CRLF
2. kb.sh with no venv exits 1 with the setup message
3. KNOWLEDGE_BUNDLE_PYTHON override is honored
4. custom XDG_DATA_HOME is honored by both setup_plugin.py and kb.sh
5. kb.sh works through a symlink and from a different cwd
6. kb.sh works from a path containing spaces
7. legacy .venv fallback works
8. mcp.unix. json is valid JSON, and its command resolves to an executable file after substituting
${PLUGIN_ROOT}
9. MCP handshake: send an initialize + tools/list + tools/call ping over stdio to 'kb.sh -m skeleton_mcp' and verify responses
10. print uname -a, swivers, arch, python version, shell, filesystem case sensitivity, and whether the process runs under Rosetta
Exit non-zero if any check fails.
Also write pytest tests covering the same behaviors, skipping the windows-only ones on non-Windows.
Finally, add instructions in README.md for registering the folder in VS Code (chat.pluginLocations / MCP: List Servers) and how to confirm the "skeleton-bundle" server shows as running and its tools are callable from Copilot Chat. Do not use any real tokens or network calls other than pip installing public packages.