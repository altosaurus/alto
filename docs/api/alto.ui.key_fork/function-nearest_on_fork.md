---
title: nearest_on_fork
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/function-nearest_on_fork/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def nearest_on_fork(point: QPointF) -> QPointF
```

{% endraw %}{% include api-source.html name="nearest_on_fork" line=258 %}{% raw %}

</div>

Return the point on the fork's line that is closest to a point.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `point` | `QPointF` | Any position in the widget, such as the mouse while the circle is dragged. |

**Returns**

| Type | Description |
| --- | --- |
| `QPointF` | The closest point on the way from the last sharp, around the U, to the last flat. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> nearest_on_fork(
...     QPointF(node_position(2).x(), 0)
... ) == node_position(
...     2
... )  # straight above the number
True
>>> nearest_on_fork(
...     QPointF(-50, node_position(0).y())
... ) == node_position(
...     0
... )  # past the end of the stem
True
```
{% endraw %}
