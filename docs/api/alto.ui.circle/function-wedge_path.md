---
title: wedge_path
parent: alto.ui.circle
api_module: alto.ui.circle
package: alto.ui
permalink: /api/alto.ui.circle/function-wedge_path/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def wedge_path(
    *,
    center: QPointF,
    inner: float,
    outer: float,
    index: int,
) -> QPainterPath
```

{% endraw %}{% include api-source.html name="wedge_path" line=113 %}{% raw %}

</div>

Return the outline of one wedge of a ring.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `center` | `QPointF` | The middle of the circle. |
| `inner` | `float` | The radius of the wedge's inner edge, in pixels. Keyword-only. |
| `outer` | `float` | The radius of its outer edge. Keyword-only. |
| `index` | `int` | Which wedge: 0 is the one at the top and they go clockwise. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QPainterPath` | A closed shape, a piece of a ring 30 degrees wide. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> shape = wedge_path(
...     center=QPointF(100, 100),
...     inner=40,
...     outer=90,
...     index=0,
... )
>>> (
...     shape.contains(QPointF(100, 30)),
...     shape.contains(QPointF(100, 170)),
... )  # the top of the circle, and the bottom
(True, False)
```
{% endraw %}
