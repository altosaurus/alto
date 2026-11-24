---
title: alto.ui.key_fork
parent: api
package: alto.ui
permalink: /api/alto.ui.key_fork/
---
{% raw %}
The fork: a picker for a key signature, shaped like a tuning fork lying
on its side.

The stem on the left ends in a natural sign (no sharps or flats, C
major). At the right the stem opens into two tines:
the top one has the sharps, 1 to 7, and the bottom one the flats, 1 to
7. A circle marks the chosen signature. Click a
number to choose it, drag the circle along the fork, or turn the mouse
wheel to move it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> fork.set_value(-3)
>>> fork.value
-3
```

## node_position

<div class="api-signature" markdown="1">

```python
def node_position(value: int) -> QPointF
```

{% endraw %}{% include api-source.html name="node_position" line=86 %}{% raw %}

</div>

Return where a signature sits on the fork.

**Parameters**

- `value` (*int*): The signature: that many sharps if positive (top tine), flats if negative (bottom tine), 0 for the stem's end.

**Returns**

- *QPointF*: The center of its number, in the widget's coordinates.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> node_position(0).x() < node_position(
...     1
... ).x() < node_position(2).x()
True
>>> node_position(3).y() < node_position(
...     0
... ).y() < node_position(-3).y()
True
```

## route

<div class="api-signature" markdown="1">

```python
def route(value: int) -> list[QPointF]
```

{% endraw %}{% include api-source.html name="route" line=120 %}{% raw %}

</div>

Return the way along the fork from the end of the stem to a
signature.

**Parameters**

- `value` (*int*): The signature, as for `node_position`.

**Returns**

- *list of QPointF*: The points to pass through: the stem's end, around the bend of the U to the tine and then each number up to the one asked.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     len(route(0)),
...     len(route(2))
...     > len(route(1))
...     > len(route(0)),
... )
(1, True)
>>> route(-1)[-1] == node_position(-1)
True
>>> round(route(3)[1].x()) == round(
...     APEX_X
... )  # it leaves the stem at the apex of the U
True
```

## path_between

<div class="api-signature" markdown="1">

```python
def path_between(
    a: int,
    *,
    b: int,
) -> list[QPointF]
```

{% endraw %}{% include api-source.html name="path_between" line=170 %}{% raw %}

</div>

Return the way along the fork from one signature to another.

The circle goes back along the tine it is on, around the U and out
along the other, never across the gap between the tines.

**Parameters**

- `a` (*int*): The signature to start from.
- `b` (*int*): The signature to end at. Keyword-only.

**Returns**

- *list of QPointF*: The points to pass through, from `a` to `b`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> path_between(2, b=2) == [node_position(2)]
True
>>> path_between(1, b=-1)[0] == node_position(
...     1
... ) and path_between(1, b=-1)[
...     -1
... ] == node_position(-1)
True
>>> any(
...     abs(p.x() - APEX_X) < 1e-9
...     for p in path_between(1, b=-1)
... )  # it goes around the U, through its apex
True
```

## point_along

<div class="api-signature" markdown="1">

```python
def point_along(
    points: list[QPointF],
    *,
    t: float,
) -> QPointF
```

{% endraw %}{% include api-source.html name="point_along" line=214 %}{% raw %}

</div>

Return the point a fraction of the way along a path made of short
straight pieces.

**Parameters**

- `points` (*list of QPointF*): The corners of the path; at least one.
- `t` (*float*): How far along, from 0 (the first point) to 1 (the last). Keyword-only.

**Returns**

- *QPointF*: The point that far along.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> point_along(
...     [
...         QPointF(0, 0),
...         QPointF(10, 0),
...         QPointF(10, 10),
...     ],
...     t=0.75,
... ).toTuple()
(10.0, 5.0)
>>> point_along(
...     [QPointF(0, 0), QPointF(3, 4)], t=0.5
... ).toTuple()  # slanting pieces are measured along their length
(1.5, 2.0)
```

## nearest_on_fork

<div class="api-signature" markdown="1">

```python
def nearest_on_fork(point: QPointF) -> QPointF
```

{% endraw %}{% include api-source.html name="nearest_on_fork" line=258 %}{% raw %}

</div>

Return the point on the fork's line that is closest to a point.

**Parameters**

- `point` (*QPointF*): Any position in the widget, such as the mouse while the circle is dragged.

**Returns**

- *QPointF*: The closest point on the way from the last sharp, around the U, to the last flat.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> nearest_on_fork(
...     QPointF(node_position(2).x(), 0)
... ) == node_position(
...     2
... )  # straight above the number
True
>>> nearest_on_fork(
...     QPointF(-50, node_position(0).y())
... ) == node_position(
...     0
... )  # past the end of the stem
True
```

## fork_path

<div class="api-signature" markdown="1">

```python
def fork_path() -> QPainterPath
```

{% endraw %}{% include api-source.html name="fork_path" line=314 %}{% raw %}

</div>

Return the outline of the fork: the stem, a half circle for the U,
and the two tines.

**Returns**

- *QPainterPath*: One smooth line, drawn from the end of the stem.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> outline = fork_path()
>>> (
...     outline.boundingRect().left() == STEM_X
...     and outline.boundingRect().top() == TOP_Y
... )
True
```

## draw_natural

<div class="api-signature" markdown="1">

```python
def draw_natural(
    p: QPainter,
    *,
    center: QPointF,
    height: float,
    color: QColor,
) -> None
```

{% endraw %}{% include api-source.html name="draw_natural" line=354 %}{% raw %}

</div>

Draw a natural sign: two upright lines joined by two slanting bars.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `center` (*QPointF*): The middle of the sign. Keyword-only.
- `height` (*float*): How tall it is, in pixels. Keyword-only.
- `color` (*QColor*): The color of the lines. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QPixmap
>>> canvas = QPixmap(20, 20)
>>> painter = QPainter(canvas)
>>> draw_natural(
...     painter,
...     center=QPointF(10, 10),
...     height=14,
...     color=QColor("black"),
... )
>>> _ = painter.end()
```

## KeyFork

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

- `value` (*int*): The chosen signature: sharps if positive, flats if negative, 0 for none.
- `locked` (*bool*): While True the fork ignores the mouse and the keyboard.
- `changed` (*Signal*): Emitted with the new `value` whenever it changes.

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

- `parent` (*QWidget or None, default None*): The widget that owns the fork. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyFork().value
0
```

### KeyFork.set_value

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

- `value` (*int*): The signature, kept between 7 flats and 7 sharps.
- `slide` (*bool, default True*): Move the circle along the fork; if False it jumps. Keyword-only.

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

### KeyFork.set_marker_color

<div class="api-signature" markdown="1">

```python
def set_marker_color(color: QColor | None) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.set_marker_color" line=563 %}{% raw %}

</div>

Color the circle, for a right or wrong answer.

**Parameters**

- `color` (*QColor or None*): The color to use, or None for the highlight color.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> fork.set_marker_color(QColor("#2e7d32"))
>>> fork._marker_color == QColor("#2e7d32")
True
```

### KeyFork.value_at

<div class="api-signature" markdown="1">

```python
@staticmethod
def value_at(point: QPointF) -> int | None
```

{% endraw %}{% include api-source.html name="KeyFork.value_at" line=583 %}{% raw %}

</div>

Return the signature whose number is under a point.

**Parameters**

- `point` (*QPointF*): A position in the widget.

**Returns**

- *int or None*: The signature there, or None if the point is not near a number.

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

### KeyFork.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.mousePressEvent" line=617 %}{% raw %}

</div>

Pick up the circle if it was pressed, or choose the number that
was clicked.

**Parameters**

- `event` (*QMouseEvent*): The press. Only the left button does anything.

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

### KeyFork.mouseMoveEvent

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

- `event` (*QMouseEvent*): The move.

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

### KeyFork.mouseReleaseEvent

<div class="api-signature" markdown="1">

```python
def mouseReleaseEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.mouseReleaseEvent" line=734 %}{% raw %}

</div>

Let go of the circle, which slides to the number it is nearest.

**Parameters**

- `event` (*QMouseEvent*): The release.

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

### KeyFork.leaveEvent

<div class="api-signature" markdown="1">

```python
def leaveEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.leaveEvent" line=771 %}{% raw %}

</div>

Stop lighting a number when the mouse leaves the fork.

**Parameters**

- `event` (*QEvent*): The leave event.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> fork._hover = 3
>>> fork.leaveEvent(QEvent(QEvent.Type.Leave))
>>> fork._hover is None
True
```

### KeyFork.wheelEvent

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

- `event` (*QWheelEvent*): The wheel turn.

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

### KeyFork.keyPressEvent

<div class="api-signature" markdown="1">

```python
def keyPressEvent(event: QKeyEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.keyPressEvent" line=834 %}{% raw %}

</div>

Move the circle with the arrow keys: up or right for a sharp,
down or left for a flat.

**Parameters**

- `event` (*QKeyEvent*): The key press.

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

### KeyFork.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyFork.paintEvent" line=869 %}{% raw %}

</div>

Draw the fork, its numbers and the circle on the chosen one.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyFork().grab().isNull()
False
```
{% endraw %}
