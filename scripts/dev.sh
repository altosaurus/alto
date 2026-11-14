#!/bin/sh
# Run Alto from this clone with its own history and settings, so working on it never touches the installed copy's.
# They are kept in ~/.alto-dev unless ALTO_HOME says otherwise. Arguments are passed on to Alto.
#
# The first run also adds "Alto (dev)" to the application menu, with this clone's icon, so the dock can show an icon for the
# development copy and keep it apart from the installed one. The entry is written only when it is missing or has changed:
# rewriting it makes the desktop read its list of applications again, which reorders the dock. It is independent of the
# installed copy, so uninstalling that leaves it alone. To remove it:
#   rm ~/.local/share/applications/alto-dev.desktop ~/.local/share/icons/hicolor/*/apps/alto-dev.png
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ALTO_HOME="${ALTO_HOME:-$HOME/.alto-dev}"
export ALTO_HOME
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
ICONS="$DATA/icons/hicolor"
DESKTOP_FILE="$DATA/applications/alto-dev.desktop"

NEW="$(mktemp)"
cat >"$NEW" <<EOT
[Desktop Entry]
Type=Application
Name=Alto (dev)
Comment=Music theory trainer, run from $ROOT
Exec=env ALTO_HOME=$ALTO_HOME sh $ROOT/scripts/dev.sh
Icon=alto-dev
Terminal=false
Categories=Education;Music;
EOT
if ! cmp -s "$NEW" "$DESKTOP_FILE" 2>/dev/null; then
    mkdir -p "$DATA/applications" "$ICONS/256x256/apps" "$ICONS/512x512/apps"
    cp "$ROOT/alto/assets/icon-256.png" "$ICONS/256x256/apps/alto-dev.png"
    cp "$ROOT/alto/assets/icon.png" "$ICONS/512x512/apps/alto-dev.png"
    cp "$NEW" "$DESKTOP_FILE"
    chmod 644 "$DESKTOP_FILE"
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA/applications" || true
    command -v gtk-update-icon-cache >/dev/null 2>&1 && [ -f "$ICONS/icon-theme.cache" ] && gtk-update-icon-cache -q -f -t "$ICONS" || true
fi
rm -f "$NEW"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON="$ROOT/.venv/bin/python"; else PYTHON=python3; fi
exec "$PYTHON" -m alto "$@"
