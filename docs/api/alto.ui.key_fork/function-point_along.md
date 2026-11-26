---
title: point_along
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/function-point_along/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def point_along(
    points: list[QPointF],
    *,
    t: float,
) -> QPointF
```

{% endraw %}{% include api-source.html name="point_along" line=214 %}{% raw %}

</div>

Return the point a fraction of the way along a path made of short
straight pieces.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `points` | `list of QPointF` | The corners of the path; at least one. |
| `t` | `float` | How far along, from 0 (the first point) to 1 (the last). Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QPointF` | The point that far along. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> point_along(
...     [
...         QPointF(0, 0),
...         QPointF(10, 0),
...         QPointF(10, 10),
...     ],
...     t=0.75,
... ).toTuple()
(10.0, 5.0)
>>> point_along(
...     [QPointF(0, 0), QPointF(3, 4)], t=0.5
... ).toTuple()  # slanting pieces are measured along their length
(1.5, 2.0)
```
{% endraw %}
