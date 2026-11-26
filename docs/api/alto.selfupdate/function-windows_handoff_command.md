---
title: windows_handoff_command
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-windows_handoff_command/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def windows_handoff_command(
    installer: Path,
    *,
    pid: int,
    alto: Path,
) -> list[str]
```

{% endraw %}{% include api-source.html name="windows_handoff_command" line=675 %}{% raw %}

</div>

Give the command that waits for Alto to end, runs the installer, and
starts the old Alto again if the installer fails.

The installer must not start while Alto is still closing: it would
find Alto's files in use and, with no one to answer, give
up. So Alto starts this command and quits, and the command waits for
Alto's process to be gone before it begins.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `installer` | `Path` | The downloaded installer. |
| `pid` | `int` | Alto's process, which is waited for (for at most a minute). Keyword-only. |
| `alto` | `Path` | The installed `alto.exe`, which is started again if the installer fails, so that the person is not left with no Alto. When it succeeds, the installer starts Alto itself (`/RELAUNCH=1`). Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The program and its arguments. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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
```
{% endraw %}
