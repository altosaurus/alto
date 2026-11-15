# PyInstaller recipe for Alto, used on Linux and Windows: `pyinstaller packaging/alto.spec`.
#
# It makes a folder, dist/alto, with the program `alto` (`alto.exe` on Windows) beside the Python, Qt and Alto files it needs. The
# folder can be copied anywhere. scripts/build-linux.sh builds it and wraps it in the Linux download.
#
# What goes in beyond what PyInstaller finds by itself:
#   - the files of the alto package that are not Python: the fonts, the recordings, the icons and the stylesheets in alto/assets;
#   - alto's package metadata, so that importlib.metadata (and so `alto --version`, a backup's version and the update check) works.
#
# ALTO_ICON, if set, names the icon of the program: a .ico on Windows. It is not set on Linux, where the menu entry names the icon.
import os

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

a = Analysis(
    ["launcher.py"],
    datas=collect_data_files("alto") + copy_metadata("alto"),
    excludes=["tkinter", "pytest"],
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
