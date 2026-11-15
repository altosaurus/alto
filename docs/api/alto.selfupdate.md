---
title: alto.selfupdate
parent: api
package: alto
order: 5
permalink: /api/alto.selfupdate/
---
{% raw %}
Replacing a packaged copy of Alto with a newer release: whether it can, getting the update, checking it, and handing over.

A packaged copy is Alto frozen with PyInstaller, in a folder the user owns: `~/.local/opt/alto` on Linux, made by `install.sh`,
and a folder under `%LOCALAPPDATA%\Programs` on Windows, made by the installer. Neither needs administrator rights, so Alto can
fetch the new package, check it, and start the program that installs it. Nothing is installed unless the signature on the list of
checksums verifies against a key that came with Alto, the list names the file, and the file's hash is the one listed (see
`alto.updates`). This module has no Qt, so the interface runs it on a worker thread and shows its progress.

**Examples**

```pycon
>>> self_update_target(executable=Path("/nowhere/alto"), system="linux") is None
True
```

## UpdateError

```python
class UpdateError(Exception)
```

Something went wrong in getting or checking an update. The message says what, in words for the person.

## UpdateCancelled

```python
class UpdateCancelled(Exception)
```

The person cancelled the update before it was ready.

## Target

```python
Target(
    system: str,
    folder: Path,
    prefix: Path | None,
)
```

A packaged copy that can replace itself, and where it is.

**Attributes**

- `system` (*str*): "linux" or "windows".
- `folder` (*Path*): The folder the program is in.
- `prefix` (*Path or None*): On Linux, the folder that holds `opt/alto` and `bin/alto` (`~/.local` by default); None on Windows.

**Examples**

```pycon
>>> Target("windows", folder=Path("C:/Alto"), prefix=None).system
'windows'
```

## Prepared

```python
Prepared(
    work: Path,
    installer: Path | None,
    root: Path | None,
)
```

An update that has been downloaded and checked, and is ready to be handed over.

**Attributes**

- `work` (*Path*): The temporary folder that holds it, which is removed after the update.
- `installer` (*Path or None*): On Windows, the installer to run.
- `root` (*Path or None*): On Linux, the unpacked download, with its `install.sh`.

**Examples**

```pycon
>>> Prepared(Path("/tmp/x"), installer=None, root=Path("/tmp/x/unpacked/alto-0.1.0")).installer is None
True
```

## self_update_target

```python
def self_update_target(
    *,
    executable: Path | None = None,
    system: str | None = None,
) -> Target | None
```

Say whether the running copy can replace itself, and if so where it is.

On Linux a copy can if it was put in `<prefix>/opt/alto` by `install.sh`, which links `<prefix>/bin/alto` to it; a folder that
someone unpacked and ran from cannot. On Windows a copy can if the installer made it, which leaves `unins000.exe` beside it.

**Parameters**

- `executable` (*Path or None, default None*): The running program; the one that is running if None. Keyword-only.
- `system` (*str or None, default None*): "linux" or "windows"; this computer's if None. Keyword-only.

**Returns**

- *Target or None*: Where the copy is, or None if it cannot replace itself.

**Examples**

```pycon
>>> self_update_target(executable=Path("/usr/bin/python3"), system="linux") is None
True
>>> self_update_target(executable=Path("/nowhere/alto.exe"), system="windows") is None
True
```

## download

```python
def download(
    url: str,
    *,
    destination: Path,
    allowed: str,
    max_bytes: int,
    progress: Callable[[int, int], None],
    cancelled: Callable[[], bool],
    seconds: int = 30,
) -> str
```

Fetch a file, checking the address, the size and the connection, and give its SHA-256 hash.

**Parameters**

- `url` (*str*): The address. It must start with `allowed`.
- `destination` (*Path*): Where to write the file. Nothing is left there if the download fails or is cancelled. Keyword-only.
- `allowed` (*str*): What the address must start with, which is where a release keeps its files. Keyword-only.
- `max_bytes` (*int*): The most to accept, by the size the server states and by what actually arrives. Keyword-only.
- `progress` (*Callable*): Called with the bytes received so far and the size the server states (0 if it does not say). Keyword-only.
- `cancelled` (*Callable*): Asked now and then; True stops the download. Keyword-only.
- `seconds` (*int, default 30*): How long to wait for the server at a time. Keyword-only.

**Returns**

- *str*: The SHA-256 hash of what was written, in hexadecimal.

**Raises**

- *UpdateError*: If the address is not allowed, the file is too large, the connection is not secure, or the download fails.
- *UpdateCancelled*: If `cancelled` said so.

## extract_tarball

```python
def extract_tarball(
    archive: Path,
    *,
    destination: Path,
) -> Path
```

Unpack the Linux download, refusing anything that would land outside the folder.

**Parameters**

- `archive` (*Path*): The `.tar.gz`.
- `destination` (*Path*): The folder to unpack it in. Keyword-only.

**Returns**

- *Path*: The one folder the download unpacks to, which holds `install.sh` and the program.

**Raises**

- *UpdateError*: If it cannot be unpacked safely, or is not what an update needs.

## ignore_progress

```python
def ignore_progress(
    done: int,
    total: int,
) -> None
```

Take a note of progress and do nothing with it, for a download whose progress nobody watches.

**Parameters**

- `done` (*int*): The bytes received so far.
- `total` (*int*): The total the server states.

**Examples**

```pycon
>>> ignore_progress(1, 2)
```

## prepare_update

```python
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
    cancelled: Callable[[], bool],
) -> Prepared
```

Download a release for this copy and check it: its signed list of checksums, then the file against its listed hash.

**Parameters**

- `release` (*updates.Release*): The release to install.
- `target` (*Target*): The copy that will be replaced.
- `work` (*Path*): An empty folder to work in.
- `keys` (*tuple of str*): The public keys (base64) a signature may be made with. Keyword-only.
- `machine` (*str*): The processor, as `platform.machine()` says it. Keyword-only.
- `base` (*str, default updates.DOWNLOAD_BASE*): Where the release keeps its files. Keyword-only.
- `status` (*Callable*): Called with what is being done, in words for the person. Keyword-only.
- `progress` (*Callable*): Called with the bytes received so far and the total, while the file downloads. Keyword-only.
- `cancelled` (*Callable*): Asked now and then; True stops. Keyword-only.

**Returns**

- *Prepared*: The checked update, ready to be handed over.

**Raises**

- *UpdateError*: If anything is missing or does not check out. Nothing is installed.
- *UpdateCancelled*: If `cancelled` said so.

## clean_environment

```python
def clean_environment(env: Mapping[str, str]) -> dict[str, str]
```

Undo what PyInstaller did to the environment, for a program that this one starts.

A packaged program puts its own libraries first on the library path, which would make the system's `sh`, `tar` and the next
Alto load them. PyInstaller keeps the original in `LD_LIBRARY_PATH_ORIG`, and asks a program that restarts itself to reset
what it passed on. The desktop's start-up token is for this launch only, so it is dropped too.

**Parameters**

- `env` (*Mapping*): The environment of this program.

**Returns**

- *dict of str to str*: The environment to give the other.

**Examples**

```pycon
>>> clean_environment({"LD_LIBRARY_PATH": "/app/lib", "LD_LIBRARY_PATH_ORIG": "/usr/lib", "_PYI_ARCHIVE_FILE": "x"})
{'LD_LIBRARY_PATH': '/usr/lib', 'PYINSTALLER_RESET_ENVIRONMENT': '1'}
>>> clean_environment({"LD_LIBRARY_PATH": "/app/lib", "LD_LIBRARY_PATH_ORIG": ""})
{'PYINSTALLER_RESET_ENVIRONMENT': '1'}
>>> clean_environment({"HOME": "/home/me"})
{'HOME': '/home/me', 'PYINSTALLER_RESET_ENVIRONMENT': '1'}
```

## log_path

```python
def log_path() -> Path
```

Give the file the Linux helper writes to, so that a failed update can be looked into.

**Returns**

- *Path*: `update.log` in Alto's folder of the user's cache.

**Examples**

```pycon
>>> log_path().name
'update.log'
```

## windows_handoff_command

```python
def windows_handoff_command(
    installer: Path,
    *,
    pid: int,
    alto: Path,
) -> list[str]
```

Give the command that waits for Alto to end, runs the installer, and starts the old Alto again if the installer fails.

The installer must not start while Alto is still closing: it would find Alto's files in use and, with no one to answer, give
up. So Alto starts this command and quits, and the command waits for Alto's process to be gone before it begins.

**Parameters**

- `installer` (*Path*): The downloaded installer.
- `pid` (*int*): Alto's process, which is waited for (for at most a minute). Keyword-only.
- `alto` (*Path*): The installed `alto.exe`, which is started again if the installer fails, so that the person is not left with no Alto. When it succeeds, the installer starts Alto itself (`/RELAUNCH=1`). Keyword-only.

**Returns**

- *list of str*: The program and its arguments.

**Examples**

```pycon
>>> command = windows_handoff_command(Path("C:/Temp/setup.exe"), pid=42, alto=Path("C:/Alto/alto.exe"))
>>> command[0], command[1:-1] == list(POWERSHELL_ARGUMENTS)
('powershell.exe', True)
>>> text = base64.b64decode(command[-1]).decode("utf-16-le")
>>> "Wait-Process -Id 42" in text and "/RELAUNCH=1" in text
True
```

## start_handoff

```python
def start_handoff(
    prepared: Prepared,
    *,
    target: Target,
    pid: int | None = None,
    log: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> None
```

Start the program that installs the update, and return at once so that Alto can quit.

**Parameters**

- `prepared` (*Prepared*): The checked update.
- `target` (*Target*): The copy that is replaced.
- `pid` (*int or None, default None*): The process to wait for, which is Alto; this one if None. Keyword-only.
- `log` (*Path or None, default None*): Where the Linux helper writes; `log_path()` if None. Keyword-only.
- `environ` (*Mapping or None, default None*): The environment to start from; this program's if None. Keyword-only.

**Raises**

- *UpdateError*: If the update is missing what the system needs.

## new_work_folder

```python
def new_work_folder() -> Path
```

Make a new temporary folder for an update, whose name says what it is for.

**Returns**

- *Path*: The empty folder.

**Examples**

```pycon
>>> folder = new_work_folder()
>>> folder.is_dir() and folder.name.startswith(LEFTOVER_PREFIX)
True
>>> folder.rmdir()
```

## remove_leftovers

```python
def remove_leftovers(
    *,
    older_than: float = 86400.0,
    now: float | None = None,
    root: Path | None = None,
) -> int
```

Remove the temporary folders of earlier updates that were never cleaned up, such as a Windows installer that was run and left.

**Parameters**

- `older_than` (*float, default 86400.0*): How old, in seconds, a folder must be. Keyword-only.
- `now` (*float or None, default None*): The time to measure from; the clock's if None. Keyword-only.
- `root` (*Path or None, default None*): The folder to look in; the system's temporary folder if None. Keyword-only.

**Returns**

- *int*: How many folders were removed.

**Examples**

```pycon
>>> remove_leftovers(root=Path("/no/such/folder"))
0
```
{% endraw %}
