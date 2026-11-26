---
title: draw_degree_text
parent: alto.ui.degree_text
api_module: alto.ui.degree_text
package: alto.ui
permalink: /api/alto.ui.degree_text/function-draw_degree_text/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_degree_text(
    painter: QPainter,
    *,
    rect: QRectF,
    text: str,
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
) -> None
```

{% endraw %}{% include api-source.html name="draw_degree_text" line=44 %}{% raw %}

</div>

Draw text with each combining circumflex centered above its
preceding digit.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `painter` | `QPainter` | The active painter, with the desired font and color. |
| `rect` | `QRectF` | The rectangle in which to align the text. Keyword-only. |
| `text` | `str` | The text, retaining combining circumflexes for copying and accessibility. Keyword-only. |
| `alignment` | `Qt.AlignmentFlag, default AlignCenter` | Horizontal and vertical alignment. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QPixmap
>>> pixmap = QPixmap(100, 40)
>>> painter_ = QPainter(pixmap)
>>> draw_degree_text(
...     painter_,
...     rect=QRectF(0, 0, 100, 40),
...     text="3̂",
... )
>>> painter_.end()
True
```
{% endraw %}
