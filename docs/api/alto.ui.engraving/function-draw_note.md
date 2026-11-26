---
title: draw_note
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-draw_note/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_note(
    p: QPainter,
    *,
    font: str,
    value: str,
    x: float,
    y: float,
    gap: float,
    color: QColor,
    stem_down: bool = False,
    flag_color: QColor | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="draw_note" line=495 %}{% raw %}

</div>

Draw a note with its head centered on a point.

The head, then a stem and (for the short values) a flag, placed on
the font's anchors.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `font` | `str` | A key of `_FILES`. Keyword-only. |
| `value` | `str` | "breve", "whole", "half", "quarter", "eighth", "sixteenth" or "thirty_second". Keyword-only. |
| `x` | `float` | The head's center, in pixels. Keyword-only. |
| `y` | `float` | The head's center, in pixels. Keyword-only. |
| `gap` | `float` | The distance between staff lines in pixels. Keyword-only. |
| `color` | `QColor` | The color. Keyword-only. |
| `flag_color` | `QColor or None` | Optional highlight for the flag alone. Keyword-only. |
| `stem_down` | `bool, default False` | Draw the stem down. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("white"))
>>> painter = QPainter(image)
>>> draw_note(
...     painter,
...     font="bravura",
...     value="eighth",
...     x=50,
...     y=60,
...     gap=16,
...     color=QColor("black"),
... )
>>> painter.end()
True
>>> image.pixelColor(50, 60).lightness() < 128
True
```
{% endraw %}
