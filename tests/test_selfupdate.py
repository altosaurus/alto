"""
Tests for a packaged copy of Alto replacing itself: which copies can, the download, the checks, the unpacking, the hand-over.

A local web server plays GitHub, the packages are built on the spot, and the keys are made for each test. The Linux hand-over runs
for real, with `sh` and the real `install.sh`, in a scratch home. Nothing here goes online.
"""

from __future__ import annotations

import base64
import hashlib
import io
import os
import subprocess
import tarfile
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from alto import (
    selfupdate,
    updates,
)
from alto.selfupdate import (
    Prepared,
    Target,
    UpdateCanceled,
    UpdateError,
)
from releases import (
    VERSION,
    Keys,
    Server,
    linux_package,
    publish,
)

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Iterator,
    )

NAME = f"alto-{VERSION}-linux-x86_64.tar.gz"
WINDOWS_NAME = f"alto-{VERSION}-windows-x64-setup.exe"


@pytest.fixture
def keys() -> Keys:
    """
    Make a key pair for one test.

    Returns
    -------
    Keys
        The pair.
    """
    return Keys()


@pytest.fixture
def server() -> Iterator[Server]:
    """
    Serve files on this computer for the length of one test.

    Yields
    ------
    Server
        The server.
    """
    with Server() as running:
        yield running


def nothing(done: int, total: int) -> None:  # noqa: PLR0917  (a progress callback, called with two numbers)
    """
    Take a note of progress and ignore it.

    Parameters
    ----------
    done : int
        The bytes received so far.
    total : int
        The total.
    """
    del done, total


def never() -> bool:
    """
    Say that nobody has canceled.

    Returns
    -------
    bool
        False.
    """
    return False


def fetch(
    server: Server,
    *,
    path: str,
    destination: Path,
    max_bytes: int = 10_000_000,
    canceled: Callable[[], bool] = never,
) -> str:
    """
    Download a file of the server with the real function.

    Parameters
    ----------
    server : Server
        The server.
    path : str
        What to fetch, such as "/releases/download/v9.9.9/file".
    destination : Path
        Where to write it.
    max_bytes : int, default 10_000_000
        The most to accept.
    canceled : Callable
        Says whether to stop.

    Returns
    -------
    str
        The hash of what was written.
    """
    return selfupdate.download(
        f"http://127.0.0.1:{server.port}{path}",
        destination=destination,
        allowed=server.base,
        max_bytes=max_bytes,
        progress=nothing,
        canceled=canceled,
    )


# -- which copies can replace themselves ----------------------------------------------------------------------------


def install_layout(prefix: Path) -> Path:
    """
    Make what `install.sh` makes: the program in `opt/alto` and a link to it in `bin`.

    Parameters
    ----------
    prefix : Path
        The folder to make it in.

    Returns
    -------
    Path
        The program.
    """
    program = prefix / "opt" / "alto" / "alto"
    program.parent.mkdir(parents=True)
    program.write_text("#!/bin/sh\n")
    (prefix / "bin").mkdir()
    (prefix / "bin" / "alto").symlink_to(program)
    return program


def test_a_copy_installed_by_the_linux_script_can_replace_itself(tmp_path: Path) -> None:
    """
    Check that a program in `<prefix>/opt/alto` with a link in `<prefix>/bin` is a target, with its prefix.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    program = install_layout(tmp_path)
    assert selfupdate.self_update_target(executable=program, system="Linux") == Target(
        "linux",
        folder=program.parent,
        prefix=tmp_path,
    )


def test_a_linux_copy_that_was_only_unpacked_or_is_linked_from_elsewhere_cannot(tmp_path: Path) -> None:
    """
    Check that a folder someone ran from, a program in the wrong place, and a link that points elsewhere are not targets.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    unpacked = tmp_path / "downloads" / "alto-0.1.0" / "alto" / "alto"
    unpacked.parent.mkdir(parents=True)
    unpacked.write_text("#!/bin/sh\n")
    assert selfupdate.self_update_target(executable=unpacked, system="linux") is None
    program = install_layout(tmp_path / "home")
    (tmp_path / "home" / "bin" / "alto").unlink()
    (tmp_path / "home" / "bin" / "alto").symlink_to(unpacked)  # the command is another copy
    assert selfupdate.self_update_target(executable=program, system="linux") is None
    (tmp_path / "home" / "bin" / "alto").unlink()  # and with no command at all
    assert selfupdate.self_update_target(executable=program, system="linux") is None
    assert selfupdate.self_update_target(executable=tmp_path / "alto", system="linux") is None


def test_a_copy_made_by_the_windows_installer_can_replace_itself_and_nothing_else_can(tmp_path: Path) -> None:
    """
    Check that on Windows the uninstaller beside the program is what marks it as installed, and that other systems never are.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    program = tmp_path / "Alto" / "alto.exe"
    program.parent.mkdir()
    program.write_text("exe")
    assert selfupdate.self_update_target(executable=program, system="Windows") is None  # unzipped, not installed
    (program.parent / "unins000.exe").write_text("uninstaller")
    assert selfupdate.self_update_target(executable=program, system="Windows") == Target(
        "windows",
        folder=program.parent,
        prefix=None,
    )
    assert selfupdate.self_update_target(executable=program.parent / "python.exe", system="Windows") is None
    assert selfupdate.self_update_target(executable=program, system="Darwin") is None


# -- downloading ----------------------------------------------------------------------------------------------------


def test_a_download_is_written_hashed_and_reports_its_progress(server: Server, tmp_path: Path) -> None:
    """
    Check that the file arrives whole, that its hash is returned, that progress counts up to the total, and that no part is left.

    Parameters
    ----------
    server : Server
        The local server.
    tmp_path : Path
        A new folder.
    """
    data = os.urandom(300_000)
    server.files["/releases/download/v1/file"] = data
    seen: list[tuple[int, int]] = []
    result = selfupdate.download(
        f"{server.base}v1/file",
        destination=tmp_path / "file",
        allowed=server.base,
        max_bytes=1_000_000,
        progress=lambda done, total: seen.append((done, total)),
        canceled=never,
    )
    assert (tmp_path / "file").read_bytes() == data and result == hashlib.sha256(data).hexdigest()
    assert seen[-1] == (len(data), len(data)) and [done for done, _ in seen] == sorted(done for done, _ in seen)
    assert not list(tmp_path.glob("*.part"))


def test_a_download_from_an_address_that_is_not_the_releases_is_refused_before_any_request(
    server: Server,
    tmp_path: Path,
) -> None:
    """
    Check that a file named at some other address is never fetched.

    Parameters
    ----------
    server : Server
        The local server.
    tmp_path : Path
        A new folder.
    """
    with pytest.raises(UpdateError, match="does not download updates from"):
        selfupdate.download(
            "https://example.org/alto.tar.gz",
            destination=tmp_path / "x",
            allowed=server.base,
            max_bytes=10,
            progress=nothing,
            canceled=never,
        )
    assert server.requests == [] and not (tmp_path / "x").exists()


def test_a_download_that_fails_too_large_or_is_canceled_leaves_nothing_behind(server: Server, tmp_path: Path) -> None:
    """
    Check the three ways a download can end badly: no such file, a file over the size allowed, and a cancel.

    Parameters
    ----------
    server : Server
        The local server.
    tmp_path : Path
        A new folder.
    """
    server.files["/releases/download/v1/big"] = b"x" * 5000
    with pytest.raises(UpdateError, match="download failed"):
        fetch(server, path="/releases/download/v1/missing", destination=tmp_path / "a")
    with pytest.raises(UpdateError, match="larger than expected"):
        fetch(server, path="/releases/download/v1/big", destination=tmp_path / "b", max_bytes=1000)
    with pytest.raises(UpdateCanceled):
        fetch(server, path="/releases/download/v1/big", destination=tmp_path / "c", canceled=lambda: True)
    assert not list(tmp_path.iterdir())


def test_a_download_that_is_redirected_somewhere_not_secure_is_stopped(server: Server, tmp_path: Path) -> None:
    """
    Check that GitHub's redirect to its own address is followed, but a redirect to a plain http address elsewhere is not.

    Parameters
    ----------
    server : Server
        The local server.
    tmp_path : Path
        A new folder.
    """
    with Server() as elsewhere:
        elsewhere.files["/payload"] = b"evil"
        server.redirects["/releases/download/v1/file"] = f"http://127.0.0.1:{elsewhere.port}/payload"
        with pytest.raises(UpdateError, match="not secure"):
            fetch(server, path="/releases/download/v1/file", destination=tmp_path / "file")
    assert not list(tmp_path.iterdir())


# -- unpacking ------------------------------------------------------------------------------------------------------


def tar_of(members: dict[str, bytes], *, links: dict[str, str] | None = None) -> bytes:
    """
    Build a `.tar.gz` with exactly these members, as given.

    Parameters
    ----------
    members : dict of str to bytes
        File names, which may be hostile, and what is in them.
    links : dict of str to str or None, default None
        Symbolic links, by name, and where they point. Keyword-only.

    Returns
    -------
    bytes
        The archive.
    """
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o755
            tar.addfile(info, io.BytesIO(data))
        for name, target in (links or {}).items():
            info = tarfile.TarInfo(name)
            # noinspection PyTypeChecker
            info.type = tarfile.SYMTYPE
            info.linkname = target
            tar.addfile(info)
    return buffer.getvalue()


def test_the_linux_download_unpacks_to_one_folder_that_holds_the_installer_and_the_program(tmp_path: Path) -> None:
    """
    Check that a good download unpacks, keeps the program executable, and gives back its one folder.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    archive = tmp_path / "a.tar.gz"
    archive.write_bytes(linux_package())
    root = selfupdate.extract_tarball(archive, destination=tmp_path / "out")
    assert root.name == f"alto-{VERSION}-linux-x86_64" and (root / "install.sh").is_file()
    assert os.access(root / "alto" / "alto", os.X_OK)


@pytest.mark.parametrize(
    ("members", "links"),
    [
        ({"../escaped": b"x", "ok/install.sh": b"x", "ok/alto/alto": b"x"}, None),
        ({"/tmp/escaped-absolutely": b"x"}, None),
        ({"ok/install.sh": b"x", "ok/alto/alto": b"x"}, {"ok/link": "../../../etc/passwd"}),
        ({"ok/install.sh": b"x"}, None),
        ({"one/install.sh": b"x", "one/alto/alto": b"x", "two/readme": b"x"}, None),
    ],
)
def test_a_download_that_escapes_its_folder_or_is_not_a_package_is_refused(
    tmp_path: Path,
    members: dict[str, bytes],
    links: dict[str, str] | None,
) -> None:
    """
    Check that names that climb out, absolute names, links that leave, and archives with the wrong shape are all refused.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    members : dict of str to bytes
        The files in the archive.
    links : dict of str to str or None
        The links in the archive.
    """
    archive = tmp_path / "bad.tar.gz"
    archive.write_bytes(tar_of(members, links=links))
    with pytest.raises(UpdateError):
        selfupdate.extract_tarball(archive, destination=tmp_path / "out")
    assert not (tmp_path / "escaped").exists() and not Path("/tmp/escaped-absolutely").exists()


def test_a_file_that_is_not_an_archive_is_refused(tmp_path: Path) -> None:
    """
    Check that damaged data gives a message and not a crash.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    archive = tmp_path / "junk.tar.gz"
    archive.write_bytes(b"this is not a tarball")
    with pytest.raises(UpdateError, match="could not be unpacked"):
        selfupdate.extract_tarball(archive, destination=tmp_path / "out")


# -- getting and checking a whole update ----------------------------------------------------------------------------


def prepare(
    release: updates.Release,
    server: Server,
    keys: Keys,
    tmp_path: Path,
    *,
    system: str = "linux",
    machine: str = "x86_64",
    trusted: tuple[str, ...] | None = None,
) -> tuple[Prepared, list[str]]:
    """
    Run the whole preparation against the local server.

    Parameters
    ----------
    release : updates.Release
        The release.
    server : Server
        The local server.
    keys : Keys
        The keys the test trusts, unless `trusted` says others.
    tmp_path : Path
        A new folder to work in.
    system : str, default "linux"
        The system of the copy. Keyword-only.
    machine : str, default "x86_64"
        The processor. Keyword-only.
    trusted : tuple of str or None, default None
        The public keys to trust. Keyword-only.

    Returns
    -------
    tuple of Prepared and list of str
        The checked update and what was said while it was made.
    """
    said: list[str] = []
    work = tmp_path / "work"
    work.mkdir(parents=True)
    prepared = selfupdate.prepare_update(
        release,
        target=Target(system, folder=tmp_path / "app", prefix=tmp_path if system == "linux" else None),
        work=work,
        keys=(keys.public,) if trusted is None else trusted,
        machine=machine,
        base=server.base,
        status=said.append,
        progress=nothing,
        canceled=never,
    )
    return prepared, said


def test_a_signed_linux_release_is_downloaded_checked_and_unpacked(server: Server, keys: Keys, tmp_path: Path) -> None:
    """
    Check the whole path for Linux: the signature, the listed hash, the download and the unpacking, and what was said on the way.

    Parameters
    ----------
    server : Server
        The local server.
    keys : Keys
        The key pair of the test.
    tmp_path : Path
        A new folder.
    """
    release = publish(server, keys=keys, package=linux_package(), name=NAME)
    prepared, said = prepare(release, server, keys, tmp_path)
    assert prepared.installer is None and prepared.root is not None and (prepared.root / "install.sh").is_file()
    assert said == ["Checking the signature…", f"Downloading {NAME}…", "Checking the download…", "Unpacking…"]
    assert not (prepared.work / NAME).exists()  # the archive is removed once it is unpacked


def test_a_signed_windows_release_gives_the_installer_to_run(server: Server, keys: Keys, tmp_path: Path) -> None:
    """
    Check the Windows path: the installer is downloaded and checked, and handed back as the file to run.

    Parameters
    ----------
    server : Server
        The local server.
    keys : Keys
        The key pair of the test.
    tmp_path : Path
        A new folder.
    """
    release = publish(server, keys=keys, package=b"MZ pretend installer", name=WINDOWS_NAME)
    prepared, _ = prepare(release, server, keys, tmp_path, system="windows", machine="AMD64")
    assert prepared.root is None and prepared.installer == prepared.work / WINDOWS_NAME
    installer = prepared.installer
    assert installer is not None and installer.read_bytes() == b"MZ pretend installer"


@pytest.mark.parametrize(
    ("other_key", "wrong_hash", "leave_out", "message"),
    [
        (True, False, (), "signature of this update is not valid"),
        (False, True, (), "does not match the checksum that was signed"),
        (False, False, ("SHA256SUMS.sig",), "no signature"),
        (False, False, ("SHA256SUMS",), "no list of checksums"),
        (False, False, (NAME,), "no download"),
    ],
)
def test_an_update_that_does_not_check_out_is_refused_and_leaves_nothing_to_install(
    server: Server,
    keys: Keys,
    tmp_path: Path,
    other_key: bool,
    wrong_hash: bool,
    leave_out: tuple[str, ...],
    message: str,
) -> None:
    """
    Check each way a release can be wrong: signed by another key, a package that is not the one listed, and a missing file.

    Parameters
    ----------
    server : Server
        The local server.
    keys : Keys
        The key pair of the test.
    tmp_path : Path
        A new folder.
    other_key : bool
        Whether the list is signed with a key that is not trusted.
    wrong_hash : bool
        Whether the list holds the hash of some other file.
    leave_out : tuple of str
        The files the release does not have.
    message : str
        What the person should be told.
    """
    release = publish(
        server,
        keys=keys,
        package=linux_package(),
        name=NAME,
        sign_with=Keys() if other_key else None,
        sums_for=b"some other bytes" if wrong_hash else None,
        leave_out=leave_out,
    )
    with pytest.raises(UpdateError, match=message):
        prepare(release, server, keys, tmp_path)
    assert not any(path.suffix == ".part" or path.name == "unpacked" for path in (tmp_path / "work").iterdir())


def test_an_old_signed_list_cannot_pass_as_a_newer_release(server: Server, keys: Keys, tmp_path: Path) -> None:
    """
    Check that a list signed for 9.9.8, served as the files of 9.9.9, is refused because it does not name the 9.9.9 package.

    Parameters
    ----------
    server : Server
        The local server.
    keys : Keys
        The key pair of the test.
    tmp_path : Path
        A new folder.
    """
    old_name = "alto-9.9.8-linux-x86_64.tar.gz"
    old = publish(server, keys=keys, package=linux_package("9.9.8"), name=old_name, version="9.9.8")
    new_files = {
        NAME: server.files[f"/releases/download/v9.9.8/{old_name}"],
        updates.CHECKSUMS_NAME: server.files["/releases/download/v9.9.8/SHA256SUMS"],
        updates.SIGNATURE_NAME: server.files["/releases/download/v9.9.8/SHA256SUMS.sig"],
    }
    assets = []
    for file, data in new_files.items():
        server.files[f"/releases/download/v9.9.9/{file}"] = data
        assets.append(updates.Asset(file, url=f"{server.base}v9.9.9/{file}", size=len(data)))
    replay = updates.Release("9.9.9", tag="v9.9.9", url=old.url, assets=tuple(assets))
    with pytest.raises(UpdateError, match="does not name alto-9.9.9"):
        prepare(replay, server, keys, tmp_path)


def test_an_update_is_refused_with_no_key_a_foreign_key_or_a_computer_it_has_no_package_for(
    server: Server,
    keys: Keys,
    tmp_path: Path,
) -> None:
    """
    Check that no key at all, a key that did not sign it, and an unsupported processor are each refused.

    Parameters
    ----------
    server : Server
        The local server.
    keys : Keys
        The key pair of the test.
    tmp_path : Path
        A new folder.
    """
    release = publish(server, keys=keys, package=linux_package(), name=NAME)
    with pytest.raises(UpdateError, match="no key to check"):
        prepare(release, server, keys, tmp_path / "one", trusted=())
    with pytest.raises(UpdateError, match="signature of this update is not valid"):
        prepare(release, server, keys, tmp_path / "two", trusted=(Keys().public,))
    with pytest.raises(UpdateError, match="no download for this computer"):
        prepare(release, server, keys, tmp_path / "three", machine="aarch64")


def test_a_cancel_during_the_download_stops_it_with_nothing_left(server: Server, keys: Keys, tmp_path: Path) -> None:
    """
    Check that canceling once the package begins to download ends in a cancel, not an error, and leaves no part file.

    Parameters
    ----------
    server : Server
        The local server.
    keys : Keys
        The key pair of the test.
    tmp_path : Path
        A new folder.
    """
    release = publish(server, keys=keys, package=linux_package(), name=NAME)
    cancel = {"now": False}

    def said(text: str) -> None:
        """
        Cancel when the package starts to download.

        Parameters
        ----------
        text : str
            What is being done.
        """
        cancel["now"] = text.startswith("Downloading")

    work = tmp_path / "work"
    work.mkdir()
    with pytest.raises(UpdateCanceled):
        selfupdate.prepare_update(
            release,
            target=Target("linux", folder=tmp_path, prefix=tmp_path),
            work=work,
            keys=(keys.public,),
            machine="x86_64",
            base=server.base,
            status=said,
            progress=nothing,
            canceled=lambda: cancel["now"],
        )
    assert not list(work.glob("*.part")) and not (work / NAME).exists()


# -- handing over ---------------------------------------------------------------------------------------------------


def test_the_environment_given_to_the_installer_is_the_systems_and_not_the_bundles() -> None:
    """Check that PyInstaller's library path and start-up variables are undone, and the rest is passed on."""
    env = {
        "PATH": "/usr/bin",
        "LD_LIBRARY_PATH": "/opt/alto/_internal",
        "LD_LIBRARY_PATH_ORIG": "/usr/local/lib",
        "_PYI_APPLICATION_HOME_DIR": "/tmp/x",
        "XDG_ACTIVATION_TOKEN": "token",
        "DESKTOP_STARTUP_ID": "token",
    }
    cleaned = selfupdate.clean_environment(env)
    assert cleaned == {"PATH": "/usr/bin", "LD_LIBRARY_PATH": "/usr/local/lib", "PYINSTALLER_RESET_ENVIRONMENT": "1"}
    assert env["LD_LIBRARY_PATH"] == "/opt/alto/_internal"  # the original is not changed


def decoded(command: list[str]) -> str:
    """
    Read the PowerShell script that a command carries, which is base64 of UTF-16 after `-EncodedCommand`.

    Parameters
    ----------
    command : list of str
        The command.

    Returns
    -------
    str
        The script.
    """
    return base64.b64decode(command[-1]).decode("utf-16-le")


def test_on_windows_a_step_waits_for_alto_to_end_then_runs_the_installer_and_restarts_the_old_alto_if_it_fails() -> None:
    """Check the script handed over: wait for the process, run the installer with its arguments, and the way back if it fails."""
    command = selfupdate.windows_handoff_command(
        Path("C:/Temp/alto-update-x/setup.exe"),
        pid=4242,
        alto=Path("C:/Users/me/Alto/alto.exe"),
    )
    assert command[:-1] == ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-EncodedCommand"]
    script = decoded(command).splitlines()
    assert script[1] == "try { Wait-Process -Id 4242 -Timeout 60 -ErrorAction Stop } catch { }"
    assert (
        script[2].startswith("$run = Start-Process -FilePath 'C:")
        and script[2].endswith("-PassThru")
        and "-Wait" not in script[2]
    )
    for argument in ("/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS", "/RELAUNCH=1"):
        assert f"'{argument}'" in script[2]
    assert script[3] == "if ($null -ne $run) { $run.WaitForExit() }"  # the installer only, not the Alto it opens again
    assert "$run.ExitCode -ne 0" in script[4] and "alto.exe" in script[4] and "Start-Process" in script[4]


def test_a_path_with_a_quote_in_it_cannot_end_the_powershell_string_early() -> None:
    """Check that a single quote in a path, as an apostrophe in a user's name, is doubled and so stays inside its string."""
    command = selfupdate.windows_handoff_command(
        Path("C:/Users/O'Brien/AppData/setup.exe"),
        pid=1,
        alto=Path("C:/O'Brien/alto.exe"),
    )
    script = decoded(command)
    assert script.count("O''Brien") == 2 and "O'Brien" not in script


def test_on_windows_alto_starts_that_step_hidden_and_detached_and_does_not_start_the_installer_itself(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that with PowerShell available, what is started is the waiting step, with the cleaned environment.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    monkeypatch : pytest.MonkeyPatch
        Replaces the starting of a program and the search for PowerShell.
    """
    started: list[tuple[list[str], dict[str, object]]] = []
    monkeypatch.setattr(selfupdate.subprocess, "Popen", lambda argv, **kwargs: started.append((argv, kwargs)))
    monkeypatch.setattr(selfupdate.shutil, "which", lambda name, path=None: "C:/Windows/powershell.exe")
    installer = tmp_path / WINDOWS_NAME
    selfupdate.start_handoff(
        Prepared(tmp_path, installer=installer, root=None),
        target=Target("windows", folder=tmp_path, prefix=None),
        pid=777,
        environ={"PATH": "x"},
    )
    command, options = started[0]
    script = decoded(command)
    assert command[0] == "powershell.exe" and "Wait-Process -Id 777" in script and str(installer) in script
    assert str(tmp_path / "alto.exe") in script  # the old one, for if the installer fails
    assert options["env"] == {"PATH": "x", "PYINSTALLER_RESET_ENVIRONMENT": "1"}
    with pytest.raises(UpdateError, match="no installer"):
        selfupdate.start_handoff(
            Prepared(tmp_path, installer=None, root=None),
            target=Target("windows", folder=tmp_path, prefix=None),
        )


def test_on_windows_without_powershell_the_installer_is_started_at_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check the fallback: with nothing to wait with, the installer itself is started with its arguments.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    monkeypatch : pytest.MonkeyPatch
        Replaces the starting of a program and the search for PowerShell.
    """
    started: list[list[str]] = []
    monkeypatch.setattr(selfupdate.subprocess, "Popen", lambda argv, **kwargs: started.append(argv))
    monkeypatch.setattr(selfupdate.shutil, "which", lambda name, path=None: None)
    installer = tmp_path / WINDOWS_NAME
    selfupdate.start_handoff(
        Prepared(tmp_path, installer=installer, root=None),
        target=Target("windows", folder=tmp_path, prefix=None),
        environ={"PATH": "x"},
    )
    assert started == [[str(installer), "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS", "/RELAUNCH=1"]]


class Home:
    """
    A scratch home with an installed copy of a stand-in Alto, and a newer download unpacked and waiting.

    Attributes
    ----------
    prefix : Path
        Where Alto is installed.
    log : Path
        The file the helper writes to.
    marker : Path
        A file the stand-in program creates when it is started, so that a restart can be seen.
    env : dict of str to str
        The environment to run in.
    work : Path
        The temporary folder of the update, holding the unpacked download.
    root : Path
        The unpacked download.
    """

    def __init__(
        self,
        tmp_path: Path,
        *,
        old: str,
        new: str,
    ) -> None:
        """
        Install the old copy with the real `install.sh`, and unpack the new download.

        Parameters
        ----------
        tmp_path : Path
            A new folder.
        old : str
            What the installed program says its version is. Keyword-only.
        new : str
            What the downloaded program says. Keyword-only.
        """
        self.prefix = tmp_path / "prefix"
        self.log = tmp_path / "update.log"
        self.marker = tmp_path / "started"
        home = tmp_path / "home"
        home.mkdir()
        self.env = {
            "PATH": os.environ["PATH"],
            "HOME": str(home),
            "XDG_DATA_HOME": str(home / "data"),
            "XDG_CONFIG_HOME": str(home / "config"),
            "ALTO_TEST_MARK": str(self.marker),
        }

        def program(version: str) -> bytes:
            """
            Write a stand-in program that says its version, and otherwise marks that it was started.

            Parameters
            ----------
            version : str
                The version it says.

            Returns
            -------
            bytes
                Its source.
            """
            lines = [
                "#!/bin/sh",
                f'if [ "$1" = "--version" ]; then echo "Alto {version}"; else echo "{version}" > "$ALTO_TEST_MARK"; fi',
            ]
            return ("\n".join(lines) + "\n").encode()

        first = tmp_path / "first.tar.gz"
        first.write_bytes(linux_package("1.0.0", program=program(old)))
        first_root = selfupdate.extract_tarball(first, destination=tmp_path / "first")
        done = subprocess.run(
            ["sh", str(first_root / "install.sh"), "install"],
            env={**self.env, "ALTO_PREFIX": str(self.prefix)},
            capture_output=True,
            text=True,
            check=False,
        )
        assert done.returncode == 0, done.stderr
        second = tmp_path / "second.tar.gz"
        second.write_bytes(linux_package("2.0.0", program=program(new)))
        self.work = tmp_path / "work"
        self.work.mkdir()
        self.root = selfupdate.extract_tarball(second, destination=self.work / "unpacked")
        self.target = Target("linux", folder=self.prefix / "opt" / "alto", prefix=self.prefix)

    def hand_over(self) -> None:
        """Start the helper, as Alto does, for a process that ends a moment later."""
        waiting = subprocess.Popen(["sleep", "0.3"])
        threading.Thread(target=waiting.wait, daemon=True).start()  # reaped as soon as it ends, as the system reaps Alto
        selfupdate.start_handoff(
            Prepared(self.work, installer=None, root=self.root),
            target=self.target,
            pid=waiting.pid,
            log=self.log,
            environ={**self.env, "LD_LIBRARY_PATH_ORIG": "", "LD_LIBRARY_PATH": "/bundle"},
        )

    def says(self) -> str:
        """
        Ask the installed program for its version.

        Returns
        -------
        str
            What `bin/alto --version` prints.
        """
        return subprocess.run(
            [str(self.prefix / "bin" / "alto"), "--version"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

    def wait_for_restart(self) -> None:
        """Wait, at most twenty seconds, for the helper to start the program again."""
        for _ in range(200):
            if self.marker.exists():
                return
            time.sleep(0.1)
        pytest.fail(f"Alto was not started again. The log says:\n{self.log.read_text() if self.log.exists() else '(no log)'}")


def test_on_linux_the_helper_installs_the_new_download_removes_it_and_starts_alto_again(tmp_path: Path) -> None:
    """
    Check the whole hand-over with the real shell and the real `install.sh`.

    The program is replaced, the work folder is gone, and Alto is started again, from a helper that does not depend on the
    process that started it.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    home = Home(tmp_path, old="OLD", new="NEW")
    assert home.says() == "Alto OLD"
    home.hand_over()
    home.wait_for_restart()
    assert home.says() == "Alto NEW" and home.marker.read_text().strip() == "NEW"
    assert not home.work.exists()
    assert "updated" in home.log.read_text() and "failed" not in home.log.read_text()
    assert not (home.prefix / "opt" / "alto.old").exists() and not (home.prefix / "opt" / "alto.new").exists()


def test_on_linux_a_failed_install_keeps_the_old_copy_and_still_starts_alto(tmp_path: Path) -> None:
    """
    Check that when the new files cannot be copied, the installed copy is untouched and is the one started again.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    home = Home(tmp_path, old="OLD", new="NEW")
    secret = home.root / "alto" / "unreadable"
    secret.write_text("x")
    secret.chmod(0)
    try:
        home.hand_over()
        home.wait_for_restart()
        assert home.says() == "Alto OLD" and home.marker.read_text().strip() == "OLD"
        assert "the update failed" in home.log.read_text()
        assert not (home.prefix / "opt" / "alto.new").exists() and not (home.prefix / "opt" / "alto.old").exists()
    finally:
        if secret.exists():  # the helper removes the whole work folder, which is what should happen, but not if it never ran
            secret.chmod(0o644)
    assert not home.work.exists()


def test_the_helper_waits_for_the_process_it_was_told_about_and_does_not_wait_for_one_that_is_gone(tmp_path: Path) -> None:
    """
    Check that a process id that no longer exists does not hold the update back (the wait loop ends at once).

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    home = Home(tmp_path, old="OLD", new="NEW")
    gone = subprocess.Popen(["true"])
    gone.wait()
    started = time.monotonic()
    selfupdate.start_handoff(
        Prepared(home.work, installer=None, root=home.root),
        target=home.target,
        pid=gone.pid,
        log=home.log,
        environ=home.env,
    )
    home.wait_for_restart()
    assert time.monotonic() - started < 10 and home.says() == "Alto NEW"


def test_leftover_update_folders_are_removed_only_when_old_and_named_for_an_update(tmp_path: Path) -> None:
    """
    Check that an old `alto-update-*` folder is removed, and a recent one and any other folder are not.

    Parameters
    ----------
    tmp_path : Path
        A new folder standing in for the temporary folder.
    """
    old, recent, other = tmp_path / "alto-update-old", tmp_path / "alto-update-recent", tmp_path / "something-else"
    for folder in (old, recent, other):
        folder.mkdir()
        (folder / "file").write_text("x")
    now = time.time()
    os.utime(old, (now - 3 * 86400, now - 3 * 86400))
    os.utime(other, (now - 3 * 86400, now - 3 * 86400))
    assert selfupdate.remove_leftovers(root=tmp_path, now=now) == 1
    assert not old.exists() and recent.exists() and other.exists()


def test_the_log_is_kept_in_altos_folder_of_the_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    Check that the helper's log goes under the cache folder, so that a failed update can be looked into.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Sets the cache folder.
    tmp_path : Path
        A new folder.
    """
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert selfupdate.log_path() == tmp_path / "alto" / "update.log"
