r"""
Replacing a packaged copy of Alto with a newer release: whether it can,
getting the update, checking it, and handing over.

A packaged copy is Alto frozen with PyInstaller, in a folder the user
owns: `~/.local/opt/alto` on Linux, made by `install.sh`,
and a folder under `%LOCALAPPDATA%\Programs` on Windows, made by the
installer. Neither needs administrator rights, so Alto can
fetch the new package, check it, and start the program that installs it.
Nothing is installed unless the signature on the list of
checksums verifies against a key that came with Alto, the list names the
file, and the file's hash is the one listed (see
`alto.updates`). This module has no Qt, so the interface runs it on a
worker thread and shows its progress.

Examples
--------
>>> self_update_target(
...     executable=Path("/nowhere/alto"),
...     system="linux",
... ) is None
True
"""

from __future__ import annotations

import base64
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from alto import updates

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Mapping,
    )

# the list of checksums and its signature are a few hundred bytes
MAX_LIST_BYTES = 1_000_000
MAX_PACKAGE_BYTES = 1_000_000_000
LEFTOVER_PREFIX = "alto-update-"
# What the Windows installer is given. `/CLOSEAPPLICATIONS` closes Alto
# if it is still open, and `/RELAUNCH=1` makes alto.iss
# start it again when the files are in place (the installer's own
# restart of the programs it closed is off, so that Alto is not
# started twice). scripts/build-windows.ps1 runs the installer with
# these same arguments, and a test checks that.
WINDOWS_INSTALLER_ARGUMENTS = (
    "/SILENT",
    "/SUPPRESSMSGBOXES",
    "/NORESTART",
    "/CLOSEAPPLICATIONS",
    "/RELAUNCH=1",
)
# How PowerShell is started on Windows to wait for Alto to end and then
# run the installer. The script travels as `-EncodedCommand`
# (base64 of UTF-16), so no path needs to be quoted for a command line,
# and no execution policy applies to it.
POWERSHELL = "powershell.exe"
POWERSHELL_ARGUMENTS = (
    "-NoProfile",
    "-NonInteractive",
    "-WindowStyle",
    "Hidden",
    "-EncodedCommand",
)
# The program that installs an update on Linux. It waits for Alto to end
# (the files it replaces are Alto's own), runs the new
# download's install.sh for the same prefix, removes what was
# downloaded, and starts Alto again, whether or not the install
# worked:
# install.sh keeps the old copy if it fails.
LINUX_HELPER = r"""
pid="$1"; root="$2"; prefix="$3"; work="$4"; log="$5"
exec >>"$log" 2>&1
echo "$(date): updating Alto in $prefix from $root"
waited=0
while kill -0 "$pid" 2>/dev/null && [ "$waited" -lt 150 ]; do
    sleep 0.2
    waited=$((waited + 1))
done
if ALTO_PREFIX="$prefix" sh "$root/install.sh" install; then
    echo "$(date): updated"
else
    echo "$(date): the update failed, and the old copy was kept"
fi
rm -rf "$work"
nohup "$prefix/bin/alto" >/dev/null 2>&1 &
"""


class UpdateError(Exception):
    """
    Something went wrong in getting or checking an update. The message
    says what, in words for the person.
    """


class UpdateCanceled(Exception):
    """The person canceled the update before it was ready."""


@dataclass(frozen=True)
class Target:
    """
    A packaged copy that can replace itself, and where it is.

    Attributes
    ----------
    system : str
        "linux" or "windows".
    folder : Path
        The folder the program is in.
    prefix : Path or None
        On Linux, the folder that holds `opt/alto` and `bin/alto`
        (`~/.local` by default); None on Windows.

    Examples
    --------
    >>> Target(
    ...     "windows",
    ...     folder=Path("C:/Alto"),
    ...     prefix=None,
    ... ).system
    'windows'
    """

    system: str
    folder: Path
    prefix: Path | None


@dataclass(frozen=True)
class Prepared:
    """
    An update that has been downloaded and checked, and is ready to be
    handed over.

    Attributes
    ----------
    work : Path
        The temporary folder that holds it, which is removed after the
        update.
    installer : Path or None
        On Windows, the installer to run.
    root : Path or None
        On Linux, the unpacked download, with its `install.sh`.

    Examples
    --------
    >>> Prepared(
    ...     Path("/tmp/x"),
    ...     installer=None,
    ...     root=Path("/tmp/x/unpacked/alto-0.1.0"),
    ... ).installer is None
    True
    """

    work: Path
    installer: Path | None
    root: Path | None


def self_update_target(
    *,
    executable: Path | None = None,
    system: str | None = None,
) -> Target | None:
    """
    Say whether the running copy can replace itself, and if so where it
    is.

    On Linux a copy can if it was put in `<prefix>/opt/alto` by
    `install.sh`, which links `<prefix>/bin/alto` to it; a folder that
    someone unpacked and ran from cannot. On Windows a copy can if the
    installer made it, which leaves `unins000.exe` beside it.

    Parameters
    ----------
    executable : Path or None, default None
        The running program; the one that is running if None.
        Keyword-only.
    system : str or None, default None
        "linux" or "windows"; this computer's if None. Keyword-only.

    Returns
    -------
    Target or None
        Where the copy is, or None if it cannot replace itself.

    Examples
    --------
    >>> self_update_target(
    ...     executable=Path("/usr/bin/python3"),
    ...     system="linux",
    ... ) is None
    True
    >>> self_update_target(
    ...     executable=Path("/nowhere/alto.exe"),
    ...     system="windows",
    ... ) is None
    True
    """
    program = Path(sys.executable if executable is None else executable)
    kind = (platform.system() if system is None else system).lower()
    if kind == "linux":
        folder = program.parent
        if (
            program.name != "alto"
            or folder.name != "alto"
            or folder.parent.name != "opt"
        ):
            return None
        prefix = folder.parent.parent
        link = prefix / "bin" / "alto"
        if not link.is_symlink() or link.resolve() != program.resolve():
            return None
        return Target("linux", folder=folder, prefix=prefix)
    if (
        kind == "windows"
        and program.name.lower() == "alto.exe"
        and (program.parent / "unins000.exe").is_file()
    ):
        return Target("windows", folder=program.parent, prefix=None)
    return None


def download(
    url: str,
    *,
    destination: Path,
    allowed: str,
    max_bytes: int,
    progress: Callable[[int, int], None],
    canceled: Callable[[], bool],
    seconds: int = 30,
) -> str:
    """
    Fetch a file, checking the address, the size and the connection, and
    give its SHA-256 hash.

    Parameters
    ----------
    url : str
        The address. It must start with `allowed`.
    destination : Path
        Where to write the file. Nothing is left there if the download
        fails or is canceled. Keyword-only.
    allowed : str
        What the address must start with, which is where a release keeps
        its files. Keyword-only.
    max_bytes : int
        The most to accept, by the size the server states and by what
        actually arrives. Keyword-only.
    progress : Callable
        Called with the bytes received so far and the size the server
        states (0 if it does not say). Keyword-only.
    canceled : Callable
        Asked now and then; True stops the download. Keyword-only.
    seconds : int, default 30
        How long to wait for the server at a time. Keyword-only.

    Returns
    -------
    str
        The SHA-256 hash of what was written, in hexadecimal.

    Raises
    ------
    UpdateError
        If the address is not allowed, the file is too large, the
        connection is not secure, or the download fails.
    UpdateCanceled
        If `canceled` said so.
    """
    if not url.startswith(allowed):
        raise UpdateError(
            (
                "The release names a file at an address that Alto does not"
                " download updates from, so it was not used."
            ),
        )
    part = destination.with_name(destination.name + ".part")
    digest = hashlib.sha256()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": updates.USER_AGENT},
    )
    try:
        with (
            urllib.request.urlopen(
                request,
                timeout=seconds,
                context=updates.ssl_context(),
            ) as response,
            part.open("wb") as out,
        ):
            if not (
                response.geturl().startswith("https://")
                or response.geturl().startswith(allowed)
            ):
                raise UpdateError(
                    (
                        "The download was sent to an address that is not "
                        "secure, so it was stopped."
                    ),
                )
            total = int(response.headers.get("Content-Length") or 0)
            if total > max_bytes:
                raise UpdateError(
                    (
                        "The update is larger than expected, so it was not"
                        " downloaded."
                    ),
                )
            received = 0
            while True:
                if canceled():
                    raise UpdateCanceled
                chunk = response.read(65536)
                if not chunk:
                    break
                received += len(chunk)
                if received > max_bytes:
                    raise UpdateError(
                        (
                            "The update is larger than expected, so the "
                            "download was stopped."
                        ),
                    )
                digest.update(chunk)
                out.write(chunk)
                progress(received, total)
    except (UpdateError, UpdateCanceled):
        part.unlink(missing_ok=True)
        raise
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        part.unlink(missing_ok=True)
        raise UpdateError(
            f"The download failed: {getattr(error, 'reason', error)}",
        ) from error
    part.replace(destination)
    return digest.hexdigest()


def extract_tarball(
    archive: Path,
    *,
    destination: Path,
) -> Path:
    """
    Unpack the Linux download, refusing anything that would land outside
    the folder.

    Parameters
    ----------
    archive : Path
        The `.tar.gz`.
    destination : Path
        The folder to unpack it in. Keyword-only.

    Returns
    -------
    Path
        The one folder the download unpacks to, which holds `install.sh`
        and the program.

    Raises
    ------
    UpdateError
        If it cannot be unpacked safely, or is not what an update needs.
    """
    if not hasattr(tarfile, "data_filter"):
        raise UpdateError(
            (
                "This version of Python cannot unpack an update safely, so"
                " it was not installed."
            ),
        )
    destination.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(destination, filter="data")
    except (tarfile.TarError, OSError) as error:
        raise UpdateError(
            f"The download could not be unpacked: {error}",
        ) from error
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if (
        len(roots) != 1
        or not (roots[0] / "install.sh").is_file()
        or not (roots[0] / "alto" / "alto").is_file()
    ):
        raise UpdateError(
            (
                "The download does not hold what an update needs, so it "
                "was not installed."
            ),
        )
    return roots[0]


def ignore_progress(done: int, total: int) -> None:  # noqa: PLR0917  (a progress callback, which is called with two numbers)
    """
    Take a note of progress and do nothing with it, for a download whose
    progress nobody watches.

    Parameters
    ----------
    done : int
        The bytes received so far.
    total : int
        The total the server states.

    Examples
    --------
    >>> ignore_progress(1, 2)
    """
    del done, total


def prepare_update(
    release: updates.Release,
    *,
    target: Target,
    work: Path,
    keys: tuple[str, ...],
    machine: str,
    base: str = updates.DOWNLOAD_BASE,
    status: Callable[[str], None],
    progress: Callable[[int, int], None],
    canceled: Callable[[], bool],
) -> Prepared:
    """
    Download a release for this copy and check it: its signed list of
    checksums, then the file against its listed hash.

    Parameters
    ----------
    release : updates.Release
        The release to install.
    target : Target
        The copy that will be replaced.
    work : Path
        An empty folder to work in.
    keys : tuple of str
        The public keys (base64) a signature may be made with.
        Keyword-only.
    machine : str
        The processor, as `platform.machine()` says it. Keyword-only.
    base : str, default updates.DOWNLOAD_BASE
        Where the release keeps its files. Keyword-only.
    status : Callable
        Called with what is being done, in words for the person.
        Keyword-only.
    progress : Callable
        Called with the bytes received so far and the total, while the
        file downloads. Keyword-only.
    canceled : Callable
        Asked now and then; True stops. Keyword-only.

    Returns
    -------
    Prepared
        The checked update, ready to be handed over.

    Raises
    ------
    UpdateError
        If anything is missing or does not check out. Nothing is
        installed.
    UpdateCanceled
        If `canceled` said so.
    """
    if not keys:
        raise UpdateError(
            (
                "This copy of Alto has no key to check an update with, so "
                "it cannot install one."
            ),
        )
    name = updates.platform_asset_name(
        release.version,
        system=target.system,
        machine=machine,
    )
    if name is None:
        raise UpdateError("This release has no download for this computer.")
    wanted = {
        "download": name,
        "list of checksums": updates.CHECKSUMS_NAME,
        "signature": updates.SIGNATURE_NAME,
    }
    found = {
        what: updates.find_asset(release, name=file, base=base)
        for what, file in wanted.items()
    }
    for what, asset in found.items():
        if asset is None:
            raise UpdateError(
                "This release has no "
                f"{what}"
                " ("
                f"{wanted[what]}"
                "), so it was not installed.",
            )
    package, listing, signature = (
        found["download"],
        found["list of checksums"],
        found["signature"],
    )
    if (
        package is None or listing is None or signature is None
    ):  # said already, and a type checker cannot see that
        raise UpdateError(
            "This release is incomplete, so it was not installed.",
        )
    status("Checking the signature…")
    list_file, signature_file = (
        work / updates.CHECKSUMS_NAME,
        work / updates.SIGNATURE_NAME,
    )
    for asset, path in ((listing, list_file), (signature, signature_file)):
        download(
            asset.url,
            destination=path,
            allowed=base,
            max_bytes=MAX_LIST_BYTES,
            progress=ignore_progress,
            canceled=canceled,
        )
    data = list_file.read_bytes()
    if not updates.verify_signature(
        data,
        signature=signature_file.read_text(encoding="utf-8", errors="replace"),
        keys=keys,
    ):
        raise UpdateError(
            (
                "The signature of this update is not valid, so it was not "
                "installed."
            ),
        )
    try:
        listed = updates.parse_checksums(data.decode("utf-8")).get(name)
    except UnicodeDecodeError as error:
        raise UpdateError(
            (
                "The signed list of checksums cannot be read, so the "
                "update was not installed."
            ),
        ) from error
    if listed is None:
        raise UpdateError(
            "The signed list of checksums does not name "
            f"{name}"
            ", so it was not installed.",
        )
    status(f"Downloading {name}…")
    file = work / name
    actual = download(
        package.url,
        destination=file,
        allowed=base,
        max_bytes=MAX_PACKAGE_BYTES,
        progress=progress,
        canceled=canceled,
    )
    status("Checking the download…")
    if actual != listed:
        file.unlink(missing_ok=True)
        raise UpdateError(
            (
                "The download does not match the checksum that was signed,"
                " so it was not installed."
            ),
        )
    if target.system == "windows":
        return Prepared(work, installer=file, root=None)
    if canceled():
        raise UpdateCanceled
    status("Unpacking…")
    root = extract_tarball(file, destination=work / "unpacked")
    file.unlink(missing_ok=True)
    return Prepared(work, installer=None, root=root)


def clean_environment(env: Mapping[str, str]) -> dict[str, str]:
    """
    Undo what PyInstaller did to the environment, for a program that
    this one starts.

    A packaged program puts its own libraries first on the library path,
    which would make the system's `sh`, `tar` and the next
    Alto load them. PyInstaller keeps the original in
    `LD_LIBRARY_PATH_ORIG`, and asks a program that restarts itself to
    reset
    what it passed on. The desktop's start-up token is for this launch
    only, so it is dropped too.

    Parameters
    ----------
    env : Mapping
        The environment of this program.

    Returns
    -------
    dict of str to str
        The environment to give the other.

    Examples
    --------
    >>> clean_environment(
    ...     {
    ...         "LD_LIBRARY_PATH": "/app/lib",
    ...         "LD_LIBRARY_PATH_ORIG": "/usr/lib",
    ...         "_PYI_ARCHIVE_FILE": "x",
    ...     }
    ... )
    {'LD_LIBRARY_PATH': '/usr/lib', 'PYINSTALLER_RESET_ENVIRONMENT':
    '1'}
    >>> clean_environment(
    ...     {
    ...         "LD_LIBRARY_PATH": "/app/lib",
    ...         "LD_LIBRARY_PATH_ORIG": "",
    ...     }
    ... )
    {'PYINSTALLER_RESET_ENVIRONMENT': '1'}
    >>> clean_environment({"HOME": "/home/me"})
    {'HOME': '/home/me', 'PYINSTALLER_RESET_ENVIRONMENT': '1'}
    """
    cleaned = dict(env)
    original = cleaned.pop("LD_LIBRARY_PATH_ORIG", None)
    if original is not None:
        if original:
            cleaned["LD_LIBRARY_PATH"] = original
        else:
            cleaned.pop("LD_LIBRARY_PATH", None)
    for name in list(cleaned):
        if name.startswith("_PYI_") or name in {
            "_MEIPASS2",
            "XDG_ACTIVATION_TOKEN",
            "DESKTOP_STARTUP_ID",
        }:
            del cleaned[name]
    cleaned["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return cleaned


def log_path() -> Path:
    """
    Give the file the Linux helper writes to, so that a failed update
    can be looked into.

    Returns
    -------
    Path
        `update.log` in Alto's folder of the user's cache.

    Examples
    --------
    >>> log_path().name
    'update.log'
    """
    return (
        Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
        / "alto"
        / "update.log"
    )


def windows_handoff_command(
    installer: Path,
    *,
    pid: int,
    alto: Path,
) -> list[str]:
    """
    Give the command that waits for Alto to end, runs the installer, and
    starts the old Alto again if the installer fails.

    The installer must not start while Alto is still closing: it would
    find Alto's files in use and, with no one to answer, give
    up. So Alto starts this command and quits, and the command waits for
    Alto's process to be gone before it begins.

    Parameters
    ----------
    installer : Path
        The downloaded installer.
    pid : int
        Alto's process, which is waited for (for at most a minute).
        Keyword-only.
    alto : Path
        The installed `alto.exe`, which is started again if the
        installer fails, so that the person is not left with no Alto.
        When it succeeds, the installer starts Alto itself
        (`/RELAUNCH=1`). Keyword-only.

    Returns
    -------
    list of str
        The program and its arguments.

    Examples
    --------
    >>> command = windows_handoff_command(
    ...     Path("C:/Temp/setup.exe"),
    ...     pid=42,
    ...     alto=Path("C:/Alto/alto.exe"),
    ... )
    >>> (
    ...     command[0],
    ...     command[1:-1]
    ...     == list(POWERSHELL_ARGUMENTS),
    ... )
    ('powershell.exe', True)
    >>> text = base64.b64decode(command[-1]).decode(
    ...     "utf-16-le"
    ... )
    >>> "Wait-Process -Id 42" in text and "/RELAUNCH=1" in text
    True
    """

    def literal(text: str) -> str:
        """
        Write text as a PowerShell string that nothing in it can end
        early.

        Parameters
        ----------
        text : str
            The text.

        Returns
        -------
        str
            The text in single quotes, with each single quote inside
            doubled.
        """
        return "'" + text.replace("'", "''") + "'"

    arguments = ",".join(
        literal(argument) for argument in WINDOWS_INSTALLER_ARGUMENTS
    )
    script = "\n".join(
        [
            "$ErrorActionPreference = 'Continue'",
            (
                "try { Wait-Process -Id "
                f"{int(pid)}"
                " -Timeout 60 -ErrorAction Stop } catch { }"
            ),
            (
                "$run = Start-Process -FilePath "
                f"{literal(str(installer))}"
                " -ArgumentList "
                f"{arguments}"
                " -PassThru"
            ),
            # not `-Wait`, which also waits for what the installer
            # starts: the Alto it opens again
            "if ($null -ne $run) { $run.WaitForExit() }",
            (
                "if ($null -eq $run -or $run.ExitCode -ne 0) { Start-Process "
                "-FilePath "
                f"{literal(str(alto))}"
                " }"
            ),
        ],
    )
    return [
        POWERSHELL,
        *POWERSHELL_ARGUMENTS,
        base64.b64encode(script.encode("utf-16-le")).decode(),
    ]


def start_handoff(
    prepared: Prepared,
    *,
    target: Target,
    pid: int | None = None,
    log: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> None:
    """
    Start the program that installs the update, and return at once so
    that Alto can quit.

    Parameters
    ----------
    prepared : Prepared
        The checked update.
    target : Target
        The copy that is replaced.
    pid : int or None, default None
        The process to wait for, which is Alto; this one if None.
        Keyword-only.
    log : Path or None, default None
        Where the Linux helper writes; `log_path()` if None.
        Keyword-only.
    environ : Mapping or None, default None
        The environment to start from; this program's if None.
        Keyword-only.

    Raises
    ------
    UpdateError
        If the update is missing what the system needs.
    """
    env = clean_environment(os.environ if environ is None else environ)
    quiet = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if target.system == "windows":
        if prepared.installer is None:
            raise UpdateError(
                (
                    "There is no installer to run, so the update was not "
                    "installed."
                ),
            )
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
            subprocess,
            "CREATE_NEW_PROCESS_GROUP",
            0,
        )
        alto = target.folder / "alto.exe"
        if shutil.which(POWERSHELL, path=env.get("PATH")):
            command = windows_handoff_command(
                prepared.installer,
                pid=os.getpid() if pid is None else pid,
                alto=alto,
            )
        # no PowerShell to wait with: start the installer at once, which
        # closes Alto if it is still open
        else:
            command = [str(prepared.installer), *WINDOWS_INSTALLER_ARGUMENTS]
        subprocess.Popen(command, env=env, creationflags=flags, **quiet)  # noqa: S603
        return
    if prepared.root is None or target.prefix is None:
        raise UpdateError(
            (
                "There is nothing unpacked to install, so the update was "
                "not installed."
            ),
        )
    where = log_path() if log is None else log
    where.parent.mkdir(parents=True, exist_ok=True)
    arguments = [
        str(os.getpid() if pid is None else pid),
        str(prepared.root),
        str(target.prefix),
        str(prepared.work),
        str(where),
    ]
    subprocess.Popen(
        ["sh", "-c", LINUX_HELPER, "alto-update", *arguments],
        env=env,
        start_new_session=True,
        **quiet,
    )  # noqa: S603, S607


def new_work_folder() -> Path:
    """
    Make a new temporary folder for an update, whose name says what it
    is for.

    Returns
    -------
    Path
        The empty folder.

    Examples
    --------
    >>> folder = new_work_folder()
    >>> folder.is_dir() and folder.name.startswith(
    ...     LEFTOVER_PREFIX
    ... )
    True
    >>> folder.rmdir()
    """
    return Path(tempfile.mkdtemp(prefix=LEFTOVER_PREFIX))


def remove_leftovers(
    *,
    older_than: float = 86400.0,
    now: float | None = None,
    root: Path | None = None,
) -> int:
    """
    Remove the temporary folders of earlier updates that were never
    cleaned up, such as a Windows installer that was run and left.

    Parameters
    ----------
    older_than : float, default 86400.0
        How old, in seconds, a folder must be. Keyword-only.
    now : float or None, default None
        The time to measure from; the clock's if None. Keyword-only.
    root : Path or None, default None
        The folder to look in; the system's temporary folder if None.
        Keyword-only.

    Returns
    -------
    int
        How many folders were removed.

    Examples
    --------
    >>> remove_leftovers(
    ...     root=Path("/no/such/folder")
    ... )
    0
    """
    folder = Path(tempfile.gettempdir()) if root is None else root
    cutoff = (time.time() if now is None else now) - older_than
    removed = 0
    if not folder.is_dir():
        return 0
    for path in folder.glob(LEFTOVER_PREFIX + "*"):
        try:
            if path.is_dir() and path.stat().st_mtime < cutoff:
                shutil.rmtree(path)
                removed += 1
        except OSError:
            continue
    return removed
