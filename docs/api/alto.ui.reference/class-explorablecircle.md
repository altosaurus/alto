---
title: ExplorableCircle
parent: alto.ui.reference
api_module: alto.ui.reference
package: alto.ui
permalink: /api/alto.ui.reference/class-explorablecircle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ExplorableCircle(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ExplorableCircle" line=96 %}{% raw %}

</div>

Bases: `FifthsCircle`

A circle of fifths that shows every key and lets you pick one.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cell` | `tuple of (str, int) or None` | The cell that is picked: its ring ("outer" or "inner") and its place clockwise from the top; None for none. |
| `hover` | `tuple of (str, int) or None` | The cell under the pointer. |
| `interactive` | `bool` | Whether the circle answers the mouse and the keys. A picture of the circle that only the program changes has it off. |
| `picked` | `Signal` | Emitted with the ring and place when a cell is picked, or with "" and -1 when the pick is cleared. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.cell, circle.title
(None, 'Circle of fifths')
```

**Constructor**

Build the circle with every key named and none picked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ExplorableCircle().shown["inner"] == set(
...     range(12)
... )
True
```

## ExplorableCircle.set_interactive

<div class="api-signature" markdown="1">

```python
def set_interactive(interactive: bool) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.set_interactive" line=149 %}{% raw %}

</div>

Let the circle be clicked and moved with the keys, or make it a
picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `interactive` | `bool` | True to answer the mouse and the keys. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.set_interactive(False)
>>> (
...     circle.interactive,
...     circle.focusPolicy()
...     == Qt.FocusPolicy.NoFocus,
... )
(False, True)
```

## ExplorableCircle.clear

<div class="api-signature" markdown="1">

```python
def clear() -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.clear" line=178 %}{% raw %}

</div>

Pick nothing: every key is named, none is lit and the middle
says what to do.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.select("outer", place=4)
>>> circle.clear()
>>> circle.cell, circle.signature, circle.lit
(None, None, set())
```

## ExplorableCircle.select

<div class="api-signature" markdown="1">

```python
def select(
    ring: str,
    *,
    place: int,
) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.select" line=206 %}{% raw %}

</div>

Pick a cell: light the chords of its key, and show its name and
key signature in the middle.

A minor key has the key signature, and the chords, of its
relative major.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ring` | `str` | "outer" for the major key at the place, "inner" for its relative minor. |
| `place` | `int` | The place, clockwise from the top. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.select("inner", place=3)
>>> (
...     circle.title,
...     circle.subtitle,
...     sorted(circle.lit),
...     circle.numerals[("outer", 4)],
... )
('F♯ minor', '3 sharps', [2, 3, 4], 'V')
```

## ExplorableCircle.cell_at

<div class="api-signature" markdown="1">

```python
def cell_at(point: QPointF) -> tuple[str, int] | None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.cell_at" line=265 %}{% raw %}

</div>

Return the cell under a point.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `point` | `QPointF` | A position in the widget. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (str, int) or None` | The ring and place, or None for the middle disc or outside the circle. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.resize(400, 400)
>>> middle, size = circle.geometry_of()
>>> circle.cell_at(
...     QPointF(
...         middle.x(), middle.y() - 0.9 * size
...     )
... )
('outer', 0)
>>> circle.cell_at(
...     QPointF(
...         middle.x() + 0.6 * size, middle.y()
...     )
... )
('inner', 3)
>>> circle.cell_at(middle) is None
True
```

## ExplorableCircle.lift_of

<div class="api-signature" markdown="1">

```python
def lift_of(
    ring: str,
    *,
    place: int,
) -> float
```

{% endraw %}{% include api-source.html name="ExplorableCircle.lift_of" line=309 %}{% raw %}

</div>

Return how bright a cell is drawn: as for any question, and a
little brighter under the pointer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ring` | `str` | "outer" or "inner". |
| `place` | `int` | The place clockwise from the top. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The brightness, from 0 to 1. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.hover = ("outer", 5)
>>> (
...     circle.lift_of("outer", place=5),
...     circle.lift_of("outer", place=6),
... )
(0.2, 0.0)
```

## ExplorableCircle.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.mousePressEvent" line=344 %}{% raw %}

</div>

Pick the cell that is clicked; a click in the middle clears the
pick.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The click. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPoint
>>> from PySide6.QtTest import QTest
>>> circle = ExplorableCircle()
>>> circle.resize(400, 400)
>>> center, radius = circle.geometry_of()
>>> QTest.mouseClick(
...     circle,
...     Qt.MouseButton.LeftButton,
...     pos=QPoint(
...         int(center.x()),
...         int(center.y() - 0.9 * radius),
...     ),
... )
>>> circle.cell
('outer', 0)
```

## ExplorableCircle.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.mouseMoveEvent" line=381 %}{% raw %}

</div>

Light the cell under the pointer, and show a hand over the ones
that can be picked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPoint
>>> from PySide6.QtTest import QTest
>>> circle = ExplorableCircle()
>>> circle.resize(400, 400)
>>> circle.show()
>>> center, radius = circle.geometry_of()
>>> QTest.mouseMove(
...     circle,
...     QPoint(
...         int(center.x()),
...         int(center.y() - 0.9 * radius),
...     ),
... )
>>> circle.hover
('outer', 0)
```

## ExplorableCircle.leaveEvent

<div class="api-signature" markdown="1">

```python
def leaveEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.leaveEvent" line=413 %}{% raw %}

</div>

Stop lighting a cell once the pointer has left.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QEvent` | The event. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.hover = ("outer", 1)
>>> circle.leaveEvent(QEvent(QEvent.Type.Leave))
>>> circle.hover is None
True
```

## ExplorableCircle.keyPressEvent

<div class="api-signature" markdown="1">

```python
def keyPressEvent(event: QKeyEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.keyPressEvent" line=462 %}{% raw %}

</div>

Move the pick with the arrow keys: Left and Right around the
circle, Up and Down between the rings.

Escape clears the pick, and Home picks C major.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QKeyEvent` | The key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> press = QKeyEvent(
...     QKeyEvent.Type.KeyPress,
...     Qt.Key.Key_Right,
...     Qt.KeyboardModifier.NoModifier,
... )
>>> circle.keyPressEvent(press)
>>> circle.cell
('outer', 0)
>>> circle.keyPressEvent(press)
>>> circle.cell
('outer', 1)
```
{% endraw %}
