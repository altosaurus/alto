---
title: alto.ui.reference
parent: api
package: alto.ui
order: 44
permalink: /api/alto.ui.reference/
---
{% raw %}
The reference pane: an interactive circle of fifths to look things up on, with an explanation under it.

Click a key on either ring, or move with the arrow keys, and the circle lights that key's chords, shows its key signature in
the middle, and the text underneath explains it.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.select("outer", place=2)
>>> circle.title, circle.signature
('D major', 2)
```

## ExplorableCircle

```python
ExplorableCircle(parent: QWidget | None = None)
```

Bases: `FifthsCircle`

A circle of fifths that shows every key and lets you pick one.

**Attributes**

- `cell` (*tuple of (str, int) or None*): The cell that is picked: its ring ("outer" or "inner") and its place clockwise from the top; None for none.
- `hover` (*tuple of (str, int) or None*): The cell under the pointer.
- `interactive` (*bool*): Whether the circle answers the mouse and the keys. A picture of the circle that only the program changes has it off.
- `picked` (*Signal*): Emitted with the ring and place when a cell is picked, or with "" and -1 when the pick is cleared.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.cell, circle.title
(None, 'Circle of fifths')
```

**Constructor**

Build the circle with every key named and none picked.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> ExplorableCircle().shown["inner"] == set(range(12))
True
```

### ExplorableCircle.set_interactive

```python
def set_interactive(interactive: bool) -> None
```

Let the circle be clicked and moved with the keys, or make it a picture.

**Parameters**

- `interactive` (*bool*): True to answer the mouse and the keys.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.set_interactive(False)
>>> circle.interactive, circle.focusPolicy() == Qt.FocusPolicy.NoFocus
(False, True)
```

### ExplorableCircle.clear

```python
def clear() -> None
```

Pick nothing: every key is named, none is lit and the middle says what to do.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.select("outer", place=4)
>>> circle.clear()
>>> circle.cell, circle.signature, circle.lit
(None, None, set())
```

### ExplorableCircle.select

```python
def select(
    ring: str,
    *,
    place: int,
) -> None
```

Pick a cell: light the chords of its key, and show its name and key signature in the middle.

A minor key has the key signature, and the chords, of its relative major.

**Parameters**

- `ring` (*str*): "outer" for the major key at the place, "inner" for its relative minor.
- `place` (*int*): The place, clockwise from the top. Keyword-only.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.select("inner", place=3)
>>> circle.title, circle.subtitle, sorted(circle.lit), circle.numerals[("outer", 4)]
('F♯ minor', '3 sharps', [2, 3, 4], 'V')
```

### ExplorableCircle.cell_at

```python
def cell_at(point: QPointF) -> tuple[str, int] | None
```

Return the cell under a point.

**Parameters**

- `point` (*QPointF*): A position in the widget.

**Returns**

- *tuple of (str, int) or None*: The ring and place, or None for the middle disc or outside the circle.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.resize(400, 400)
>>> middle, size = circle.geometry_of()
>>> circle.cell_at(QPointF(middle.x(), middle.y() - 0.9 * size))
('outer', 0)
>>> circle.cell_at(QPointF(middle.x() + 0.6 * size, middle.y()))
('inner', 3)
>>> circle.cell_at(middle) is None
True
```

### ExplorableCircle.lift_of

```python
def lift_of(
    ring: str,
    *,
    place: int,
) -> float
```

Return how bright a cell is drawn: as for any question, and a little brighter under the pointer.

**Parameters**

- `ring` (*str*): "outer" or "inner".
- `place` (*int*): The place clockwise from the top. Keyword-only.

**Returns**

- *float*: The brightness, from 0 to 1.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.hover = ("outer", 5)
>>> circle.lift_of("outer", place=5), circle.lift_of("outer", place=6)
(0.2, 0.0)
```

### ExplorableCircle.mousePressEvent

```python
def mousePressEvent(event: QMouseEvent) -> None
```

Pick the cell that is clicked; a click in the middle clears the pick.

**Parameters**

- `event` (*QMouseEvent*): The click.

**Examples**

```pycon
>>> from PySide6.QtCore import QPoint
>>> from PySide6.QtTest import QTest
>>> circle = ExplorableCircle()
>>> circle.resize(400, 400)
>>> centre, radius = circle.geometry_of()
>>> QTest.mouseClick(circle, Qt.MouseButton.LeftButton, pos=QPoint(int(centre.x()), int(centre.y() - 0.9 * radius)))
>>> circle.cell
('outer', 0)
```

### ExplorableCircle.mouseMoveEvent

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

Light the cell under the pointer, and show a hand over the ones that can be picked.

**Parameters**

- `event` (*QMouseEvent*): The move.

**Examples**

```pycon
>>> from PySide6.QtCore import QPoint
>>> from PySide6.QtTest import QTest
>>> circle = ExplorableCircle()
>>> circle.resize(400, 400)
>>> circle.show()
>>> centre, radius = circle.geometry_of()
>>> QTest.mouseMove(circle, QPoint(int(centre.x()), int(centre.y() - 0.9 * radius)))
>>> circle.hover
('outer', 0)
```

### ExplorableCircle.leaveEvent

```python
def leaveEvent(event: QEvent) -> None
```

Stop lighting a cell once the pointer has left.

**Parameters**

- `event` (*QEvent*): The event.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> circle.hover = ("outer", 1)
>>> circle.leaveEvent(QEvent(QEvent.Type.Leave))
>>> circle.hover is None
True
```

### ExplorableCircle.keyPressEvent

```python
def keyPressEvent(event: QKeyEvent) -> None
```

Move the pick with the arrow keys: Left and Right round the circle, Up and Down between the rings.

Escape clears the pick, and Home picks C major.

**Parameters**

- `event` (*QKeyEvent*): The key.

**Examples**

```pycon
>>> circle = ExplorableCircle()
>>> press = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier)
>>> circle.keyPressEvent(press)
>>> circle.cell
('outer', 0)
>>> circle.keyPressEvent(press)
>>> circle.cell
('outer', 1)
```

## ReferencePanel

```python
ReferencePanel(parent: QWidget | None = None)
```

Bases: `QWidget`

The reference for the circle of fifths: a short description, the circle to explore, and what the picked key means.

**Attributes**

- `circle` (*ExplorableCircle*): The circle to pick a key on.
- `explanation` (*QLabel*): The text under the circle, which follows the pick.
- `lesson_button` (*QPushButton*): Opens the lesson on the circle of fifths.
- `lesson_requested` (*Signal*): Emitted with the key of the lesson to open when that button is pressed.

**Examples**

```pycon
>>> panel = ReferencePanel()
>>> panel.circle.select("outer", place=1)
>>> "<b>G major</b>" in panel.explanation.text()
True
```

**Constructor**

Build the panel with nothing picked.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> panel = ReferencePanel()
>>> panel.explanation.text() == ""
False
```

## reference_panel_for

```python
def reference_panel_for(exercise: Exercise) -> ReferencePanel | None
```

Return the reference pane for an exercise.

**Parameters**

- `exercise` (*Exercise*): The exercise.

**Returns**

- *ReferencePanel or None*: The panel, or None for an exercise with nothing to look up.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> reference_panel_for(NoteNames()) is None, reference_panel_for(CircleOfFifths()) is not None
(True, True)
```
{% endraw %}
