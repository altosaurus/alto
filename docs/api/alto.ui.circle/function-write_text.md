---
title: write_text
parent: alto.ui.circle
api_module: alto.ui.circle
package: alto.ui
permalink: /api/alto.ui.circle/function-write_text/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def write_text(
    p: QPainter,
    *,
    center: QPointF,
    text: str,
    pixels: float,
    weight: QFont.Weight,
    color: QColor,
    max_width: float | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="write_text" line=313 %}{% raw %}

</div>

Write a line of text centered on a point, with its sharps and flats
drawn as the notation font draws them.

The letters are in the app's own font. Its ♭ is the shape of a small
"b", though, and does not look like a flat sign, so
the sharps, flats and naturals are the glyphs of the notation style
that the staff is drawn in, sized to the letters.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `center` | `QPointF` | The middle of the line. Keyword-only. |
| `text` | `str` | What to write, such as "B♭m" or "F♯ major". Keyword-only. |
| `pixels` | `float` | The size of the letters. Keyword-only. |
| `weight` | `QFont.Weight` | How heavy they are. Keyword-only. |
| `color` | `QColor` | The color. Keyword-only. |
| `max_width` | `float or None, default None` | The widest the line may be. A longer line is written smaller to fit. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     120, 60, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("black"))
>>> painter = QPainter(image)
>>> write_text(
...     painter,
...     center=QPointF(60, 30),
...     text="B♭m",
...     pixels=24,
...     weight=QFont.Weight.Bold,
...     color=QColor("white"),
... )
>>> painter.end()
True
>>> any(
...     image.pixelColor(x, 30).lightness()
...     > 128
...     for x in range(20, 100)
... )
True
```
{% endraw %}
