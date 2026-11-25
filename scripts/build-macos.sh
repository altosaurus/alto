#!/bin/sh
# Build and smoke-test an Apple Silicon preview, with a local ad-hoc signature.
set -eu

if [ "$(uname -s)-$(uname -m)" != Darwin-arm64 ]; then
    echo "Run this build on an Apple Silicon Mac." >&2
    exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$ROOT"
"${PYTHON:-python3}" -m venv "$WORK/venv"
PYTHON="$WORK/venv/bin/python"
# Pillow converts Alto's existing PNG icon to the macOS icon format at build time.
"$PYTHON" -m pip install --quiet '.[package]' pillow
VERSION="$("$PYTHON" -c 'from importlib.metadata import version; print(version("alto"))')"
"$PYTHON" -m PyInstaller --clean --noconfirm --log-level WARN \
    --distpath "$WORK/dist" --workpath "$WORK/build" packaging/alto.spec

# ditto preserves the symlinks and executable permissions of the app and Qt frameworks.
NAME="alto-$VERSION-macos-arm64-test"
ditto -c -k --keepParent "$WORK/dist/Alto.app" "$WORK/$NAME.zip"
ditto -x -k "$WORK/$NAME.zip" "$WORK/unpacked"
APP="$WORK/unpacked/Alto.app"
EXE="$APP/Contents/MacOS/alto"
lipo -verify_arch arm64 "$EXE"
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

mkdir -p "$ROOT/dist"
mv "$WORK/$NAME.zip" "$ROOT/dist/"
echo "Wrote dist/$NAME.zip"
