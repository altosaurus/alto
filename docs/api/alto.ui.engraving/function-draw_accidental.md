---
title: draw_accidental
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-draw_accidental/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_accidental(
    p: QPainter,
    *,
    font: str,
    sign: int,
    x: float,
    y: float,
    gap: float,
    color: QColor,
    fit: float | None = None,
) -> float
```

{% endraw %}{% include api-source.html name="draw_accidental" line=849 %}{% raw %}

</div>

Draw a sharp, flat or natural with its left edge at a point.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `font` | `str` | A key of `_FILES`. Keyword-only. |
| `sign` | `int` | -2 for a double flat, -1 flat, 0 natural, 1 sharp or 2 double sharp. Keyword-only. |
| `x` | `float` | The glyph's left edge, in pixels. Keyword-only. |
| `y` | `float` | The glyph's reference line, in pixels. Keyword-only. |
| `gap` | `float` | The distance between staff lines in pixels. Keyword-only. |
| `color` | `QColor` | The color. Keyword-only. |
| `fit` | `float or None, default None` | If given, shrink the glyph to be no wider than this many pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The width drawn, in pixels. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> painter = QPainter(image)
>>> normal = draw_accidental(
...     painter,
...     font="bravura",
...     sign=1,
...     x=10,
...     y=50,
...     gap=16,
...     color=QColor("black"),
... )
>>> squeezed = draw_accidental(
...     painter,
...     font="bravura",
...     sign=1,
...     x=10,
...     y=50,
...     gap=16,
...     color=QColor("black"),
...     fit=5.0,
... )
>>> painter.end()
True
>>> squeezed <= 5.0 < normal
True
```
{% endraw %}
