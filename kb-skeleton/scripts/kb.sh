#!/bin/sh

SCRIPT_PATH=$0
while [ -L "$SCRIPT_PATH" ]; do
    SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd)
    LINK_TARGET=$(readlink "$SCRIPT_PATH") || exit 1
    case "$LINK_TARGET" in
        /*) SCRIPT_PATH=$LINK_TARGET ;;
        *) SCRIPT_PATH=$SCRIPT_DIR/$LINK_TARGET ;;
    esac
done

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd)
PLUGIN_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
PYTHON=${KNOWLEDGE_BUNDLE_PYTHON:-"$DATA_HOME/kb-skeleton/venv/bin/python"}

if [ ! -x "$PYTHON" ]; then
    PYTHON=$PLUGIN_ROOT/.venv/bin/python
fi

if [ ! -x "$PYTHON" ]; then
    printf '%s\n' "No Python environment found. Run: python3 \"$PLUGIN_ROOT/scripts/setup_plugin.py\"" >&2
    exit 1
fi

cd "$PLUGIN_ROOT" || exit 1
exec "$PYTHON" "$@"
