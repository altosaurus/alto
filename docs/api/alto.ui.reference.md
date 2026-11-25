---
title: alto.ui.reference
parent: api
package: alto.ui
permalink: /api/alto.ui.reference/
---
{% raw %}
The reference pane: an interactive circle of fifths to look things up
on, with an explanation under it.

Click a key on either ring, or move with the arrow keys, and the circle
lights that key's chords, shows its key signature in
the middle, and the text underneath explains it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.select("outer", place=2)
>>> circle.title, circle.signature
('D major', 2)
```

## ExplorableCircle

<div class="api-signature" markdown="1">

```python
ExplorableCircle(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ExplorableCircle" line=94 %}{% raw %}

</div>

Bases: `FifthsCircle`

A circle of fifths that shows every key and lets you pick one.

**Attributes**

- `cell` (*tuple of (str, int) or None*): The cell that is picked: its ring ("outer" or "inner") and its place clockwise from the top; None for none.
- `hover` (*tuple of (str, int) or None*): The cell under the pointer.
- `interactive` (*bool*): Whether the circle answers the mouse and the keys. A picture of the circle that only the program changes has it off.
- `picked` (*Signal*): Emitted with the ring and place when a cell is picked, or with "" and -1 when the pick is cleared.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.cell, circle.title
(None, 'Circle of fifths')
```

**Constructor**

Build the circle with every key named and none picked.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ExplorableCircle().shown["inner"] == set(
...     range(12)
... )
True
```

### ExplorableCircle.set_interactive

<div class="api-signature" markdown="1">

```python
def set_interactive(interactive: bool) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.set_interactive" line=147 %}{% raw %}

</div>

Let the circle be clicked and moved with the keys, or make it a
picture.

**Parameters**

- `interactive` (*bool*): True to answer the mouse and the keys.

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

### ExplorableCircle.clear

<div class="api-signature" markdown="1">

```python
def clear() -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.clear" line=176 %}{% raw %}

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

### ExplorableCircle.select

<div class="api-signature" markdown="1">

```python
def select(
    ring: str,
    *,
    place: int,
) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.select" line=204 %}{% raw %}

</div>

Pick a cell: light the chords of its key, and show its name and
key signature in the middle.

A minor key has the key signature, and the chords, of its
relative major.

**Parameters**

- `ring` (*str*): "outer" for the major key at the place, "inner" for its relative minor.
- `place` (*int*): The place, clockwise from the top. Keyword-only.

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

### ExplorableCircle.cell_at

<div class="api-signature" markdown="1">

```python
def cell_at(point: QPointF) -> tuple[str, int] | None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.cell_at" line=263 %}{% raw %}

</div>

Return the cell under a point.

**Parameters**

- `point` (*QPointF*): A position in the widget.

**Returns**

- *tuple of (str, int) or None*: The ring and place, or None for the middle disc or outside the circle.

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

### ExplorableCircle.lift_of

<div class="api-signature" markdown="1">

```python
def lift_of(
    ring: str,
    *,
    place: int,
) -> float
```

{% endraw %}{% include api-source.html name="ExplorableCircle.lift_of" line=307 %}{% raw %}

</div>

Return how bright a cell is drawn: as for any question, and a
little brighter under the pointer.

**Parameters**

- `ring` (*str*): "outer" or "inner".
- `place` (*int*): The place clockwise from the top. Keyword-only.

**Returns**

- *float*: The brightness, from 0 to 1.

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

### ExplorableCircle.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.mousePressEvent" line=342 %}{% raw %}

</div>

Pick the cell that is clicked; a click in the middle clears the
pick.

**Parameters**

- `event` (*QMouseEvent*): The click.

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

### ExplorableCircle.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.mouseMoveEvent" line=379 %}{% raw %}

</div>

Light the cell under the pointer, and show a hand over the ones
that can be picked.

**Parameters**

- `event` (*QMouseEvent*): The move.

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

### ExplorableCircle.leaveEvent

<div class="api-signature" markdown="1">

```python
def leaveEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.leaveEvent" line=411 %}{% raw %}

</div>

Stop lighting a cell once the pointer has left.

**Parameters**

- `event` (*QEvent*): The event.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.hover = ("outer", 1)
>>> circle.leaveEvent(QEvent(QEvent.Type.Leave))
>>> circle.hover is None
True
```

### ExplorableCircle.keyPressEvent

<div class="api-signature" markdown="1">

```python
def keyPressEvent(event: QKeyEvent) -> None
```

{% endraw %}{% include api-source.html name="ExplorableCircle.keyPressEvent" line=460 %}{% raw %}

</div>

Move the pick with the arrow keys: Left and Right around the
circle, Up and Down between the rings.

Escape clears the pick, and Home picks C major.

**Parameters**

- `event` (*QKeyEvent*): The key.

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

## ReferencePanel

<div class="api-signature" markdown="1">

```python
ReferencePanel(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ReferencePanel" line=510 %}{% raw %}

</div>

Bases: `QWidget`

The reference for the circle of fifths: a short description, the
circle to explore, and what the picked key means.

**Attributes**

- `circle` (*ExplorableCircle*): The circle to pick a key on.
- `explanation` (*QLabel*): The text under the circle, which follows the pick.
- `lesson_button` (*QPushButton*): Opens the lesson on the circle of fifths.
- `lesson_requested` (*Signal*): Emitted with the key of the lesson to open when that button is pressed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ReferencePanel()
>>> panel.explanation.text() == ""
False
```

## ClefReferencePanel

<div class="api-signature" markdown="1">

```python
ClefReferencePanel(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ClefReferencePanel" line=634 %}{% raw %}

</div>

Bases: `QWidget`

The reference for the clefs: how they are made, and a picture of
each with where its symbol goes.

**Attributes**

- `lesson_button` (*QPushButton*): Opens the lesson on the clefs.
- `lesson_requested` (*Signal*): Emitted with the key of the lesson to open when that button is pressed.
- `rows` (*dict of str to QLabel*): The words beside the picture of each clef, by clef.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ClefReferencePanel()
>>> "C clef" in panel.rows[
...     "mezzo"
... ].text() and "bottom line" in panel.rows[
...     "french"
... ].text()
True
```

**Constructor**

Build the panel: the lesson button, a line of explanation and a
row for each clef.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(ClefReferencePanel().rows) == len(
...     settings.CLEF_BASICS_CLEFS
... )
True
```

## ScaleReferencePanel

<div class="api-signature" markdown="1">

```python
ScaleReferencePanel(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ScaleReferencePanel" line=725 %}{% raw %}

</div>

Bases: `QWidget`

Scale identification hints and a link to the guided lesson.

**Constructor**

Build a scrollable guide to tonic reading and scale patterns.

## NoteReferencePanel

<div class="api-signature" markdown="1">

```python
NoteReferencePanel(exercise: Exercise)
```

{% endraw %}{% include api-source.html name="NoteReferencePanel" line=874 %}{% raw %}

</div>

Bases: `QWidget`

Hints for reading notes or intervals and a link to the associated
lesson.

**Constructor**

Show the hints for the current note exercise.

**Parameters**

- `exercise` (*Exercise*): The note exercise whose reference was opened.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteReferencePanel(
...     KeyboardNotes()
... ).lesson_button.text()
'New to this? Take the full lesson  →'
```

## PluginReferencePanel

<div class="api-signature" markdown="1">

```python
PluginReferencePanel(
    exercise: Exercise,
    *,
    lessons: list[Lesson],
)
```

{% endraw %}{% include api-source.html name="PluginReferencePanel" line=929 %}{% raw %}

</div>

Bases: `QWidget`

What a plugin's exercise offers to look up: what it asks, and a
button for each lesson that teaches it.

**Constructor**

Show the exercise's description and a button for each lesson
that goes with it.

**Parameters**

- `exercise` (*Exercise*): The plugin's exercise whose reference was opened.
- `lessons` (*list of Lesson*): At least one lesson that names the exercise as practice, or that the exercise names. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> demo = Lesson(
...     key="pack.d.l",
...     title="Parts",
...     about="",
...     summary="",
...     category="D",
...     steps=(),
...     exercise="x",
... )
>>> PluginReferencePanel(
...     NoteNames(), lessons=[demo]
... ).lesson_buttons[0].text()
'New to this? Take the lesson: Parts  →'
```

## reference_panel_for

<div class="api-signature" markdown="1">

```python
def reference_panel_for(exercise: Exercise) -> ReferencePanel | ClefReferencePanel | ScaleReferencePanel | NoteReferencePanel | PluginReferencePanel | None
```

{% endraw %}{% include api-source.html name="reference_panel_for" line=999 %}{% raw %}

</div>

Return the reference pane for an exercise.

**Parameters**

- `exercise` (*Exercise*): The exercise.

**Returns**

- *ReferencePanel or ClefReferencePanel or ScaleReferencePanel or*
- *NoteReferencePanel or None*: The panel, or None for an exercise with nothing to look up.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> (
...     isinstance(
...         reference_panel_for(NoteNames()),
...         NoteReferencePanel,
...     ),
...     reference_panel_for(CircleOfFifths())
...     is not None,
... )
(True, True)
>>> type(
...     reference_panel_for(ClefBasics())
... ).__name__
'ClefReferencePanel'
```
{% endraw %}
