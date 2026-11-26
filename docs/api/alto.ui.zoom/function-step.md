---
title: step
parent: alto.ui.zoom
api_module: alto.ui.zoom
package: alto.ui
permalink: /api/alto.ui.zoom/function-step/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def step(direction: int) -> bool
```

{% endraw %}{% include api-source.html name="step" line=290 %}{% raw %}

</div>

Zoom in or out by one step.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `direction` | `int` | Positive to zoom in, negative to zoom out. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the zoom changed, False at the largest or smallest step. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> step(1), percent()
(True, 110)
>>> step(-1), percent()
(True, 100)
>>> while step(-1):
...     pass
>>> percent(), step(-1)
(50, False)
>>> reset(), percent()
(True, 100)
```
{% endraw %}
