---
title: start
parent: alto.ui.warmup
api_module: alto.ui.warmup
package: alto.ui
permalink: /api/alto.ui.warmup/function-start/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def start(
    owner: QObject,
    *,
    steps: list[Callable[[], None]] | None = None,
    delay: int = START_DELAY_MS,
) -> None
```

{% endraw %}{% include api-source.html name="start" line=237 %}{% raw %}

</div>

Run the warm-up's steps one at a time, each when the event loop has
nothing else to do, beginning after a short delay.

Input and painting are handled between the steps, so the window
stays as responsive as it is without the warm-up. If the
owner is deleted first (the window closed), the rest of the steps
are dropped.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `owner` | `QObject` | What the warm-up belongs to, usually the main window. |
| `steps` | `list of callable or None, default None` | The steps; None for the usual ones (`warmup_steps()`). Keyword-only. |
| `delay` | `int, default START_DELAY_MS` | How long to wait first, in milliseconds. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> start(
...     QObject(), steps=[], delay=0
... )  # nothing to do
```
{% endraw %}
