---
title: nice_ticks
parent: alto.ui.charts
api_module: alto.ui.charts
package: alto.ui
permalink: /api/alto.ui.charts/function-nice_ticks/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def nice_ticks(
    top: float,
    *,
    count: int = 4,
) -> list[float]
```

{% endraw %}{% include api-source.html name="nice_ticks" line=82 %}{% raw %}

</div>

Return round tick values from 0 up to just above a top value.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `top` | `float` | The largest value to show. |
| `count` | `int, default 4` | Roughly how many ticks to aim for. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of float` | Ticks at round steps (1, 2, 2.5, 5 or 10 times a power of ten), starting at 0 and reaching at least `top`. Just 0 and 1 when `top` is not positive. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> nice_ticks(13)
[0, 5, 10, 15]
>>> nice_ticks(8)[-1] >= 8
True
>>> nice_ticks(0)
[0.0, 1.0]
```
{% endraw %}
