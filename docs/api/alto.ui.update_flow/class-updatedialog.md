---
title: UpdateDialog
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/class-updatedialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
UpdateDialog(
    parent: QWidget | None,
    *,
    command: tuple[str, list[str]],
)
```

{% endraw %}{% include api-source.html name="UpdateDialog" line=823 %}{% raw %}

</div>

Bases: `QDialog`

The window that shows an update being installed: a bar that keeps
moving, what `uv` prints, and then what comes next.

It cannot be closed while the update runs, because stopping it half
way could leave the installed copy broken. When it has
finished it says so, and its one button closes it. After a
successful update the caller restarts Alto.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `status` | `QLabel` | What is happening. |
| `bar` | `QProgressBar` | A bar that keeps moving while the update runs, and fills when it has succeeded. |
| `log` | `QPlainTextEdit` | What `uv` prints, as it prints it. |
| `button` | `QPushButton` | Enabled when the update has ended. |
| `ended` | `bool` | Whether the update has ended. |
| `succeeded` | `bool` | Whether it ended well. |
| `runner` | `CommandRunner` | The program that does the update. |

**Constructor**

Build the window; the update does not start until `run` is
called.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None` | The window it belongs to. |
| `command` | `tuple of str and list of str` | The program that installs the update and its arguments. Keyword-only. |

## UpdateDialog.run

<div class="api-signature" markdown="1">

```python
def run() -> bool
```

{% endraw %}{% include api-source.html name="UpdateDialog.run" line=899 %}{% raw %}

</div>

Install the update, showing the window until the person has read
how it went.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if it succeeded and OK was pressed, so Alto should restart. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # noinspection PyTypeChecker
>>> UpdateDialog(
...     None,
...     command=(
...         "uv",
...         ["tool", "install", "alto"],
...     ),
... ).succeeded
False
```

## UpdateDialog.reject

<div class="api-signature" markdown="1">

```python
def reject() -> None
```

{% endraw %}{% include api-source.html name="UpdateDialog.reject" line=926 %}{% raw %}

</div>

Close the window, but not while the update is running.

## UpdateDialog.closeEvent

<div class="api-signature" markdown="1">

```python
def closeEvent(event: QCloseEvent) -> None
```

{% endraw %}{% include api-source.html name="UpdateDialog.closeEvent" line=931 %}{% raw %}

</div>

Refuse to close while the update is running.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QCloseEvent` | The request to close. |
{% endraw %}
