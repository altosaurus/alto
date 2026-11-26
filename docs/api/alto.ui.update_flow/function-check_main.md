---
title: check_main
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-check_main/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def check_main(
    parent: QWidget,
    *,
    source: Source,
    restart: Callable[[], None],
) -> None
```

{% endraw %}{% include api-source.html name="check_main" line=1216 %}{% raw %}

</div>

Ask the address Alto came from for the newest commit on its main
branch and compare it with the one that is running.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | The window the questions are asked over. |
| `source` | `Source` | Where the running copy came from. Keyword-only. |
| `restart` | `Callable` | What to do after a successful update. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> check_main  # doctest: +SKIP
```
{% endraw %}
