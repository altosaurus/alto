---
title: draw_key_signature
parent: alto.ui.staff
api_module: alto.ui.staff
package: alto.ui
permalink: /api/alto.ui.staff/function-draw_key_signature/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_key_signature(
    p: QPainter,
    *,
    clef: str,
    key: int,
    x: float,
    bottom: float,
    gap: float,
    color: QColor,
    step: float = KEY_STEP,
    size: float = 2.0,
    font: str | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="draw_key_signature" line=219 %}{% raw %}

</div>

Draw the sharps or flats of a key signature, left to right.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `clef` | `str` | The clef, which decides where on the staff each accidental goes. Keyword-only. |
| `key` | `int` | The key signature: that many sharps if positive, flats if negative; nothing is drawn for 0. Keyword-only. |
| `x` | `float` | The left edge of the first accidental, in pixels. Keyword-only. |
| `bottom` | `float` | The y position of the staff's bottom line, in pixels. Keyword-only. |
| `gap` | `float` | The distance between staff lines, in pixels. Keyword-only. |
| `color` | `QColor` | The color to draw in. Keyword-only. |
| `step` | `float, default KEY_STEP` | The horizontal spacing between accidentals. Keyword-only. |
| `size` | `float, default 2.0` | The size of the built-in characters, in staff gaps. Keyword-only. |
| `font` | `str or None, default None` | A SMuFL font to engrave them in; None uses the built-in sharp and flat characters. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     200, 120, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("white"))
>>> painter = QPainter(image)
>>> draw_key_signature(
...     painter,
...     clef="treble",
...     key=3,
...     x=10,
...     bottom=80,
...     gap=12,
...     color=QColor("black"),
...     font="bravura",
... )
>>> painter.end()
True
>>> any(
...     image.pixelColor(x_, y_).lightness()
...     < 128
...     for x_ in range(10, 60)
...     for y_ in range(20, 100)
... )
True
```
{% endraw %}
