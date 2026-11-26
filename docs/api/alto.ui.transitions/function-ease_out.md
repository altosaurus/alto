---
title: ease_out
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-ease_out/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ease_out(progress: float) -> float
```

{% endraw %}{% include api-source.html name="ease_out" line=146 %}{% raw %}

</div>

Ease a progress from 0 to 1 so that it starts fast and slows to a
stop.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `progress` | `float` | How far along, from 0 to 1. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The eased progress. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ease_out(0.0), ease_out(1.0), ease_out(0.5)
(0.0, 1.0, 0.875)
```
{% endraw %}
