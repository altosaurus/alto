---
title: draw_note
parent: alto.ui.notes
api_module: alto.ui.notes
package: alto.ui
permalink: /api/alto.ui.notes/function-draw_note/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_note(
    p: QPainter,
    *,
    value: str,
    x: float,
    y: float,
    gap: float,
    color: QColor,
    stem_down: bool = False,
) -> None
```

{% endraw %}{% include api-source.html name="draw_note" line=358 %}{% raw %}

</div>

Draw a note with its head centered on a point, in Noto Music.

The note is drawn from the Noto Music font, so it is only drawn as
it should be where that font is installed. The staff
draws with Bravura, which comes with Alto, wherever Noto Music is
missing.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | The painter to draw with. |
| `value` | `str` | The note value. Keyword-only. |
| `x` | `float` | The head's center, in pixels. Keyword-only. |
| `y` | `float` | The head's center, in pixels. Keyword-only. |
| `gap` | `float` | The distance between staff lines, which is also the head's height. Keyword-only. |
| `color` | `QColor` | The color to draw in. Keyword-only. |
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
...     value="quarter",
...     x=50,
...     y=50,
...     gap=16,
...     color=QColor("black"),
... )
>>> painter.end()
True
>>> from PySide6.QtGui import QFontDatabase
>>> not QFontDatabase.hasFamily(
...     "Noto Music"
... ) or image.pixelColor(
...     50, 50
... ).lightness() < 128  # the head is at the point
True
```
{% endraw %}
