#!/bin/sh
# Install or remove Alto for the current user, from the unpacked Linux download. Nothing here needs root.
#
#   sh install.sh install              copy Alto to ~/.local/opt/alto, link it as ~/.local/bin/alto and add it to the application menu
#   sh install.sh uninstall            remove all of that; keep your practice history and settings
#   sh install.sh uninstall --purge    also delete your practice history and settings
#
# To update, unpack the newer download and run `sh install.sh install` again: it replaces the old files and keeps your data.
# ALTO_PREFIX (default ~/.local) moves the program to $ALTO_PREFIX/opt/alto and the link to $ALTO_PREFIX/bin/alto.
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${ALTO_PREFIX:-$HOME/.local}"
OPT="$PREFIX/opt/alto"
BIN="$PREFIX/bin"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
DESKTOP_FILE="$DATA/applications/alto.desktop"
ICONS="$DATA/icons/hicolor"

# What is ours is told by where it points, so a copy installed another way (alto-install.sh makes the same names) is never touched.
link_is_ours() {
    [ -L "$BIN/alto" ] && [ "$(readlink "$BIN/alto")" = "$OPT/alto" ]
}

entry_is_ours() {
    [ -f "$DESKTOP_FILE" ] && grep -qxF "Exec=\"$OPT/alto\"" "$DESKTOP_FILE"
}

refresh_desktop() {
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA/applications" || true
    command -v gtk-update-icon-cache >/dev/null 2>&1 && [ -f "$ICONS/icon-theme.cache" ] && gtk-update-icon-cache -q -f -t "$ICONS" || true
}

case "${1:-}" in
install)
    [ -x "$HERE/alto/alto" ] || {
        echo "This folder has no alto/alto program. Run install.sh from the folder the download was unpacked to." >&2
        exit 1
    }
    if [ -e "$BIN/alto" ] || [ -L "$BIN/alto" ]; then
        link_is_ours || {
            echo "$BIN/alto already exists and is not from this download, so nothing was changed." >&2
            echo "If it is a copy installed with alto-install.sh, remove it first: sh alto-install.sh uninstall" >&2
            exit 1
        }
    fi
    mkdir -p "$BIN" "$(dirname "$OPT")" "$DATA/applications" "$ICONS/256x256/apps" "$ICONS/512x512/apps"
    rm -rf "$OPT"
    cp -R "$HERE/alto" "$OPT"
    ln -sf "$OPT/alto" "$BIN/alto"
    cp "$HERE/icons/icon-256.png" "$ICONS/256x256/apps/alto.png"
    cp "$HERE/icons/icon.png" "$ICONS/512x512/apps/alto.png"
    cat >"$DESKTOP_FILE" <<EOT
[Desktop Entry]
Type=Application
Name=Alto
Comment=Music theory trainer
Exec="$OPT/alto"
Icon=alto
Terminal=false
Categories=Education;Music;
EOT
    refresh_desktop
    echo "Installed $("$OPT/alto" --version) in $OPT"
    case ":$PATH:" in
    *":$BIN:"*) echo "Start it from the application menu, or with: alto" ;;
    *) echo "Start it from the application menu, or with: $OPT/alto  ($BIN is not on your PATH)" ;;
    esac
    ;;
uninstall)
    if [ ! -d "$OPT" ] && ! link_is_ours; then
        echo "Alto from this download is not installed in $PREFIX."
    else
        link_is_ours && rm -f "$BIN/alto"
        if entry_is_ours; then
            rm -f "$DESKTOP_FILE" "$ICONS/256x256/apps/alto.png" "$ICONS/512x512/apps/alto.png"
            refresh_desktop
        fi
        [ -n "$OPT" ] && rm -rf "$OPT"
        echo "Removed Alto from $PREFIX and from the application menu."
    fi
    if [ "${2:-}" = "--purge" ]; then
        echo "Deleting your practice history and settings:"
        for path in "$DATA/Alto" "$CONFIG/alto"; do
            echo "  $path"
            rm -rf "$path"
        done
    else
        echo "Your practice history ($DATA/Alto) and settings ($CONFIG/alto) were kept. Add --purge to delete them too."
    fi
    ;;
*)
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
