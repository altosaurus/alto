#!/bin/sh
# Build and smoke-test an Apple Silicon app. A Developer ID also produces a signed DMG.
set -eu

if [ "$(uname -s)-$(uname -m)" != Darwin-arm64 ]; then
    echo "Run this build on an Apple Silicon Mac." >&2
    exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$ROOT"
"${PYTHON:-python3}" "$ROOT/scripts/build_environment.py" "$ROOT" "$WORK/venv" "$ROOT/dist/macos-packages.json"
PYTHON="$WORK/venv/bin/python"
VERSION="$("$PYTHON" -c 'from importlib.metadata import version; print(version("alto"))')"
# Resolve distribution metadata from the installed wheel, outside the source checkout.
cd "$WORK"
export ALTO_QT_SOURCES="$WORK/qt-sources"
"$PYTHON" -m PyInstaller --clean --noconfirm --log-level WARN \
    --distpath "$WORK/dist" --workpath "$WORK/build" "$ROOT/packaging/alto.spec"

# ditto preserves the symlinks and executable permissions of the app and Qt frameworks.
NAME="alto-$VERSION-macos-arm64-test"
ditto -c -k --keepParent "$WORK/dist/Alto.app" "$WORK/$NAME.zip"
ditto -x -k "$WORK/$NAME.zip" "$WORK/unpacked"
APP="$WORK/unpacked/Alto.app"
EXE="$APP/Contents/MacOS/alto"
"$PYTHON" "$ROOT/packaging/dependency_licenses.py" verify "$APP/Contents/Resources"
"$PYTHON" "$ROOT/packaging/macos/check_bundle.py" "$APP" "$ALTO_QT_SOURCES"
lipo "$EXE" -verify_arch arm64
codesign --verify --deep --strict "$APP"
[ "$("$EXE" --version)" = "Alto $VERSION" ]
"$EXE" --self-test

# Launch with the native Qt platform and an empty profile on the runner.
ALTO_HOME="$WORK/profile" "$PYTHON" - "$EXE" <<'PY'
import subprocess
import sys

try:
    result = subprocess.run([sys.argv[1]], timeout=8)
except subprocess.TimeoutExpired:
    print("Alto stayed open during the launch check.")
else:
    sys.exit(f"Alto exited early with status {result.returncode}")
PY

sh "$ROOT/packaging/macos/check-replacement.sh" "$APP" "$WORK" "$PYTHON"
mkdir -p "$ROOT/dist/qt-sources"
cp "$ALTO_QT_SOURCES/"*.tar.xz "$ROOT/dist/qt-sources/"
if [ -n "${ALTO_MACOS_SIGN_IDENTITY:-}" ]; then
    STAGE="$WORK/disk-image"
    mkdir -p "$STAGE"
    mv "$APP" "$STAGE/Alto.app"
    ln -s /Applications "$STAGE/Applications"
    DMG="alto-$VERSION-macos-arm64.dmg"
    hdiutil create -volname Alto -srcfolder "$STAGE" -fs HFS+ -format UDZO "$WORK/$DMG"
    codesign --sign "$ALTO_MACOS_SIGN_IDENTITY" --timestamp "$WORK/$DMG"
    codesign --verify --strict "$WORK/$DMG"
    mv "$WORK/$DMG" "$ROOT/dist/"
    echo "Wrote dist/$DMG"
    exit 0
fi
mv "$WORK/$NAME.zip" "$ROOT/dist/"
echo "Wrote dist/$NAME.zip"
