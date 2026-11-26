---
title: draw_clef
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-draw_clef/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_clef(
    p: QPainter,
    *,
    font: str,
    clef: str,
    x: float,
    bottom: float,
    gap: float,
    color: QColor,
) -> None
```

{% endraw %}{% include api-source.html name="draw_clef" line=738 %}{% raw %}

</div>

Draw a clef with its left edge at a point.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `font` | `str` | A key of `_FILES`. Keyword-only. |
| `clef` | `str` | "treble", "bass", "alto", "tenor", "soprano", "mezzo", "baritone_c" or "baritone_f". Keyword-only. |
| `x` | `float` | The clef's left edge, in pixels. Keyword-only. |
| `bottom` | `float` | The y position of the staff's bottom line, in pixels. Keyword-only. |
| `gap` | `float` | The distance between staff lines in pixels. Keyword-only. |
| `color` | `QColor` | The color. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("white"))
>>> painter = QPainter(image)
>>> draw_clef(
...     painter,
...     font="bravura",
...     clef="treble",
...     x=10,
...     bottom=70,
...     gap=10,
...     color=QColor("black"),
... )
>>> painter.end()
True
>>> any(
...     image.pixelColor(x_, y).lightness()
...     < 128
...     for x_ in range(10, 40)
...     for y in range(20, 90)
... )
True
```
{% endraw %}
