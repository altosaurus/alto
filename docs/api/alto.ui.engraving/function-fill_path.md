---
title: fill_path
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-fill_path/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def fill_path(
    p: QPainter,
    *,
    path: QPainterPath,
    color: QColor,
) -> None
```

{% endraw %}{% include api-source.html name="fill_path" line=450 %}{% raw %}

</div>

Fill a path with a color and no outline.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `path` | `QPainterPath` | What to fill. Keyword-only. |
| `color` | `QColor` | The color. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     20, 20, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("white"))
>>> painter = QPainter(image)
>>> square = QPainterPath()
>>> square.addRect(QRectF(5, 5, 10, 10))
>>> fill_path(
...     painter,
...     path=square,
...     color=QColor("black"),
... )
>>> painter.end()
True
>>> image.pixelColor(10, 10).lightness() < 128
True
```
{% endraw %}
