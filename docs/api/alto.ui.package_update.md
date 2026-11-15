---
title: alto.ui.package_update
parent: api
package: alto.ui
order: 40
permalink: /api/alto.ui.package_update/
---
{% raw %}
The window that updates a packaged copy of Alto: the download and its checks with their progress, then what happens next.

The work is in `alto.selfupdate`, which has no Qt, and runs on another thread here so that the window keeps moving. Until the
download has been checked nothing has been installed, and Cancel (or closing the window) throws it away. When it is ready the
window says that Alto will close, install the update and open again, and OK hands over; the caller starts the installer and quits.

**Examples**

```pycon
>>> from alto.updates import Release
>>> PackageUpdateDialog  # doctest: +ELLIPSIS
<class '...PackageUpdateDialog'>
```

## UpdatePreparer

```python
UpdatePreparer(parent: QObject | None = None)
```

Bases: `QObject`

Download and check an update on another thread, and report how it goes through signals.

**Attributes**

- `status` (*Signal*): Emitted with what is being done ("Checking the signature…").
- `progress` (*Signal*): Emitted with the bytes received so far and the total (0 if it is not known), while the file downloads.
- `done` (*Signal*): Emitted once at the end, with 0 if the update is ready (see `prepared`) or 1 if it failed, and the reason. Nothing is emitted if the person cancelled.
- `prepared` (*Prepared or None*): The checked update, once it is ready.

**Examples**

```pycon
>>> UpdatePreparer().prepared is None
True
```

**Constructor**

Make a preparer that has not started.

**Parameters**

- `parent` (*QObject or None, default None*): The object that owns it.

### UpdatePreparer.start

```python
def start(
    *,
    release: Release,
    target: Target,
    work: Path,
    keys: tuple[str, ...],
) -> None
```

Start downloading and checking.

**Parameters**

- `release` (*Release*): The release to install.
- `target` (*Target*): The copy that will be replaced.
- `work` (*Path*): An empty folder to work in.
- `keys` (*tuple of str*): The public keys (base64) a signature may be made with.

### UpdatePreparer.cancel

```python
def cancel() -> None
```

Stop, at the next chance, and say nothing more.

### UpdatePreparer.is_cancelled

```python
def is_cancelled() -> bool
```

Say whether the person has cancelled.

**Returns**

- *bool*: True once `cancel` has been called.

**Examples**

```pycon
>>> UpdatePreparer().is_cancelled()
False
```

## PackageUpdateDialog

```python
PackageUpdateDialog(
    parent: QWidget | None,
    *,
    release: Release,
    target: Target,
)
```

Bases: `QDialog`

The window that downloads and checks an update for a packaged copy, and then says what happens next.

**Attributes**

- `status` (*QLabel*): What is happening.
- `bar` (*QProgressBar*): The progress of the download; a bar that keeps moving while the size is not known.
- `button` (*QPushButton*): Cancel while the update is being prepared, then OK if it is ready or Close if it failed.
- `ended` (*bool*): Whether the preparing has ended, ready, failed or cancelled.
- `ready` (*bool*): Whether the update is downloaded and checked.
- `cancelled` (*bool*): Whether the person cancelled.
- `error` (*str*): Why it failed, if it did.
- `preparer` (*UpdatePreparer*): What does the work.

**Constructor**

Build the window; nothing is downloaded until `run` is called.

**Parameters**

- `parent` (*QWidget or None*): The window it belongs to.
- `release` (*Release*): The release to install. Keyword-only.
- `target` (*Target*): The copy that will be replaced. Keyword-only.

### PackageUpdateDialog.run

```python
def run() -> Prepared | None
```

Download and check the update, showing the window until the person has read how it went.

**Returns**

- *Prepared or None*: The update, if it is ready and OK was pressed; None if it failed or was cancelled, in which case nothing is left behind.

**Examples**

```pycon
>>> here = Target("linux", folder=Path("/x"), prefix=None)
>>> # noinspection PyTypeChecker
>>> PackageUpdateDialog(None, release=Release("0.1.0", tag="v0.1.0", url=""), target=here).ready
False
```

### PackageUpdateDialog.reject

```python
def reject() -> None
```

Close the window; before the update is ready that cancels it.
{% endraw %}
