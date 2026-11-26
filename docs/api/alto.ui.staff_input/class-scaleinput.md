---
title: ScaleInput
parent: alto.ui.staff_input
api_module: alto.ui.staff_input
package: alto.ui
permalink: /api/alto.ui.staff_input/class-scaleinput/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ScaleInput(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ScaleInput" line=611 %}{% raw %}

</div>

Bases: `StaffInput`

A staff you click to place the notes of a scale one after another,
left to right, and then, if asked, its steps.

The next note follows the pointer, snapped to a line or space, in
the place it will take. Each click puts it there and
moves on to the next place. The places are all drawn from the start,
so the notes do not move as more are placed.

When steps are asked for, once all the notes are placed two lines
rise from each pair of neighboring notes to a point
above them (a wedge). The step to be marked next is shown there, in
the preview color, as "W" (whole) or "H" (half).
The mouse wheel or a right click changes it, and a left click marks
it and moves on to the next pair.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `notes_changed` | `Signal` | Emitted when a note or a step is placed or taken back. |
| `step_selected` | `Signal` | Emitted with "W" or "H" when the step to be marked next changes. |
| `accidental_stepped` | `Signal` | Emitted with 1 or -1 for each notch of the mouse wheel while notes are placed: the owner moves on to the next sign (1) or back to the one before (-1). |
| `notes` | `list of Note` | The notes placed so far, left to right. |
| `steps` | `list of str` | The steps marked so far, each "W" or "H". |
| `slots` | `int` | How many notes the scale has. |
| `with_steps` | `bool` | Whether the steps are asked for too. |
| `pending_step` | `str` | The step that a left click would mark next, "W" or "H". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPointF
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=8)
>>> staff.resize(600, 300)
>>> point = QPointF(
...     50, staff.staff_bottoms()["treble"]
... )
>>> staff.mousePressEvent(
...     QMouseEvent(
...         QEvent.Type.MouseButtonPress,
...         point,
...         point,
...         Qt.MouseButton.LeftButton,
...         Qt.MouseButton.LeftButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> (
...     [str(n) for n in staff.notes],
...     len(staff.columns),
... )
(['E4'], 8)
```

**Constructor**

Create the staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the staff. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleInput().notes
[]
```

## ScaleInput.reset_scale

<div class="api-signature" markdown="1">

```python
def reset_scale(
    clef: str,
    *,
    slots: int,
    caption: str = '',
    with_steps: bool = False,
    key: int = 0,
) -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.reset_scale" line=701 %}{% raw %}

</div>

Clear the staff for a new scale: a staff with room for its
notes, and the key signature it is to have.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | The clef to draw. |
| `slots` | `int` | How many notes the scale has. Keyword-only. |
| `caption` | `str, default ""` | The name of the scale, written under the staff. Keyword-only. |
| `with_steps` | `bool, default False` | Also ask for the steps between the notes. Keyword-only. |
| `key` | `int, default 0` | The key signature drawn on the staff: that many sharps if positive, flats if negative. It is the staff's, not the scale's: a note placed without a sign takes the sign the signature gives its letter. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.notes, staff.slots = (
...     [Note.parse("C4")],
...     3,
... )
>>> staff.reset_scale(
...     "bass", slots=8, caption="D Major"
... )
>>> (
...     staff.notes,
...     staff.slots,
...     staff.caption,
...     staff.key,
... )
([], 8, 'D Major', 0)
>>> staff.reset_scale("bass", slots=8, key=-2)
>>> staff.key
-2
```

## ScaleInput.complete

<div class="api-signature" markdown="1">

```python
@property
def complete() -> bool
```

{% endraw %}{% include api-source.html name="ScaleInput.complete" line=766 %}{% raw %}

</div>

Report whether every note of the scale has been placed.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True when there are as many notes as places. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=1)
>>> staff.complete
False
>>> staff.notes.append(Note.parse("C4"))
>>> staff.complete
True
```

## ScaleInput.placing_steps

<div class="api-signature" markdown="1">

```python
@property
def placing_steps() -> bool
```

{% endraw %}{% include api-source.html name="ScaleInput.placing_steps" line=788 %}{% raw %}

</div>

Report whether it is the turn of the steps: they are asked for,
every note is placed and some step is still to mark.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True while the next click marks a step. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale(
...     "treble", slots=2, with_steps=True
... )
>>> staff.notes.extend(
...     [Note.parse("C4"), Note.parse("D4")]
... )
>>> staff.placing_steps
True
>>> staff.steps.append("W")
>>> staff.placing_steps
False
```

## ScaleInput.done

<div class="api-signature" markdown="1">

```python
@property
def done() -> bool
```

{% endraw %}{% include api-source.html name="ScaleInput.done" line=820 %}{% raw %}

</div>

Report whether everything asked for is placed: every note and,
if they are asked for, every step.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True when the scale can be handed in. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale(
...     "treble", slots=2, with_steps=True
... )
>>> staff.notes.extend(
...     [Note.parse("C4"), Note.parse("D4")]
... )
>>> staff.done
False
>>> staff.steps.append("W")
>>> staff.done
True
```

## ScaleInput.show_note

<div class="api-signature" markdown="1">

```python
def show_note(
    note: Note | None,
    *,
    color: QColor | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.show_note" line=891 %}{% raw %}

</div>

Show the pointer's note in the next place, or take it away.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note or None` | The note to show; None shows none. |
| `color` | `QColor or None, default None` | Unused: the note under the pointer is always drawn in the preview color. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=4)
>>> staff.show_note(Note.parse("G4"))
>>> staff.columns[0], staff.notes
([Note(octave=4, letter=4, accidental=0)], [])
```

## ScaleInput.set_pending_step

<div class="api-signature" markdown="1">

```python
def set_pending_step(step: str) -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.set_pending_step" line=918 %}{% raw %}

</div>

Choose the step that the next click marks.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `step` | `str` | "W" for a whole step or "H" for a half step. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale(
...     "treble", slots=3, with_steps=True
... )
>>> chosen = []
>>> _ = staff.step_selected.connect(
...     chosen.append
... )
>>> staff.set_pending_step("H")
>>> staff.pending_step, chosen
('H', ['H'])
```

## ScaleInput.toggle_step

<div class="api-signature" markdown="1">

```python
def toggle_step() -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.toggle_step" line=946 %}{% raw %}

</div>

Switch the step that the next click marks between whole and
half.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale(
...     "treble", slots=3, with_steps=True
... )
>>> staff.toggle_step()
>>> staff.pending_step
'H'
>>> staff.toggle_step()
>>> staff.pending_step
'W'
```

## ScaleInput.undo

<div class="api-signature" markdown="1">

```python
def undo() -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.undo" line=966 %}{% raw %}

</div>

Take back the last thing placed: the last step if there is one,
otherwise the last note.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=4)
>>> staff.notes.append(Note.parse("C4"))
>>> staff.undo()
>>> staff.notes
[]
```

## ScaleInput.wheelEvent

<div class="api-signature" markdown="1">

```python
def wheelEvent(event: QWheelEvent) -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.wheelEvent" line=989 %}{% raw %}

</div>

Use the mouse wheel for what comes next: the sign of the note to
place, or the step to mark.

While notes are placed each notch asks the owner to move on to
the next sign (up) or back to the one before (down).
While steps are marked each notch switches between whole and
half. Once everything is placed it does nothing.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QWheelEvent` | The wheel turn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPoint, QPointF
>>> staff = ScaleInput()
>>> staff.reset_scale(
...     "treble", slots=2, with_steps=True
... )
>>> signs = []
>>> _ = staff.accidental_stepped.connect(
...     signs.append
... )
>>> here = QPointF(50, 50)
>>> turn = QWheelEvent(
...     here,
...     here,
...     QPoint(0, 0),
...     QPoint(0, 120),
...     Qt.MouseButton.NoButton,
...     Qt.KeyboardModifier.NoModifier,
...     Qt.ScrollPhase.NoScrollPhase,
...     False,
... )
>>> staff.wheelEvent(turn)
>>> signs, staff.pending_step
([1], 'W')
>>> staff.notes.extend(
...     [Note.parse("C4"), Note.parse("D4")]
... )
>>> staff.wheelEvent(turn)
>>> signs, staff.pending_step
([1], 'H')
```

## ScaleInput.caret_start

<div class="api-signature" markdown="1">

```python
def caret_start() -> int
```

{% endraw %}{% include api-source.html name="ScaleInput.caret_start" line=1050 %}{% raw %}

</div>

Return the staff step the caret starts from: that of the last
note placed, or the middle line.

**Returns**

| Type | Description |
| --- | --- |
| `int` | Where the keyboard's first move begins. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=8)
>>> str(
...     Note.from_diatonic(staff.caret_start())
... )  # the middle line
'B4'
>>> staff.notes.append(Note.parse("D4"))
>>> str(
...     Note.from_diatonic(staff.caret_start())
... )  # the note before
'D4'
```

## ScaleInput.place_next

<div class="api-signature" markdown="1">

```python
def place_next(note: Note | None = None) -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.place_next" line=1076 %}{% raw %}

</div>

Place the next note, or mark the next step once the notes are
placed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note or None, default None` | The note to place; the note at the caret if None. Ignored while steps are marked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale(
...     "treble", slots=2, with_steps=True
... )
>>> staff.place_next(Note.parse("C4"))
>>> staff.place_next(Note.parse("D4"))
>>> # the notes are placed: this marks the first step
>>> staff.place_next()
>>> [str(n) for n in staff.notes], staff.steps
(['C4', 'D4'], ['W'])
```

## ScaleInput.place_caret

<div class="api-signature" markdown="1">

```python
def place_caret() -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.place_caret" line=1125 %}{% raw %}

</div>

Place the next note at the caret, or mark the next step, as a
click would.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=2)
>>> staff.move_cursor(2)
>>> staff.place_caret()
>>> [str(n) for n in staff.notes]
['D5']
```

## ScaleInput.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="ScaleInput.mousePressEvent" line=1141 %}{% raw %}

</div>

Place the next note or mark the next step on a left click;
change the sign or the step on a right click.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse press. Nothing happens while the staff is locked or when everything is placed. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPointF
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=1)
>>> staff.resize(600, 300)
>>> point = QPointF(
...     50, staff.staff_bottoms()["treble"]
... )
>>> press = QMouseEvent(
...     QEvent.Type.MouseButtonPress,
...     point,
...     point,
...     Qt.MouseButton.LeftButton,
...     Qt.MouseButton.LeftButton,
...     Qt.KeyboardModifier.NoModifier,
... )
>>> staff.mousePressEvent(press)
>>> staff.mousePressEvent(
...     press
... )  # every place is taken
>>> [str(n) for n in staff.notes]
['E4']
```
{% endraw %}
