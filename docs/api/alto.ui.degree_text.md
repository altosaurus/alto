---
title: alto.ui.degree_text
parent: api
package: alto.ui
permalink: /api/alto.ui.degree_text/
---
{% raw %}
Draw scale-degree carets above their digits without relying on
font-specific combining accents.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> button = DegreeButton("♭3̂")
>>> button.text()
'♭3̂'
```

## draw_degree_text

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

- `painter` (*QPainter*): The active painter, with the desired font and color.
- `rect` (*QRectF*): The rectangle in which to align the text. Keyword-only.
- `text` (*str*): The text, retaining combining circumflexes for copying and accessibility. Keyword-only.
- `alignment` (*Qt.AlignmentFlag, default AlignCenter*): Horizontal and vertical alignment. Keyword-only.

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

## degree_tooltip

<div class="api-signature" markdown="1">

```python
def degree_tooltip(text: str) -> str
```

{% endraw %}{% include api-source.html name="degree_tooltip" line=123 %}{% raw %}

</div>

Render caret examples as an inline image for Qt's rich-text tooltip.

**Parameters**

- `text` (*str*): The tooltip text. Text without combining carets is returned unchanged.

**Returns**

- *str*: Plain text or HTML containing the explicitly centered carets.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> degree_tooltip("Letters")
'Letters'
>>> "data:image/png;base64," in degree_tooltip(
...     "Caret (1̂ 2̂ 3̂)"
... )
True
```

## DegreeButton

<div class="api-signature" markdown="1">

```python
class DegreeButton(QPushButton)
```

{% endraw %}{% include api-source.html name="DegreeButton" line=182 %}{% raw %}

</div>

An answer button that draws scale-degree carets directly above the
digits.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeButton("2̂").text()
'2̂'
```

### DegreeButton.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="DegreeButton.paintEvent" line=193 %}{% raw %}

</div>

Keep the native button appearance and position degree accents
explicitly.

**Parameters**

- `event` (*QPaintEvent*): The paint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeButton("2̂").grab().isNull()
False
```

## DegreeCheckBox

<div class="api-signature" markdown="1">

```python
class DegreeCheckBox(QCheckBox)
```

{% endraw %}{% include api-source.html name="DegreeCheckBox" line=230 %}{% raw %}

</div>

Draw the scale degree caret centered above the checkbox label's
digit.

### DegreeCheckBox.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="DegreeCheckBox.paintEvent" line=236 %}{% raw %}

</div>

Paint the native checkbox and use the shared scale degree
renderer for its label.

## DegreeLabel

<div class="api-signature" markdown="1">

```python
class DegreeLabel(QLabel)
```

{% endraw %}{% include api-source.html name="DegreeLabel" line=270 %}{% raw %}

</div>

A plain-text label with explicitly positioned scale-degree carets.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeLabel("Note to place: 2̂ / 4").text()
'Note to place: 2̂ / 4'
```

### DegreeLabel.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="DegreeLabel.paintEvent" line=280 %}{% raw %}

</div>

Paint degree labels with carets centered above their numbers.

**Parameters**

- `event` (*QPaintEvent*): The paint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeLabel("2̂").grab().isNull()
False
```
{% endraw %}
