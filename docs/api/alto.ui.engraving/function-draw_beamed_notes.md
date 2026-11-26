---
title: draw_beamed_notes
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-draw_beamed_notes/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_beamed_notes(
    p: QPainter,
    *,
    font: str,
    heads: list[QPointF],
    colors: list[QColor],
    gap: float,
    middle: float,
    ink: QColor,
    beams: int = 1,
) -> None
```

{% endraw %}{% include api-source.html name="draw_beamed_notes" line=622 %}{% raw %}

</div>

Draw a group with one beam for eighths or more for shorter notes.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | Score painter. |
| `font` | `str` | Selected SMuFL font. |
| `heads` | `list of QPointF` | Notehead centers in reading order. |
| `colors` | `list of QColor` | Ink for each notehead and its stem. |
| `gap` | `float` | Staff space in pixels. |
| `middle` | `float` | Height of the middle staff line, for choosing stem direction. |
| `ink` | `QColor` | Color of the shared beams. |
| `beams` | `int` | Number of beams for the written duration. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QPicture
>>> with QPainter(QPicture()) as painter:  # doctest: +SKIP
...     draw_beamed_notes(
...         painter, font="bravura", gap=8, middle=40,
...         heads=[QPointF(20, 48), QPointF(40, 44)],
...         colors=[QColor("black")] * 2, ink=QColor("black"),
...     )
```
{% endraw %}
