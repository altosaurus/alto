---
title: update_package
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-update_package/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def update_package(
    parent: QWidget,
    *,
    release: updates.Release,
    target: selfupdate.Target,
    quit_app: Callable[[], None],
) -> None
```

{% endraw %}{% include api-source.html name="update_package" line=1320 %}{% raw %}

</div>

Replace a packaged copy after the user agrees: download and check
it, say that Alto will restart, and hand over.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | The window the questions are asked over. |
| `release` | `updates.Release` | The newer release. Keyword-only. |
| `target` | `selfupdate.Target` | The copy that will be replaced. Keyword-only. |
| `quit_app` | `Callable` | What to do to close Alto once the update has been handed to the program that installs it. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> update_package  # doctest: +SKIP
```
{% endraw %}
