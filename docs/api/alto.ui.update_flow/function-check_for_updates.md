---
title: check_for_updates
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-check_for_updates/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def check_for_updates(
    parent: QWidget,
    *,
    restart: Callable[[], None],
    quit_app: Callable[[], None] = QApplication.quit,
) -> None
```

{% endraw %}{% include api-source.html name="check_for_updates" line=998 %}{% raw %}

</div>

Ask whether a newer Alto is available and, if the person agrees,
install it and restart.

What is asked depends on the copy: one run from a source folder is
told how it is updated; a packaged copy asks for the
latest release and is offered its download page; one installed with
the script follows what Settings says, the latest release
or the main branch, and can install it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | The window the questions are asked over. |
| `restart` | `Callable` | What to do after a successful update to start the new version in place of this one. Keyword-only. |
| `quit_app` | `Callable, default QApplication.quit` | What to do to close Alto once an update has been handed to the program that installs it, which is how a packaged copy is replaced. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> check_for_updates  # doctest: +SKIP
```
{% endraw %}
