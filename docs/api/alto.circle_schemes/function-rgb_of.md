---
title: rgb_of
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-rgb_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def rgb_of(
    color: Hsl,
    *,
    capped: bool,
) -> tuple[float, float, float]
```

{% endraw %}{% include api-source.html name="rgb_of" line=222 %}{% raw %}

</div>

Turn a color into red, green and blue, keeping a dark circle's cells
from getting too bright.

Yellows and greens look far brighter than blues of the same
lightness, so on dark wedges a color that is brighter than
white names can stand is brought down to the limit.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `color` | `tuple of float` | The hue, saturation and lightness. |
| `capped` | `bool` | Whether to bring a too bright color down. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of float` | Red, green and blue, each from 0 to 1. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> r, g, b = rgb_of(
...     (60.0, 0.9, 0.5), capped=True
... )
>>> 0.299 * r + 0.587 * g + 0.114 * b <= MAX_BRIGHTNESS + 1e-9
True
>>> rgb_of((0.0, 0.0, 1.0), capped=False)
(1.0, 1.0, 1.0)
```
{% endraw %}
