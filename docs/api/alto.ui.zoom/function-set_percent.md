---
title: set_percent
parent: alto.ui.zoom
api_module: alto.ui.zoom
package: alto.ui
permalink: /api/alto.ui.zoom/function-set_percent/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_percent(value: int) -> bool
```

{% endraw %}{% include api-source.html name="set_percent" line=254 %}{% raw %}

</div>

Zoom to the step nearest a percentage, save it and say so.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `int` | The percentage wanted. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the zoom changed, False if it was already there. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_percent(125)
True
>>> percent(), factor()
(125, 1.25)
>>> set_percent(125)
False
>>> set_percent(100)
True
```
{% endraw %}
