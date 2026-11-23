# PyInstaller recipe for Alto, used on Linux and Windows: `pyinstaller packaging/alto.spec`.
#
# It makes a folder, dist/alto, with the program `alto` (`alto.exe` on Windows) beside the Python, Qt and Alto files it needs. The
# folder can be copied anywhere. scripts/build-linux.sh builds it and wraps it in the Linux download.
#
# What goes in beyond what PyInstaller finds by itself:
#   - the files of the alto package that are not Python: the fonts, the recordings, the icons and the stylesheets in alto/assets;
#   - alto's package metadata, so that importlib.metadata (and so `alto --version`, a backup's version and the update check) works;
#   - PyNaCl, which checks the signature of an update: it loads a compiled helper (`_cffi_backend`) by a name that PyInstaller cannot
#     see from the imports, so without this the program does not start at all. `alto --self-test` and the build catch it if it breaks.
#
# ALTO_ICON, if set, names the icon of the program: a .ico on Windows. It is not set on Linux, where the menu entry names the icon.
#
# On Windows, Microsoft's Visual C++ runtime (vcruntime140.dll, msvcp140.dll and the like) is left out: the program uses
# the copy installed on Windows, and the installer makes sure it is there, installing it from Microsoft if need be
# (packaging/windows/alto.iss). ALTO_RUNTIME_FILE, if set, names a file in which the build writes what the
# installer must check: the names of the runtime files left out, and the newest version among them, which the system's
# copies must at least match.
import os
import re
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

if sys.platform == "win32":
    import pefile  # PyInstaller's own dependency on Windows, used to read the runtime's version

a = Analysis(
    ["launcher.py"],
    datas=collect_data_files("alto") + copy_metadata("alto") + copy_metadata("fsrs"),
    hiddenimports=["_cffi_backend", *collect_submodules("nacl")],
    excludes=["tkinter", "pytest", "numpy"],  # numpy is for the tests only; Alto does not use it
)
# Qt's hooks collect optional plugins and their native libraries. Alto draws its own keyboard
# and plays local PCM WAVs with QSoundEffect, which uses the platform audio output.
def unused_qt_component(destination):
    name = Path(destination).name.lower()
    return (
        "virtualkeyboard" in destination.lower()
        or "ffmpeg" in name
        or name in {"libqpdf.so", "qpdf.dll"}
        or name.startswith(("libqt6pdf.", "qt6pdf."))
        or re.fullmatch(r"(?:lib)?(?:avcodec|avformat|avutil|swresample|swscale)(?:-\d+\.dll|\.so(?:\.\d+)*)", name)
    )


a.binaries = [entry for entry in a.binaries if not unused_qt_component(entry[0])]
a.datas = [entry for entry in a.datas if not unused_qt_component(entry[0])]

# Microsoft's C and C++ runtime: the Visual C++ runtime, and the Universal C runtime that Windows 10 and later include.
MICROSOFT_RUNTIME = re.compile(
    r"(?:vcruntime\d+(?:_\d+)?|msvcp\d+(?:_[a-z0-9_]+)?(?:-[0-9a-f]+)?|concrt\d+|vccorlib\d+|vcamp\d+|vcomp\d+"
    r"|ucrtbase|api-ms-win-.+)\.dll",
    re.IGNORECASE,
)
UNIVERSAL_RUNTIME = re.compile(r"ucrtbase|api-ms-win-.+", re.IGNORECASE)  # part of Windows itself
# The files Microsoft's Visual C++ Redistributable installs, so the only ones the installer can make sure of.
REDISTRIBUTABLE = re.compile(r"(?:vcruntime140(?:_1)?|msvcp140(?:_1|_2|_atomic_wait|_codecvt_ids)?|concrt140|vcomp140)\.dll")


def microsoft_runtime(destination):
    return bool(MICROSOFT_RUNTIME.fullmatch(Path(destination).name))


def file_version(path):
    pe = pefile.PE(path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
    info = pe.VS_FIXEDFILEINFO[0]
    return (info.FileVersionMS >> 16, info.FileVersionMS & 0xFFFF, info.FileVersionLS >> 16, info.FileVersionLS & 0xFFFF)


if sys.platform == "win32":
    left_out = [entry for entry in a.binaries if microsoft_runtime(entry[0])]
    a.binaries = [entry for entry in a.binaries if not microsoft_runtime(entry[0])]
    visual_cpp = [
        (Path(name).name.lower(), source) for name, source, _kind in left_out if not UNIVERSAL_RUNTIME.match(Path(name).name)
    ]
    needed = sorted({name for name, _source in visual_cpp})
    if not needed:
        raise SystemExit("No Visual C++ runtime files were found to leave out, but Python and Qt bring some: check the build.")
    unexpected = [name for name in needed if not REDISTRIBUTABLE.fullmatch(name)]
    if unexpected:
        raise SystemExit(f"Microsoft runtime files that its Visual C++ Redistributable may not install: {unexpected}")
    newest = max(file_version(source) for _name, source in visual_cpp)
    if os.environ.get("ALTO_RUNTIME_FILE"):
        Path(os.environ["ALTO_RUNTIME_FILE"]).write_text(
            f"version={'.'.join(map(str, newest))}\nfiles={';'.join(needed)}\n",
            encoding="ascii",
        )
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="alto",
    console=False,  # a window, not a terminal: there is no console to print to on Windows
    icon=os.environ.get("ALTO_ICON") or None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="alto",
)

# Check the finished bundle, including native libraries and symlinks created during collection.
for path in Path(coll.name).rglob("*"):
    if unused_qt_component(str(path.relative_to(coll.name))):
        raise SystemExit(f"Unexpected optional Qt component in the desktop package: {path}")
    if microsoft_runtime(path.name):
        raise SystemExit(f"Microsoft's runtime must not be in the desktop package: {path}")
    if path.name == "numpy" and path.is_dir():
        raise SystemExit(f"numpy must not be in the desktop package: {path}")
