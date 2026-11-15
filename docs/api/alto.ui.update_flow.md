---
title: alto.ui.update_flow
parent: api
package: alto.ui
order: 52
permalink: /api/alto.ui.update_flow/
---
{% raw %}
Checking for a newer Alto and installing it: the questions asked, the progress shown, and the restart afterwards.

The menu's "Check for updates…" asks the address Alto was installed from for its newest commit. If there is a newer one and the
person agrees, `uv tool upgrade alto` installs it while its output is shown, and when it has finished Alto says that it will
restart and does so after OK is pressed. Only a copy that was installed with `scripts/alto-install.sh` can do this; a copy run
from a source folder is told to update with git.

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

## CheckDialog

```python
CheckDialog(
    parent: QWidget | None,
    *,
    source: Source,
    git: str,
)
```

Bases: `QDialog`

A small window that waits while the address Alto came from is asked for its newest commit.

**Attributes**

- `commit` (*str*): The newest commit, once it is known; empty if it could not be found out.
- `error` (*str*): What went wrong, if there is no commit.
- `ended` (*bool*): Whether the asking has ended, by an answer, a failure or a cancel.
- `cancelled` (*bool*): Whether the person cancelled it.
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
>>> CheckDialog(None, source=Source("https://example.org/a.git", commit="abc1234"), git="git").cancelled
False
```

### CheckDialog.reject

```python
def reject() -> None
```

Cancel the asking.

## UpdateDialog

```python
UpdateDialog(
    parent: QWidget | None,
    *,
    uv: str,
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
- `uv` (*str*): The path of the `uv` program. Keyword-only.

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
>>> UpdateDialog(None, uv="uv").succeeded
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
) -> None
```

Ask whether a newer Alto is available and, if the person agrees, install it and restart.

**Parameters**

- `parent` (*QWidget*): The window the questions are asked over.
- `restart` (*Callable*): What to do after a successful update to start the new version in place of this one. Keyword-only.

**Examples**

```pycon
>>> check_for_updates  # doctest: +SKIP
```
{% endraw %}
