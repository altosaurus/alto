---
title: alto.ui.update_flow
parent: api
package: alto.ui
order: 64
permalink: /api/alto.ui.update_flow/
---
{% raw %}
Checking for a newer Alto and installing it: the questions asked, the progress shown, and the restart afterwards.

The menu's "Check for updates…" follows one of two channels, chosen in Settings: the newest release (the default), or the
newest commit on the main branch. A copy installed with `scripts/alto-install.sh` can replace itself, from either, with
`uv tool install`, showing its output, and restarts when OK is pressed. A packaged copy cannot replace itself, so it is told
that a newer release exists and offered the page where it can be downloaded; it always follows releases. A copy run from a
source folder is told to update with git.

**Examples**

```pycon
>>> brief("fatal: unable to access 'https://example.org/': Could not resolve host\n")
"fatal: unable to access 'https://example.org/': Could not resolve host"
```

## brief

```python
def brief(
    text: str,
    *,
    limit: int = 400,
) -> str
```

Cut what a program printed down to what is worth showing in a message: the end of it, without the blank space around it.

**Parameters**

- `text` (*str*): What the program printed.
- `limit` (*int, default 400*): The most characters to keep. Keyword-only.

**Returns**

- *str*: The end of the text, at most `limit` characters long.

**Examples**

```pycon
>>> brief("  one\ntwo  \n")
'one\ntwo'
>>> brief("x" * 10, limit=4)
'xxxx'
```

## CommandRunner

```python
CommandRunner(parent: QObject | None = None)
```

Bases: `QObject`

Run one program without freezing the window, handing on what it prints as it prints it, and how it ended.

**Attributes**

- `output` (*Signal*): Emitted with each piece of text the program prints, as it arrives. Its errors are mixed in with it.
- `done` (*Signal*): Emitted once, with the exit code and everything the program printed. The exit code is -1 if the program could not be started, was stopped for taking too long, or crashed.

**Examples**

```pycon
>>> runner = CommandRunner()
>>> runner.running
False
```

**Constructor**

Make a runner that has not started anything.

**Parameters**

- `parent` (*QObject or None, default None*): The object that owns it.

### CommandRunner.running

```python
@property
def running() -> bool
```

Say whether a program has been started and has not yet ended.

**Returns**

- *bool*: True while it runs.

### CommandRunner.start

```python
def start(
    program: str,
    *,
    arguments: list[str],
    seconds: int = 0,
) -> None
```

Start a program.

**Parameters**

- `program` (*str*): The program's path.
- `arguments` (*list of str*): What to give it. Keyword-only.
- `seconds` (*int, default 0*): Stop it if it has not ended by then; 0 lets it take as long as it takes. Keyword-only.

**Examples**

```pycon
>>> import sys
>>> runner = CommandRunner()
>>> runner.start(sys.executable, arguments=["-c", "import time; time.sleep(30)"])
>>> runner.stop()
>>> runner.running
False
```

### CommandRunner.stop

```python
def stop() -> None
```

Stop the program, if it is running, without announcing that it has ended.

**Examples**

```pycon
>>> CommandRunner().stop()
```

## saved_channel

```python
def saved_channel() -> str
```

Return what the update check follows, as chosen in Settings.

**Returns**

- *str*: "releases" for the newest release, or "main" for the newest commit on the main branch; "releases" if nothing valid is saved.

**Examples**

```pycon
>>> saved_channel()
'releases'
>>> save_channel("main")
>>> saved_channel()
'main'
>>> save_channel("releases")
```

## save_channel

```python
def save_channel(channel: str) -> None
```

Remember what the update check follows.

**Parameters**

- `channel` (*str*): "releases" or "main". Anything else is saved as "releases".

**Examples**

```pycon
>>> save_channel("nonsense")
>>> saved_channel()
'releases'
```

## WaitDialog

```python
WaitDialog(
    parent: QWidget | None,
    *,
    text: str,
)
```

Bases: `QDialog`

A small window with a bar that keeps moving and a Cancel button, shown while something is asked for.

**Attributes**

- `ended` (*bool*): Whether the asking has ended, by an answer, a failure or a cancel.
- `canceled` (*bool*): Whether the person canceled it.

**Constructor**

Build the window.

**Parameters**

- `parent` (*QWidget or None*): The window it belongs to.
- `text` (*str*): What is being asked for. Keyword-only.

### WaitDialog.reject

```python
def reject() -> None
```

Cancel the asking.

## CheckDialog

```python
CheckDialog(
    parent: QWidget | None,
    *,
    source: Source,
    git: str,
)
```

Bases: `WaitDialog`

A waiting window while the address Alto came from is asked for the newest commit of its main branch.

**Attributes**

- `commit` (*str*): The newest commit, once it is known; empty if it could not be found out.
- `error` (*str*): What went wrong, if there is no commit.
- `runner` (*CommandRunner*): The program that does the asking.

**Constructor**

Build the window; it asks nothing until `run` is called.

**Parameters**

- `parent` (*QWidget or None*): The window it belongs to.
- `source` (*Source*): Where the running copy of Alto came from. Keyword-only.
- `git` (*str*): The path of the `git` program. Keyword-only.

### CheckDialog.run

```python
def run() -> None
```

Ask, showing the window until there is an answer.

**Examples**

```pycon
>>> # noinspection PyTypeChecker
>>> CheckDialog(None, source=Source("https://example.org/a.git", commit="abc1234"), git="git").canceled
False
```

## ReleaseFetcher

```python
ReleaseFetcher(parent: QObject | None = None)
```

Bases: `QObject`

Ask GitHub for the latest release on another thread, so that the window never freezes while it waits.

**Attributes**

- `done` (*Signal*): Emitted once, with the HTTP status (0 if GitHub was not reached) and the answer or the reason there was none.

**Examples**

```pycon
>>> ReleaseFetcher().cancel()
```

**Constructor**

Make a fetcher that has not asked anything.

**Parameters**

- `parent` (*QObject or None, default None*): The object that owns it.

### ReleaseFetcher.start

```python
def start(
    *,
    seconds: int,
) -> None
```

Start asking.

**Parameters**

- `seconds` (*int*): How long to wait for GitHub. Keyword-only.

### ReleaseFetcher.cancel

```python
def cancel() -> None
```

Stop caring about the answer; the thread ends by itself when GitHub answers or the time is up.

## ReleaseDialog

```python
ReleaseDialog(parent: QWidget | None)
```

Bases: `WaitDialog`

A waiting window while GitHub is asked for the latest release.

**Attributes**

- `release` (*Release or None*): The latest release, once it is known; None if it could not be found out.
- `error` (*str*): What went wrong, if there is no release.
- `fetcher` (*ReleaseFetcher*): What does the asking.

**Constructor**

Build the window; it asks nothing until `run` is called.

**Parameters**

- `parent` (*QWidget or None*): The window it belongs to.

### ReleaseDialog.run

```python
def run() -> None
```

Ask, showing the window until there is an answer.

**Examples**

```pycon
>>> # noinspection PyTypeChecker
>>> ReleaseDialog(None).canceled
False
```

## UpdateDialog

```python
UpdateDialog(
    parent: QWidget | None,
    *,
    command: tuple[str, list[str]],
)
```

Bases: `QDialog`

The window that shows an update being installed: a bar that keeps moving, what `uv` prints, and then what comes next.

It cannot be closed while the update runs, because stopping it half way could leave the installed copy broken. When it has
finished it says so, and its one button closes it. After a successful update the caller restarts Alto.

**Attributes**

- `status` (*QLabel*): What is happening.
- `bar` (*QProgressBar*): A bar that keeps moving while the update runs, and fills when it has succeeded.
- `log` (*QPlainTextEdit*): What `uv` prints, as it prints it.
- `button` (*QPushButton*): Enabled when the update has ended.
- `ended` (*bool*): Whether the update has ended.
- `succeeded` (*bool*): Whether it ended well.
- `runner` (*CommandRunner*): The program that does the update.

**Constructor**

Build the window; the update does not start until `run` is called.

**Parameters**

- `parent` (*QWidget or None*): The window it belongs to.
- `command` (*tuple of str and list of str*): The program that installs the update and its arguments. Keyword-only.

### UpdateDialog.run

```python
def run() -> bool
```

Install the update, showing the window until the person has read how it went.

**Returns**

- *bool*: True if it succeeded and OK was pressed, so Alto should restart.

**Examples**

```pycon
>>> # noinspection PyTypeChecker
>>> UpdateDialog(None, command=("uv", ["tool", "install", "alto"])).succeeded
False
```

### UpdateDialog.reject

```python
def reject() -> None
```

Close the window, but not while the update is running.

### UpdateDialog.closeEvent

```python
def closeEvent(event: QCloseEvent) -> None
```

Refuse to close while the update is running.

**Parameters**

- `event` (*QCloseEvent*): The request to close.

## check_for_updates

```python
def check_for_updates(
    parent: QWidget,
    *,
    restart: Callable[[], None],
    quit_app: Callable[[], None] = QApplication.quit,
) -> None
```

Ask whether a newer Alto is available and, if the person agrees, install it and restart.

What is asked depends on the copy: one run from a source folder is told how it is updated; a packaged copy asks for the
latest release and is offered its download page; one installed with the script follows what Settings says, the latest release
or the main branch, and can install it.

**Parameters**

- `parent` (*QWidget*): The window the questions are asked over.
- `restart` (*Callable*): What to do after a successful update to start the new version in place of this one. Keyword-only.
- `quit_app` (*Callable, default QApplication.quit*): What to do to close Alto once an update has been handed to the program that installs it, which is how a packaged copy is replaced. Keyword-only.

**Examples**

```pycon
>>> check_for_updates  # doctest: +SKIP
```

## check_release

```python
def check_release(
    parent: QWidget,
    *,
    kind: InstallKind,
    source: Source | None,
    restart: Callable[[], None],
    quit_app: Callable[[], None],
) -> None
```

Ask GitHub for the latest release and compare it with the version that is running.

**Parameters**

- `parent` (*QWidget*): The window the questions are asked over.
- `kind` (*InstallKind*): What kind of copy is running: a packaged one is offered a download page, and one installed with the script is offered the update. Keyword-only.
- `source` (*Source or None*): Where the running copy came from; None for a packaged copy. Keyword-only.
- `restart` (*Callable*): What to do after a successful update. Keyword-only.
- `quit_app` (*Callable*): What to do to close Alto once an update has been handed to the program that installs it. Keyword-only.

**Examples**

```pycon
>>> check_release  # doctest: +SKIP
```

## check_main

```python
def check_main(
    parent: QWidget,
    *,
    source: Source,
    restart: Callable[[], None],
) -> None
```

Ask the address Alto came from for the newest commit on its main branch and compare it with the one that is running.

**Parameters**

- `parent` (*QWidget*): The window the questions are asked over.
- `source` (*Source*): Where the running copy came from. Keyword-only.
- `restart` (*Callable*): What to do after a successful update. Keyword-only.

**Examples**

```pycon
>>> check_main  # doctest: +SKIP
```

## install

```python
def install(
    parent: QWidget,
    *,
    source: Source,
    tag: str | None,
    restart: Callable[[], None],
) -> None
```

Install a release, or the newest commit of the main branch, showing the progress, and restart if it worked.

**Parameters**

- `parent` (*QWidget*): The window the progress is shown over.
- `source` (*Source*): Where the running copy came from. Keyword-only.
- `tag` (*str or None*): The release to install, such as "v0.1.0"; None for the newest commit of the main branch. Keyword-only.
- `restart` (*Callable*): What to do after a successful update. Keyword-only.

**Examples**

```pycon
>>> install  # doctest: +SKIP
```

## update_package

```python
def update_package(
    parent: QWidget,
    *,
    release: updates.Release,
    target: selfupdate.Target,
    installed: str,
    quit_app: Callable[[], None],
) -> None
```

Offer to replace a packaged copy with a release: download and check it, say that Alto will restart, and hand over.

**Parameters**

- `parent` (*QWidget*): The window the questions are asked over.
- `release` (*updates.Release*): The newer release. Keyword-only.
- `target` (*selfupdate.Target*): The copy that will be replaced. Keyword-only.
- `installed` (*str*): The version that is running. Keyword-only.
- `quit_app` (*Callable*): What to do to close Alto once the update has been handed to the program that installs it. Keyword-only.

**Examples**

```pycon
>>> update_package  # doctest: +SKIP
```
{% endraw %}
