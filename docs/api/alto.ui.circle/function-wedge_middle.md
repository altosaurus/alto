---
title: wedge_middle
parent: alto.ui.circle
api_module: alto.ui.circle
package: alto.ui
permalink: /api/alto.ui.circle/function-wedge_middle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def wedge_middle(
    *,
    center: QPointF,
    radius: float,
    index: int,
) -> QPointF
```

{% endraw %}{% include api-source.html name="wedge_middle" line=180 %}{% raw %}

</div>

Return the point in the middle of a wedge, at a given distance from
the center.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `center` | `QPointF` | The middle of the circle. |
| `radius` | `float` | How far out, in pixels. Keyword-only. |
| `index` | `int` | Which wedge, clockwise from the top. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QPointF` | The point. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> wedge_middle(
...     center=QPointF(100, 100),
...     radius=50,
...     index=0,
... ).toTuple()  # straight up
(100.0, 50.0)
>>> round(
...     wedge_middle(
...         center=QPointF(100, 100),
...         radius=50,
...         index=3,
...     ).x()
... )  # a quarter of the way around: to the right
150
```
{% endraw %}
