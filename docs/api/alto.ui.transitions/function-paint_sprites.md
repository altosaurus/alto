---
title: paint_sprites
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-paint_sprites/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def paint_sprites(
    painter: QPainter,
    *,
    sprites: Sequence[Sprite],
) -> None
```

{% endraw %}{% include api-source.html name="paint_sprites" line=1560 %}{% raw %}

</div>

Draw sprites as they now look.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `painter` | `QPainter` | The painter to draw with. |
| `sprites` | `sequence of Sprite` | The sprites, drawn in order. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     20, 20, QImage.Format.Format_ARGB32
... )
>>> brush = QPainter(image)
>>> paint_sprites(
...     brush,
...     sprites=[
...         Sprite(
...             pixmap=QPixmap(10, 10),
...             rect=QRectF(0, 0, 10, 10),
...         )
...     ],
... )
>>> brush.end()
True
```
{% endraw %}
