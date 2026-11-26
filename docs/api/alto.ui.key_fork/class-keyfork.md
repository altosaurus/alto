---
title: KeyFork
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/class-keyfork/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyFork(
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyFork" line=415 %}{% raw %}

</div>

Bases: `QWidget`

A tuning fork on its side, for choosing how many sharps or flats a
key signature has.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `value` | `int` | The chosen signature: sharps if positive, flats if negative, 0 for none. |
| `locked` | `bool` | While True the fork ignores the mouse and the keyboard. |
| `changed` | `Signal` | Emitted with the new `value` whenever it changes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> got = []
>>> _ = fork.changed.connect(got.append)
>>> fork.set_value(2)
>>> fork.set_value(2)  # no change, nothing said
>>> got
[2]
```

**Constructor**

Build the fork, set to no sharps or flats.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the fork. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyFork().value
0
```

## KeyFork.set_value

<div class="api-signature" markdown="1">

```python
def set_value(
    value: int,
    *,
    slide: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.set_value" line=498 %}{% raw %}

</div>

Choose a signature and move the circle to it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `int` | The signature, kept between 7 flats and 7 sharps. |
| `slide` | `bool, default True` | Move the circle along the fork; if False it jumps. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> fork.set_value(99)
>>> fork.value
7
>>> fork.set_value(0, slide=False)
>>> fork.value, fork._marker == node_position(0)
(0, True)
```

## KeyFork.set_marker_color

<div class="api-signature" markdown="1">

```python
def set_marker_color(color: QColor | None) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.set_marker_color" line=563 %}{% raw %}

</div>

Color the circle, for a right or wrong answer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `color` | `QColor or None` | The color to use, or None for the highlight color. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> fork.set_marker_color(QColor("#2e7d32"))
>>> fork._marker_color == QColor("#2e7d32")
True
```

## KeyFork.value_at

<div class="api-signature" markdown="1">

```python
@staticmethod
def value_at(point: QPointF) -> int | None
```

{% endraw %}{% include api-source.html name="KeyFork.value_at" line=583 %}{% raw %}

</div>

Return the signature whose number is under a point.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `point` | `QPointF` | A position in the widget. |

**Returns**

| Type | Description |
| --- | --- |
| `int or None` | The signature there, or None if the point is not near a number. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> (
...     fork.value_at(node_position(3)),
...     fork.value_at(node_position(-4)),
...     fork.value_at(node_position(0)),
... )
(3, -4, 0)
>>> fork.value_at(QPointF(5, 130)) is None
True
```

## KeyFork.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.mousePressEvent" line=617 %}{% raw %}

</div>

Pick up the circle if it was pressed, or choose the number that
was clicked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The press. Only the left button does anything. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> fork = KeyFork()
>>> point = node_position(-2)
>>> fork.mousePressEvent(
...     QMouseEvent(
...         QEvent.Type.MouseButtonPress,
...         point,
...         point,
...         Qt.MouseButton.LeftButton,
...         Qt.MouseButton.LeftButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> fork.value
-2
```

## KeyFork.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.mouseMoveEvent" line=663 %}{% raw %}

</div>

Carry the circle along the fork while it is held, and light the
number under the mouse otherwise.

The signature changes to the nearest number as the circle passes
it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> fork = KeyFork()
>>> here = node_position(0)
>>> there = node_position(3)
>>> fork.mousePressEvent(
...     QMouseEvent(
...         QEvent.Type.MouseButtonPress,
...         here,
...         here,
...         Qt.MouseButton.LeftButton,
...         Qt.MouseButton.LeftButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> fork.mouseMoveEvent(
...     QMouseEvent(
...         QEvent.Type.MouseMove,
...         there,
...         there,
...         Qt.MouseButton.NoButton,
...         Qt.MouseButton.LeftButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> fork.value
3
```

## KeyFork.mouseReleaseEvent

<div class="api-signature" markdown="1">

```python
def mouseReleaseEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.mouseReleaseEvent" line=734 %}{% raw %}

</div>

Let go of the circle, which slides to the number it is nearest.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The release. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> fork = KeyFork()
>>> fork._dragging = True
>>> fork._marker = node_position(0) + QPointF(
...     9, 0
... )
>>> fork.mouseReleaseEvent(
...     QMouseEvent(
...         QEvent.Type.MouseButtonRelease,
...         fork._marker,
...         fork._marker,
...         Qt.MouseButton.LeftButton,
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> fork._dragging
False
```

## KeyFork.leaveEvent

<div class="api-signature" markdown="1">

```python
def leaveEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.leaveEvent" line=771 %}{% raw %}

</div>

Stop lighting a number when the mouse leaves the fork.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QEvent` | The leave event. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> fork._hover = 3
>>> fork.leaveEvent(QEvent(QEvent.Type.Leave))
>>> fork._hover is None
True
```

## KeyFork.wheelEvent

<div class="api-signature" markdown="1">

```python
def wheelEvent(event: QWheelEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.wheelEvent" line=792 %}{% raw %}

</div>

Move the circle one number along the fork for each notch of the
wheel.

Rolling up goes toward more sharps and down toward more flats,
passing through the natural sign.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QWheelEvent` | The wheel turn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPoint
>>> fork = KeyFork()
>>> point = QPointF(100, 50)
>>> fork.wheelEvent(
...     QWheelEvent(
...         point,
...         point,
...         QPoint(0, 0),
...         QPoint(0, -120),
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...         Qt.ScrollPhase.NoScrollPhase,
...         False,
...     )
... )
>>> fork.value
-1
```

## KeyFork.keyPressEvent

<div class="api-signature" markdown="1">

```python
def keyPressEvent(event: QKeyEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.keyPressEvent" line=834 %}{% raw %}

</div>

Move the circle with the arrow keys: up or right for a sharp,
down or left for a flat.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QKeyEvent` | The key press. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> fork = KeyFork()
>>> fork.keyPressEvent(
...     QKeyEvent(
...         QEvent.Type.KeyPress,
...         Qt.Key.Key_Up,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> fork.value
1
```

## KeyFork.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.paintEvent" line=869 %}{% raw %}

</div>

Draw the fork, its numbers and the circle on the chosen one.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyFork().grab().isNull()
False
```
{% endraw %}
