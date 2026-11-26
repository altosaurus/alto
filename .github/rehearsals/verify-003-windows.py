"""Exercise the released updater on a fresh Windows runner."""
# ruff: noqa: INP001 -- standalone runner script

import hashlib
import os
import shutil
import subprocess
import time
import winreg
from pathlib import Path

import psutil
import win32con
import win32gui
import win32process

from alto import selfupdate, updates

assert (
    Path(selfupdate.__file__)
    .resolve()
    .is_relative_to(Path.cwd() / "old-source")
)
work = Path(os.environ["RUNNER_TEMP"])
target = work / "installed-alto"
app = target / "alto.exe"
old = next(Path("old").absolute().glob("*.exe"))
new = next(Path("candidate").absolute().glob("*.exe"))
os.environ.update(QT_QPA_PLATFORM="offscreen", ALTO_HOME=str(work / "profile"))


def sha(path: Path) -> str:
    """
    Read one file.

    Returns
    -------
    str
        SHA-256 digest.
    """
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def manifest(folder: Path) -> dict[Path, str]:
    """
    Inventory the installed files.

    Returns
    -------
    dict
        Relative paths and SHA-256 digests.
    """
    return {
        p.relative_to(folder): sha(p) for p in folder.rglob("*") if p.is_file()
    }


def accepted() -> str | None:
    """
    Read the installer registry entry.

    Returns
    -------
    str or None
        Accepted terms version.
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Alto Installer",
        ) as key:
            return winreg.QueryValueEx(key, "AcceptedTerms")[0]
    except FileNotFoundError:
        return None


def click_terms(choice: int) -> None:
    """
    Click the requested button in the Microsoft terms prompt.

    Raises
    ------
    TimeoutError
        If the expected prompt never opens.
    """
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        windows = []
        win32gui.EnumWindows(lambda w, result: result.append(w), windows)
        for window in windows:
            if (
                not win32gui.IsWindowVisible(window)
                or win32gui.GetClassName(window) != "#32770"
            ):
                continue
            children = []
            win32gui.EnumChildWindows(
                window,
                lambda w, result: result.append(w),
                children,
            )
            text = " ".join(win32gui.GetWindowText(w) for w in children)
            if "terms for the Microsoft code" not in text:
                continue
            pid = win32process.GetWindowThreadProcessId(window)[1]
            assert (
                psutil.Process(pid).name().lower().endswith((".tmp", ".exe"))
            )
            selected = win32gui.GetDlgItem(window, choice)
            assert (
                selected
                and win32gui.GetDlgItem(window, 6)
                and win32gui.GetDlgItem(window, 7)
            )
            win32gui.PostMessage(selected, win32con.BM_CLICK, 0, 0)
            return
        time.sleep(0.25)
    raise TimeoutError("Microsoft consent prompt did not appear")


def update(running: psutil.Process, *, choice: int) -> psutil.Process:
    """
    Run the 0.0.2 handoff and wait for Alto to reopen.

    Returns
    -------
    psutil.Process
        Relaunched application.

    Raises
    ------
    TimeoutError
        If the updater never reopens Alto.
    """
    selfupdate.start_handoff(
        selfupdate.Prepared(work, installer=new, root=None),
        target=selfupdate.Target("windows", folder=target, prefix=None),
        pid=running.pid,
    )
    running.terminate()
    running.wait(timeout=15)
    click_terms(choice)
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        for process in psutil.process_iter(["exe"]):
            if process.info["exe"] and Path(process.info["exe"]) == app:
                time.sleep(1)
                assert process.is_running()
                return process
        time.sleep(0.3)
    raise TimeoutError("Alto did not reopen after the consent choice")


for installer in (old, new):
    sums = installer.parent / "SHA256SUMS"
    if sums.exists():
        data = sums.read_bytes()
        assert updates.verify_signature(
            data,
            signature=(sums.parent / "SHA256SUMS.sig").read_text(),
            keys=updates.UPDATE_PUBLIC_KEYS,
        )
        assert (
            f"{sha(installer)}  {installer.name}" in data.decode().splitlines()
        )
    print(installer.name, sha(installer))

subprocess.run(
    [
        old,
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/CURRENTUSER",
        f"/DIR={target}",
    ],
    check=True,
    timeout=150,
)
assert (
    target / "_internal/alto-0.0.2.dist-info"
).is_dir() and accepted() is None
subprocess.run([app, "--self-test"], check=True, timeout=30)
running = psutil.Popen([str(app)])
time.sleep(4)
before = manifest(target)
running = update(running, choice=7)
assert accepted() is None and before == manifest(target)
subprocess.run([app, "--self-test"], check=True, timeout=30)
print(
    "Decline passed. Files and terms record preserved. Alto 0.0.2 reopened.",
)
running = update(running, choice=6)
assert (
    accepted() == "1" and (target / "_internal/alto-0.0.3.dist-info").is_dir()
)
subprocess.run([app, "--self-test"], check=True, timeout=30)
print(
    "Accept passed. Alto 0.0.3 reopened; self-test and terms record verified.",
)
running.terminate()
running.wait(timeout=15)

copy = work / "replacement-test"
shutil.copytree(target, copy)
pyside = copy / "_internal/PySide6"
core = pyside / "Qt6Core.dll"
data = core.read_bytes()
version = b"\x006.12.0\x00"
assert data.count(version) == 1
core.write_bytes(data.replace(version, b"\x006.12.1\x00"))
marker = work / "loaded-version.txt"
with (pyside / "__init__.py").open("a", encoding="utf-8") as stream:
    stream.write(
        "\nfrom pathlib import Path\nfrom PySide6.QtCore import qVersion\n"
        f"Path({str(marker)!r}).write_text(qVersion())\n",
    )
subprocess.run([copy / "alto.exe", "--self-test"], check=True, timeout=30)
assert marker.read_text() == "6.12.1"
print(
    "Replacement passed. Modified Qt and PySide6 loaded; self-test passed.",
)
