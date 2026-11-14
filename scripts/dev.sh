#!/bin/sh
# Run Alto from this clone with its own history and settings, so working on it never touches the installed copy's.
# They are kept in ~/.alto-dev unless ALTO_HOME says otherwise. Arguments are passed on to Alto.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ALTO_HOME="${ALTO_HOME:-$HOME/.alto-dev}"
export ALTO_HOME
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON="$ROOT/.venv/bin/python"; else PYTHON=python3; fi
exec "$PYTHON" -m alto "$@"
