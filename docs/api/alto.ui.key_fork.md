---
title: alto.ui.key_fork
parent: api
package: alto.ui
order: 30
permalink: /api/alto.ui.key_fork/
---
{% raw %}
The fork: a picker for a key signature, shaped like a tuning fork lying on its side.

The stem on the left ends in a natural sign (no sharps or flats, C major). At the right the stem opens into two tines:
the top one has the sharps, 1 to 7, and the bottom one the flats, 1 to 7. A circle marks the chosen signature. Click a
number to choose it, or turn the mouse wheel to move the circle along the fork.

**Examples**

```pycon
>>> fork = KeyFork()
>>> fork.set_value(-3)
>>> fork.value
-3
```

## node_position

```python
def node_position(value: int) -> QPointF
```

Return where a signature sits on the fork.

**Parameters**

- `value` (*int*): The signature: that many sharps if positive (top tine), flats if negative (bottom tine), 0 for the stem's end.

**Returns**

- *QPointF*: The centre of its number, in the widget's coordinates.

**Examples**

```pycon
>>> node_position(0).x() < node_position(1).x() < node_position(2).x()
True
>>> node_position(3).y() < node_position(0).y() < node_position(-3).y()
True
```

## route

```python
def route(value: int) -> list[QPointF]
```

Return the way along the fork from the end of the stem to a signature.

**Parameters**

- `value` (*int*): The signature, as for `node_position`.

**Returns**

- *list of QPointF*: The points to pass through: the stem's end, round the bend of the U to the tine and then each number up to the one asked.

**Examples**

```pycon
>>> len(route(0)), len(route(2)) > len(route(1)) > len(route(0))
(1, True)
>>> route(-1)[-1] == node_position(-1)
True
>>> round(route(3)[1].x()) == round(APEX_X)  # it leaves the stem at the apex of the U
True
```

## path_between

```python
def path_between(
    a: int,
    *,
    b: int,
) -> list[QPointF]
```

Return the way along the fork from one signature to another.

The circle goes back along the tine it is on, round the U and out along the other, never across the gap between the tines.

**Parameters**

- `a` (*int*): The signature to start from.
- `b` (*int*): The signature to end at. Keyword-only.

**Returns**

- *list of QPointF*: The points to pass through, from `a` to `b`.

**Examples**

```pycon
>>> path_between(2, b=2) == [node_position(2)]
True
>>> path_between(1, b=-1)[0] == node_position(1) and path_between(1, b=-1)[-1] == node_position(-1)
True
>>> any(abs(p.x() - APEX_X) < 1e-9 for p in path_between(1, b=-1))  # it goes round the U, through its apex
True
```

## point_along

```python
def point_along(
    points: list[QPointF],
    *,
    t: float,
) -> QPointF
```

Return the point a fraction of the way along a path made of short straight pieces.

**Parameters**

- `points` (*list of QPointF*): The corners of the path; at least one.
- `t` (*float*): How far along, from 0 (the first point) to 1 (the last). Keyword-only.

**Returns**

- *QPointF*: The point that far along.

**Examples**

```pycon
>>> point_along([QPointF(0, 0), QPointF(10, 0), QPointF(10, 10)], t=0.75).toTuple()
(10.0, 5.0)
>>> point_along([QPointF(0, 0), QPointF(3, 4)], t=0.5).toTuple()  # slanting pieces are measured along their length
(1.5, 2.0)
```

## fork_path

```python
def fork_path() -> QPainterPath
```

Return the outline of the fork: the stem, a half circle for the U, and the two tines.

**Returns**

- *QPainterPath*: One smooth line, drawn from the end of the stem.

**Examples**

```pycon
>>> outline = fork_path()
>>> outline.boundingRect().left() == STEM_X and outline.boundingRect().top() == TOP_Y
True
```

## draw_natural

```python
def draw_natural(
    p: QPainter,
    *,
    center: QPointF,
    height: float,
    color: QColor,
) -> None
```

Draw a natural sign: two upright lines joined by two slanting bars.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `center` (*QPointF*): The middle of the sign. Keyword-only.
- `height` (*float*): How tall it is, in pixels. Keyword-only.
- `color` (*QColor*): The colour of the lines. Keyword-only.

**Examples**

```pycon
>>> from PySide6.QtGui import QPixmap
>>> canvas = QPixmap(20, 20)
>>> painter = QPainter(canvas)
>>> draw_natural(painter, center=QPointF(10, 10), height=14, color=QColor("black"))
>>> _ = painter.end()
```

## KeyFork

```python
KeyFork(
    *,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

A tuning fork on its side, for choosing how many sharps or flats a key signature has.

**Attributes**

- `value` (*int*): The chosen signature: sharps if positive, flats if negative, 0 for none.
- `locked` (*bool*): While True the fork ignores the mouse and the keyboard.
- `changed` (*Signal*): Emitted with the new `value` whenever it changes.

**Examples**

```pycon
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

```pycon
>>> KeyFork().value
0
```

### KeyFork.set_value

```python
def set_value(
    value: int,
    *,
    slide: bool = True,
) -> None
```

Choose a signature and move the circle to it.

**Parameters**

- `value` (*int*): The signature, kept between 7 flats and 7 sharps.
- `slide` (*bool, default True*): Move the circle along the fork; if False it jumps. Keyword-only.

**Examples**

```pycon
>>> fork = KeyFork()
>>> fork.set_value(99)
>>> fork.value
7
>>> fork.set_value(0, slide=False)
>>> fork.value, fork._marker == node_position(0)
(0, True)
```

### KeyFork.set_marker_color

```python
def set_marker_color(color: QColor | None) -> None
```

Colour the circle, for a right or wrong answer.

**Parameters**

- `color` (*QColor or None*): The colour to use, or None for the highlight colour.

**Examples**

```pycon
>>> fork = KeyFork()
>>> fork.set_marker_color(QColor("#2e7d32"))
>>> fork._marker_color == QColor("#2e7d32")
True
```

### KeyFork.value_at

```python
@staticmethod
def value_at(point: QPointF) -> int | None
```

Return the signature whose number is under a point.

**Parameters**

- `point` (*QPointF*): A position in the widget.

**Returns**

- *int or None*: The signature there, or None if the point is not near a number.

**Examples**

```pycon
>>> fork = KeyFork()
>>> fork.value_at(node_position(3)), fork.value_at(node_position(-4)), fork.value_at(node_position(0))
(3, -4, 0)
>>> fork.value_at(QPointF(5, 130)) is None
True
```

### KeyFork.mousePressEvent

```python
def mousePressEvent(event: QMouseEvent) -> None
```

Choose the number that was clicked.

**Parameters**

- `event` (*QMouseEvent*): The press. Only the left button does anything.

**Examples**

```pycon
>>> from PySide6.QtCore import QEvent
>>> fork = KeyFork()
>>> point = node_position(-2)
>>> fork.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.LeftButton,
...                                  Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
>>> fork.value
-2
```

### KeyFork.wheelEvent

```python
def wheelEvent(event: QWheelEvent) -> None
```

Move the circle one number along the fork for each notch of the wheel.

Rolling up goes towards more sharps and down towards more flats, passing through the natural sign.

**Parameters**

- `event` (*QWheelEvent*): The wheel turn.

**Examples**

```pycon
>>> from PySide6.QtCore import QPoint
>>> fork = KeyFork()
>>> point = QPointF(100, 50)
>>> fork.wheelEvent(QWheelEvent(point, point, QPoint(0, 0), QPoint(0, -120), Qt.MouseButton.NoButton,
...                             Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False))
>>> fork.value
-1
```

### KeyFork.keyPressEvent

```python
def keyPressEvent(event: QKeyEvent) -> None
```

Move the circle with the arrow keys: up or right for a sharp, down or left for a flat.

**Parameters**

- `event` (*QKeyEvent*): The key press.

**Examples**

```pycon
>>> from PySide6.QtCore import QEvent
>>> fork = KeyFork()
>>> fork.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier))
>>> fork.value
1
```

### KeyFork.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw the fork, its numbers and the circle on the chosen one.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```pycon
>>> KeyFork().grab().isNull()
False
```
{% endraw %}
