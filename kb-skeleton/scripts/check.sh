#!/bin/sh

set -u
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PLUGIN_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

PYTHON=
for CANDIDATE in python python3 python3.14 python3.13 python3.12; do
    if command -v "$CANDIDATE" >/dev/null 2>&1 &&
        "$CANDIDATE" -c 'import sys; sys.exit(sys.version_info < (3, 12))'
    then
        PYTHON=$(command -v "$CANDIDATE")
        break
    fi
done

if [ -z "$PYTHON" ]; then
    printf '%s\n' 'Python 3.12 or newer is required to run checks.' >&2
    exit 1
fi

CHECKS="
test_launcher_mode_and_line_endings
test_missing_environment_shows_setup_message
test_python_override_is_used
test_custom_xdg_path_is_used
test_symlink_and_other_working_directory
test_path_with_spaces
test_legacy_venv_fallback
test_portable_launcher_uses_custom_xdg_venv
test_portable_mcp_config_targets_cross_platform_launcher
test_marketplace_catalog_references_plugin
test_stdio_mcp_handshake_and_tools
test_portable_mcp_config_starts_server
test_platform_diagnostics
"

FAILURES=0
for CHECK in $CHECKS; do
    if "$PYTHON" -m pytest -q "$PLUGIN_ROOT/tests/test_launcher.py::$CHECK"; then
        printf 'PASS: %s\n' "$CHECK"
    else
        printf 'FAIL: %s\n' "$CHECK"
        FAILURES=$((FAILURES + 1))
    fi
done

printf '\nPlatform diagnostics:\n'
uname -a || FAILURES=$((FAILURES + 1))
if command -v sw_vers >/dev/null 2>&1; then
    sw_vers || FAILURES=$((FAILURES + 1))
else
    printf 'sw_vers: unavailable on this platform\n'
fi
arch || FAILURES=$((FAILURES + 1))
printf '\n'
"$PYTHON" --version || FAILURES=$((FAILURES + 1))
printf 'shell: %s\n' "${SHELL:-unknown}"
"$PYTHON" - "$PLUGIN_ROOT" <<'PY' || FAILURES=$((FAILURES + 1))
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(dir=sys.argv[1]) as directory:
    lower = Path(directory) / "caseprobe"
    lower.touch()
    print(f"filesystem case-sensitive: {not (Path(directory) / 'CASEPROBE').exists()}")
PY
if [ "$(uname -s)" = Darwin ]; then
    TRANSLATED=$(sysctl -in sysctl.proc_translated 2>/dev/null || printf '0')
    if [ "$TRANSLATED" = 1 ]; then
        printf 'Rosetta translation: yes\n'
    else
        printf 'Rosetta translation: no\n'
    fi
else
    printf 'Rosetta translation: not applicable\n'
fi

if [ "$FAILURES" -ne 0 ]; then
    printf '\n%d check(s) failed.\n' "$FAILURES" >&2
    exit 1
fi
printf '\nAll checks passed.\n'
