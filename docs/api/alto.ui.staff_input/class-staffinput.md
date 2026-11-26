---
title: StaffInput
parent: alto.ui.staff_input
api_module: alto.ui.staff_input
package: alto.ui
permalink: /api/alto.ui.staff_input/class-staffinput/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
StaffInput(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="StaffInput" line=65 %}{% raw %}

</div>

Bases: `StaffWidget`

A single staff you click to place a note, or place a note on with
the keyboard.

The note snaps to the nearest line or space and follows the pointer
until you click. Without the mouse, a caret marks
the note that would be placed: `move_cursor` and `jump_to_letter`
move it, and `place_caret` places it.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `placed` | `Signal` | Emitted with the `Note` when you click, using the current `accidental`. |
| `accidental_cycled` | `Signal` | Emitted on a right click: the owner steps through natural, sharp and flat. |
| `caret_moved` | `Signal` | Emitted when the caret moves. |
| `accidental` | `int or None` | The sign you chose (-1 flat, 0 natural, 1 sharp); None follows the key signature. |
| `locked` | `bool` | Ignore the mouse (while feedback is showing). |
| `caret` | `int or None` | The staff step of the note that the keyboard would place, as `Note.diatonic` counts them; None until the keyboard or a click has put it somewhere. Once it has a place the note is shown in the preview color while the pointer is away. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("treble", key=0)
>>> staff.resize(400, 300)
>>> str(
...     staff.note_at(
...         staff.staff_bottoms()["treble"]
...     )
... )  # the bottom line of the treble staff
'E4'
```

**Constructor**

Create the staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the staff. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StaffInput().hasMouseTracking()
True
```

## StaffInput.reset

<div class="api-signature" markdown="1">

```python
def reset(
    clef: str,
    *,
    key: int = 0,
    caption: str = '',
    placement: Question | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="StaffInput.reset" line=144 %}{% raw %}

</div>

Clear the staff for a new question, drawing a key signature.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | The clef to draw. |
| `key` | `int, default 0` | The key signature: that many sharps if positive, flats if negative. Keyword-only. |
| `caption` | `str, default ""` | Text to write under the staff. Keyword-only. |
| `placement` | `Question or None` | Written placement question with an optional fixed starting note. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.accidental, staff.locked = 1, True
>>> staff.reset("bass", key=-2)
>>> (
...     staff.accidental is None,
...     staff.locked,
...     staff.key,
... )
(True, False, -2)
```

## StaffInput.note_at

<div class="api-signature" markdown="1">

```python
def note_at(y: float) -> Note
```

{% endraw %}{% include api-source.html name="StaffInput.note_at" line=194 %}{% raw %}

</div>

Return the note on the line or space nearest to a height on the
staff.

The note is kept within five ledger lines of the staff. On a
grand staff, a click in the upper half is on the treble
staff and the lower half on the bass staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `y` | `float` | The height in the widget, in pixels from the top. |

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The note, with the chosen accidental or, if none is chosen, the one the key signature gives it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset(
...     "treble", key=1
... )  # G major: F is sharp
>>> staff.resize(400, 300)
>>> bottom = staff.staff_bottoms()["treble"]
>>> str(
...     staff.note_at(
...         bottom - 3 * staff.GAP / 2
...     )
... )  # three steps above E4
'A4'
>>> str(
...     staff.note_at(bottom - staff.GAP / 2)
... )  # one step above E4: F, sharp in this key
'F♯4'
```

## StaffInput.note_for

<div class="api-signature" markdown="1">

```python
def note_for(diatonic: int) -> Note
```

{% endraw %}{% include api-source.html name="StaffInput.note_for" line=257 %}{% raw %}

</div>

Return the note on a staff step, with the chosen sign or the one
the key signature gives it.

The step is kept within five ledger lines of the staff, as
clicking is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `diatonic` | `int` | The staff step, as `Note.diatonic` counts them. |

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The note. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset(
...     "treble", key=1
... )  # G major: F is sharp
>>> str(
...     staff.note_for(
...         Note.parse("F4").diatonic
...     )
... )
'F♯4'
>>> staff.accidental = 0
>>> str(
...     staff.note_for(
...         Note.parse("F4").diatonic
...     )
... )
'F4'
```

## StaffInput.caret_start

<div class="api-signature" markdown="1">

```python
def caret_start() -> int
```

{% endraw %}{% include api-source.html name="StaffInput.caret_start" line=304 %}{% raw %}

</div>

Return the staff step the caret starts from, when the keyboard
first moves it.

**Returns**

| Type | Description |
| --- | --- |
| `int` | The middle line of the staff, or middle C on a grand staff. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> str(Note.from_diatonic(staff.caret_start()))
'B4'
>>> staff.reset("grand")
>>> str(Note.from_diatonic(staff.caret_start()))
'C4'
```

## StaffInput.caret_note

<div class="api-signature" markdown="1">

```python
def caret_note() -> Note | None
```

{% endraw %}{% include api-source.html name="StaffInput.caret_note" line=326 %}{% raw %}

</div>

Return the note that the keyboard would place.

**Returns**

| Type | Description |
| --- | --- |
| `Note or None` | The note at the caret, with the chosen sign; None if the caret has not been put anywhere. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("bass")
>>> staff.caret_note() is None
True
>>> staff.move_cursor(0)
>>> str(staff.caret_note())
'D3'
```

## StaffInput.move_cursor

<div class="api-signature" markdown="1">

```python
def move_cursor(steps: int) -> None
```

{% endraw %}{% include api-source.html name="StaffInput.move_cursor" line=348 %}{% raw %}

</div>

Move the caret up (positive) or down (negative) by staff steps,
and show the note there.

The first move starts from `caret_start`. The caret stays within
the furthest ledger lines.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `steps` | `int` | How many lines and spaces to move; 7 is an octave. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.move_cursor(1)
>>> str(staff.caret_note())
'C5'
>>> staff.move_cursor(-7)
>>> str(staff.caret_note())
'C4'
>>> staff.move_cursor(
...     -500
... )  # no further than the ledger lines go
>>> staff.caret == RANGE_LIMITS["treble"][0]
True
```

## StaffInput.jump_to_letter

<div class="api-signature" markdown="1">

```python
def jump_to_letter(letter: int) -> None
```

{% endraw %}{% include api-source.html name="StaffInput.jump_to_letter" line=383 %}{% raw %}

</div>

Move the caret to the nearest note with a letter name, above or
below where it is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `letter` | `int` | The letter, counting from C as 0: D is 1, E is 2, F is 3, G is 4, A is 5 and B is 6. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.move_cursor(0)  # B4, the middle line
>>> staff.jump_to_letter(0)
>>> str(
...     staff.caret_note()
... )  # the nearest C is the one just above
'C5'
>>> staff.jump_to_letter(4)
>>> str(
...     staff.caret_note()
... )  # and the nearest G is the one just below
'G4'
```

## StaffInput.place_caret

<div class="api-signature" markdown="1">

```python
def place_caret() -> None
```

{% endraw %}{% include api-source.html name="StaffInput.place_caret" line=420 %}{% raw %}

</div>

Place the note at the caret, as a click would.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> placed = []
>>> _ = staff.placed.connect(placed.append)
>>> # the first press places the note at the start
>>> staff.place_caret()
>>> [str(n) for n in placed]
['B4']
```

## StaffInput.show_note

<div class="api-signature" markdown="1">

```python
def show_note(
    note: Note | None,
    *,
    color: QColor | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="StaffInput.show_note" line=443 %}{% raw %}

</div>

Draw a single note on the staff, or clear it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note or None` | The note to draw; None clears the staff. |
| `color` | `QColor or None, default None` | The color to draw it in; the notation's own ink if None. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.show_note(Note.parse("C4"))
>>> len(staff.columns)
1
>>> staff.show_note(None)
>>> staff.columns
[]
```

## StaffInput.refresh_preview

<div class="api-signature" markdown="1">

```python
def refresh_preview() -> None
```

{% endraw %}{% include api-source.html name="StaffInput.refresh_preview" line=480 %}{% raw %}

</div>

Redraw the note that would be placed, for example after the
accidental changes.

It is the pointer's note while the pointer is over the staff,
and otherwise the note at the caret, once the keyboard
has put the caret somewhere.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> # the pointer is not over the staff, and there is no caret:
>>> # nothing to redraw
>>> staff.refresh_preview()
>>> staff.columns
[]
>>> staff.reset("treble")
>>> staff.move_cursor(0)
>>> len(staff.columns)  # the note at the caret
1
```

## StaffInput.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="StaffInput.mouseMoveEvent" line=512 %}{% raw %}

</div>

Show the note under the pointer, in a lighter color.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.resize(400, 300)
>>> from PySide6.QtCore import QPointF
>>> point = QPointF(
...     50, staff.staff_bottoms()["treble"]
... )
>>> staff.mouseMoveEvent(
...     QMouseEvent(
...         QEvent.Type.MouseMove,
...         point,
...         point,
...         Qt.MouseButton.NoButton,
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> str(staff.columns[0][0])
'E4'
```

## StaffInput.leaveEvent

<div class="api-signature" markdown="1">

```python
def leaveEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="StaffInput.leaveEvent" line=546 %}{% raw %}

</div>

Remove the pointer's note when the pointer leaves the staff,
showing the note at the caret instead if there is one.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QEvent` | The leave event. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.show_note(Note.parse("C4"))
>>> staff.leaveEvent(QEvent(QEvent.Type.Leave))
>>> staff.columns
[]
```

## StaffInput.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="StaffInput.mousePressEvent" line=567 %}{% raw %}

</div>

Place the note on a left click, or step through the accidentals
on a right click.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse press. Nothing happens while the staff is locked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.resize(400, 300)
>>> placed = []
>>> _ = staff.placed.connect(placed.append)
>>> from PySide6.QtCore import QPointF
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
>>> [str(n) for n in placed]
['E4']
```
{% endraw %}
