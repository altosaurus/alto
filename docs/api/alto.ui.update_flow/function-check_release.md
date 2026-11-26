---
title: check_release
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-check_release/
---
{% raw %}
<div class="api-signature" markdown="1">

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

{% endraw %}{% include api-source.html name="check_release" line=1056 %}{% raw %}

</div>

Ask GitHub for the latest release and compare it with the version
that is running.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | The window the questions are asked over. |
| `kind` | `InstallKind` | What kind of copy is running: a packaged one is offered a download page, and one installed with the script is offered the update. Keyword-only. |
| `source` | `Source or None` | Where the running copy came from; None for a packaged copy. Keyword-only. |
| `restart` | `Callable` | What to do after a successful update. Keyword-only. |
| `quit_app` | `Callable` | What to do to close Alto once an update has been handed to the program that installs it. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> check_release  # doctest: +SKIP
```
{% endraw %}
