---
title: draw_natural
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/function-draw_natural/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_natural(
    p: QPainter,
    *,
    center: QPointF,
    height: float,
    color: QColor,
) -> None
```

{% endraw %}{% include api-source.html name="draw_natural" line=354 %}{% raw %}

</div>

Draw a natural sign: two upright lines joined by two slanting bars.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `center` | `QPointF` | The middle of the sign. Keyword-only. |
| `height` | `float` | How tall it is, in pixels. Keyword-only. |
| `color` | `QColor` | The color of the lines. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QPixmap
>>> canvas = QPixmap(20, 20)
>>> painter = QPainter(canvas)
>>> draw_natural(
...     painter,
...     center=QPointF(10, 10),
...     height=14,
...     color=QColor("black"),
... )
>>> _ = painter.end()
```
{% endraw %}
