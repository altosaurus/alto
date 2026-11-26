---
title: px
parent: alto.ui.zoom
api_module: alto.ui.zoom
package: alto.ui
permalink: /api/alto.ui.zoom/function-px/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def px(value: float) -> int
```

{% endraw %}{% include api-source.html name="px" line=134 %}{% raw %}

</div>

Scale a length in pixels by the zoom.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `float` | The length at 100%. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The length now, rounded, and never less than one pixel unless it was zero. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> px(20), px(0), px(-4)
(20, 0, -4)
```
{% endraw %}
