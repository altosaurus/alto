#!/bin/sh
# Install, update or remove Alto as a program on this computer (Linux).
#
#   sh scripts/alto-install.sh install            install from GitHub and add Alto to the application menu
#   sh scripts/alto-install.sh update             fetch the newest version from GitHub
#   sh scripts/alto-install.sh uninstall          remove the program, its menu entry and its icon; keep your data
#   sh scripts/alto-install.sh uninstall --purge  also delete your practice history and settings
#
# The program lives in its own environment under uv's tool folder, apart from any checkout, so working on Alto in a clone never
# changes the installed copy. Set ALTO_SOURCE to install from somewhere else (a fork, a branch: git+https://...@branch, a path).
set -eu

SOURCE="${ALTO_SOURCE:-git+https://github.com/altosaurus/alto.git}"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
DESKTOP_FILE="$DATA/applications/alto.desktop"
ICONS="$DATA/icons/hicolor"

need_uv() {
    command -v uv >/dev/null 2>&1 || {
        echo "uv is needed (https://docs.astral.sh/uv/). Install it first, then run this again." >&2
        exit 1
    }
}

refresh_desktop() {
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA/applications" || true
    command -v gtk-update-icon-cache >/dev/null 2>&1 && [ -f "$ICONS/icon-theme.cache" ] && gtk-update-icon-cache -q -f -t "$ICONS" || true
}

# The menu entry and the icon are not something uv knows about, so they are written here and removed by `uninstall`. The icon is
# a PNG at two sizes that the entry names, and the desktop matches the window to the entry by the app ID that Alto announces.
add_menu_entry() {
    bin="$(uv tool dir --bin)/alto"
    assets="$("$(uv tool dir)/alto/bin/python" -c 'import alto, pathlib; print(pathlib.Path(alto.__file__).parent / "assets")')"
    mkdir -p "$DATA/applications" "$ICONS/256x256/apps" "$ICONS/512x512/apps"
    cp "$assets/icon-256.png" "$ICONS/256x256/apps/alto.png"
    cp "$assets/icon.png" "$ICONS/512x512/apps/alto.png"
    cat >"$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Alto
Comment=Music theory trainer
Exec=$bin
Icon=alto
Terminal=false
Categories=Education;Music;
EOF
    refresh_desktop
}

remove_menu_entry() {
    rm -f "$DESKTOP_FILE" "$ICONS/256x256/apps/alto.png" "$ICONS/512x512/apps/alto.png"
    refresh_desktop
}

case "${1:-}" in
install)
    need_uv
    uv tool install --force "$SOURCE"
    add_menu_entry
    echo "Installed. Start Alto from the application menu, or with: $(uv tool dir --bin)/alto"
    ;;
update)
    need_uv
    uv tool upgrade alto
    add_menu_entry # the icon or the path may have changed
    echo "Up to date."
    ;;
uninstall)
    need_uv
    uv tool uninstall alto || echo "The program was not installed."
    remove_menu_entry
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
    sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
