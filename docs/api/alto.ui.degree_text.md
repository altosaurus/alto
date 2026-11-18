---
title: alto.ui.degree_text
parent: api
package: alto.ui
order: 35
permalink: /api/alto.ui.degree_text/
---
{% raw %}
Draw scale-degree carets above their digits without relying on font-specific combining accents.

**Examples**

```pycon
>>> button = DegreeButton("♭3̂")
>>> button.text()
'♭3̂'
```

## draw_degree_text

```python
def draw_degree_text(
    painter: QPainter,
    *,
    rect: QRectF,
    text: str,
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
) -> None
```

Draw text with each combining circumflex centered above its preceding digit.

**Parameters**

- `painter` (*QPainter*): The active painter, with the desired font and color.
- `rect` (*QRectF*): The rectangle in which to align the text. Keyword-only.
- `text` (*str*): The text, retaining combining circumflexes for copying and accessibility. Keyword-only.
- `alignment` (*Qt.AlignmentFlag, default AlignCenter*): Horizontal and vertical alignment. Keyword-only.

**Examples**

```pycon
>>> from PySide6.QtGui import QPixmap
>>> pixmap = QPixmap(100, 40)
>>> painter_ = QPainter(pixmap)
>>> draw_degree_text(painter_, rect=QRectF(0, 0, 100, 40), text="3̂")
>>> painter_.end()
True
```

## degree_tooltip

```python
def degree_tooltip(text: str) -> str
```

Render caret examples as an inline image for Qt's rich-text tooltip.

**Parameters**

- `text` (*str*): The tooltip text. Text without combining carets is returned unchanged.

**Returns**

- *str*: Plain text or HTML containing the explicitly centered carets.

**Examples**

```pycon
>>> degree_tooltip("Letters")
'Letters'
>>> "data:image/png;base64," in degree_tooltip("Caret (1̂ 2̂ 3̂)")
True
```

## DegreeButton

```python
class DegreeButton(QPushButton)
```

An answer button that draws scale-degree carets directly above the digits.

**Examples**

```pycon
>>> DegreeButton("2̂").text()
'2̂'
```

### DegreeButton.paintEvent

```python
def paintEvent(event: QPaintEvent) -> None
```

Keep the native button appearance and position degree accents explicitly.

**Parameters**

- `event` (*QPaintEvent*): The paint request.

**Examples**

```pycon
>>> DegreeButton("2̂").grab().isNull()
False
```

## DegreeCheckBox

```python
class DegreeCheckBox(QCheckBox)
```

Draw the scale degree caret centered above the checkbox label's digit.

### DegreeCheckBox.paintEvent

```python
def paintEvent(event: QPaintEvent) -> None
```

Paint the native checkbox and use the shared scale degree renderer for its label.

## DegreeLabel

```python
class DegreeLabel(QLabel)
```

A plain-text label with explicitly positioned scale-degree carets.

**Examples**

```pycon
>>> DegreeLabel("Note to place: 2̂ / 4").text()
'Note to place: 2̂ / 4'
```

### DegreeLabel.paintEvent

```python
def paintEvent(event: QPaintEvent) -> None
```

Paint degree labels with carets centered above their numbers.

**Parameters**

- `event` (*QPaintEvent*): The paint request.

**Examples**

```pycon
>>> DegreeLabel("2̂").grab().isNull()
False
```
{% endraw %}
