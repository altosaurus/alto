---
title: draw_brace
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-draw_brace/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_brace(
    p: QPainter,
    *,
    font: str,
    x: float,
    y0: float,
    y1: float,
    color: QColor,
    width: float,
) -> bool
```

{% endraw %}{% include api-source.html name="draw_brace" line=938 %}{% raw %}

</div>

Draw the font's brace stretched between two heights, for a grand
staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `font` | `str` | A key of `_FILES`. Keyword-only. |
| `x` | `float` | The brace's right edge, in pixels. Keyword-only. |
| `y0` | `float` | The top, in pixels. Keyword-only. |
| `y1` | `float` | The bottom, in pixels. Keyword-only. |
| `color` | `QColor` | The color. Keyword-only. |
| `width` | `float` | How wide to draw it, in pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if it was drawn; False (and nothing is drawn) if the font has no usable brace. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> painter = QPainter(image)
>>> draw_brace(
...     painter,
...     font="bravura",
...     x=30,
...     y0=10,
...     y1=90,
...     color=QColor("black"),
...     width=12,
... )
True
>>> painter.end()
True
```
{% endraw %}
