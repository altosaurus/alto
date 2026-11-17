---
title: alto.ui.staff_input
parent: api
package: alto.ui
order: 55
permalink: /api/alto.ui.staff_input/
---
{% raw %}
The staffs you click to place notes or a clef.

One note for the note construction exercise, a row of them for scale construction, and a clef for the clef exercise.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.accidental is None and not staff.locked
True
```

## StaffInput

```python
StaffInput(parent: QWidget | None = None)
```

Bases: `StaffWidget`

A single staff you click to place a note, or place a note on with the keyboard.

The note snaps to the nearest line or space and follows the pointer until you click. Without the mouse, a caret marks
the note that would be placed: `move_cursor` and `jump_to_letter` move it, and `place_caret` places it.

**Attributes**

- `placed` (*Signal*): Emitted with the `Note` when you click, using the current `accidental`.
- `accidental_cycled` (*Signal*): Emitted on a right click: the owner steps through natural, sharp and flat.
- `caret_moved` (*Signal*): Emitted when the caret moves.
- `accidental` (*int or None*): The sign you chose (-1 flat, 0 natural, 1 sharp); None follows the key signature.
- `locked` (*bool*): Ignore the mouse (while feedback is showing).
- `caret` (*int or None*): The staff step of the note that the keyboard would place, as `Note.diatonic` counts them; None until the keyboard or a click has put it somewhere. Once it has a place the note is shown in the preview color while the pointer is away.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble", key=0)
>>> staff.resize(400, 300)
>>> str(staff.note_at(staff.staff_bottoms()["treble"]))  # the bottom line of the treble staff
'E4'
```

**Constructor**

Create the staff.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the staff.

**Constructor examples**

```pycon
>>> StaffInput().hasMouseTracking()
True
```

### StaffInput.reset

```python
def reset(
    clef: str,
    *,
    key: int = 0,
    caption: str = '',
) -> None
```

Clear the staff for a new question, drawing a key signature.

**Parameters**

- `clef` (*str*): The clef to draw.
- `key` (*int, default 0*): The key signature: that many sharps if positive, flats if negative. Keyword-only.
- `caption` (*str, default ""*): Text to write under the staff. Keyword-only.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.accidental, staff.locked = 1, True
>>> staff.reset("bass", key=-2)
>>> staff.accidental is None, staff.locked, staff.key
(True, False, -2)
```

### StaffInput.note_at

```python
def note_at(y: float) -> Note
```

Return the note on the line or space nearest to a height on the staff.

The note is kept within five ledger lines of the staff. On a grand staff, a click in the upper half is on the treble
staff and the lower half on the bass staff.

**Parameters**

- `y` (*float*): The height in the widget, in pixels from the top.

**Returns**

- *Note*: The note, with the chosen accidental or, if none is chosen, the one the key signature gives it.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble", key=1)  # G major: F is sharp
>>> staff.resize(400, 300)
>>> bottom = staff.staff_bottoms()["treble"]
>>> str(staff.note_at(bottom - 3 * staff.GAP / 2))  # three steps above E4
'A4'
>>> str(staff.note_at(bottom - staff.GAP / 2))  # one step above E4: F, sharp in this key
'F♯4'
```

### StaffInput.note_for

```python
def note_for(diatonic: int) -> Note
```

Return the note on a staff step, with the chosen sign or the one the key signature gives it.

The step is kept within five ledger lines of the staff, as clicking is.

**Parameters**

- `diatonic` (*int*): The staff step, as `Note.diatonic` counts them.

**Returns**

- *Note*: The note.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble", key=1)  # G major: F is sharp
>>> str(staff.note_for(Note.parse("F4").diatonic))
'F♯4'
>>> staff.accidental = 0
>>> str(staff.note_for(Note.parse("F4").diatonic))
'F4'
```

### StaffInput.caret_start

```python
def caret_start() -> int
```

Return the staff step the caret starts from, when the keyboard first moves it.

**Returns**

- *int*: The middle line of the staff, or middle C on a grand staff.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> str(Note.from_diatonic(staff.caret_start()))
'B4'
>>> staff.reset("grand")
>>> str(Note.from_diatonic(staff.caret_start()))
'C4'
```

### StaffInput.caret_note

```python
def caret_note() -> Note | None
```

Return the note that the keyboard would place.

**Returns**

- *Note or None*: The note at the caret, with the chosen sign; None if the caret has not been put anywhere.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("bass")
>>> staff.caret_note() is None
True
>>> staff.move_cursor(0)
>>> str(staff.caret_note())
'D3'
```

### StaffInput.move_cursor

```python
def move_cursor(steps: int) -> None
```

Move the caret up (positive) or down (negative) by staff steps, and show the note there.

The first move starts from `caret_start`. The caret stays within the furthest ledger lines.

**Parameters**

- `steps` (*int*): How many lines and spaces to move; 7 is an octave.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.move_cursor(1)
>>> str(staff.caret_note())
'C5'
>>> staff.move_cursor(-7)
>>> str(staff.caret_note())
'C4'
>>> staff.move_cursor(-500)  # no further than the ledger lines go
>>> staff.caret == RANGE_LIMITS["treble"][0]
True
```

### StaffInput.jump_to_letter

```python
def jump_to_letter(letter: int) -> None
```

Move the caret to the nearest note with a letter name, above or below where it is.

**Parameters**

- `letter` (*int*): The letter, counting from C as 0: D is 1, E is 2, F is 3, G is 4, A is 5 and B is 6.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.move_cursor(0)  # B4, the middle line
>>> staff.jump_to_letter(0)
>>> str(staff.caret_note())  # the nearest C is the one just above
'C5'
>>> staff.jump_to_letter(4)
>>> str(staff.caret_note())  # and the nearest G is the one just below
'G4'
```

### StaffInput.place_caret

```python
def place_caret() -> None
```

Place the note at the caret, as a click would.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> placed = []
>>> _ = staff.placed.connect(placed.append)
>>> staff.place_caret()  # the first press places the note at the start
>>> [str(n) for n in placed]
['B4']
```

### StaffInput.show_note

```python
def show_note(
    note: Note | None,
    *,
    color: QColor | None = None,
) -> None
```

Draw a single note on the staff, or clear it.

**Parameters**

- `note` (*Note or None*): The note to draw; None clears the staff.
- `color` (*QColor or None, default None*): The color to draw it in; the notation's own ink if None. Keyword-only.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.show_note(Note.parse("C4"))
>>> len(staff.columns)
1
>>> staff.show_note(None)
>>> staff.columns
[]
```

### StaffInput.refresh_preview

```python
def refresh_preview() -> None
```

Redraw the note that would be placed, for example after the accidental changes.

It is the pointer's note while the pointer is over the staff, and otherwise the note at the caret, once the keyboard
has put the caret somewhere.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.refresh_preview()  # the pointer is not over the staff, and there is no caret: nothing to redraw
>>> staff.columns
[]
>>> staff.reset("treble")
>>> staff.move_cursor(0)
>>> len(staff.columns)  # the note at the caret
1
```

### StaffInput.mouseMoveEvent

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

Show the note under the pointer, in a lighter color.

**Parameters**

- `event` (*QMouseEvent*): The mouse move.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.resize(400, 300)
>>> from PySide6.QtCore import QPointF
>>> point = QPointF(50, staff.staff_bottoms()["treble"])
>>> staff.mouseMoveEvent(QMouseEvent(QEvent.Type.MouseMove, point, point, Qt.MouseButton.NoButton,
...                                  Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier))
>>> str(staff.columns[0][0])
'E4'
```

### StaffInput.leaveEvent

```python
def leaveEvent(event: QEvent) -> None
```

Remove the pointer's note when the pointer leaves the staff, showing the note at the caret instead if there is one.

**Parameters**

- `event` (*QEvent*): The leave event.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.show_note(Note.parse("C4"))
>>> staff.leaveEvent(QEvent(QEvent.Type.Leave))
>>> staff.columns
[]
```

### StaffInput.mousePressEvent

```python
def mousePressEvent(event: QMouseEvent) -> None
```

Place the note on a left click, or step through the accidentals on a right click.

**Parameters**

- `event` (*QMouseEvent*): The mouse press. Nothing happens while the staff is locked.

**Examples**

```pycon
>>> staff = StaffInput()
>>> staff.reset("treble")
>>> staff.resize(400, 300)
>>> placed = []
>>> _ = staff.placed.connect(placed.append)
>>> from PySide6.QtCore import QPointF
>>> point = QPointF(50, staff.staff_bottoms()["treble"])
>>> staff.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.LeftButton,
...                                   Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
>>> [str(n) for n in placed]
['E4']
```

## ScaleInput

```python
ScaleInput(parent: QWidget | None = None)
```

Bases: `StaffInput`

A staff you click to place the notes of a scale one after another, left to right, and then, if asked, its steps.

The next note follows the pointer, snapped to a line or space, in the place it will take. Each click puts it there and
moves on to the next place. The places are all drawn from the start, so the notes do not move as more are placed.

When steps are asked for, once all the notes are placed two lines rise from each pair of neighboring notes to a point
above them (a wedge). The step to be marked next is shown there, in the preview color, as "W" (whole) or "H" (half).
The mouse wheel or a right click changes it, and a left click marks it and moves on to the next pair.

**Attributes**

- `notes_changed` (*Signal*): Emitted when a note or a step is placed or taken back.
- `step_selected` (*Signal*): Emitted with "W" or "H" when the step to be marked next changes.
- `accidental_stepped` (*Signal*): Emitted with 1 or -1 for each notch of the mouse wheel while notes are placed: the owner moves on to the next sign (1) or back to the one before (-1).
- `notes` (*list of Note*): The notes placed so far, left to right.
- `steps` (*list of str*): The steps marked so far, each "W" or "H".
- `slots` (*int*): How many notes the scale has.
- `with_steps` (*bool*): Whether the steps are asked for too.
- `pending_step` (*str*): The step that a left click would mark next, "W" or "H".

**Examples**

```pycon
>>> from PySide6.QtCore import QPointF
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=8)
>>> staff.resize(600, 300)
>>> point = QPointF(50, staff.staff_bottoms()["treble"])
>>> staff.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.LeftButton,
...                                   Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
>>> [str(n) for n in staff.notes], len(staff.columns)
(['E4'], 8)
```

**Constructor**

Create the staff.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the staff.

**Constructor examples**

```pycon
>>> ScaleInput().notes
[]
```

### ScaleInput.reset_scale

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

Clear the staff for a new scale: a staff with room for its notes, and the key signature it is to have.

**Parameters**

- `clef` (*str*): The clef to draw.
- `slots` (*int*): How many notes the scale has. Keyword-only.
- `caption` (*str, default ""*): The name of the scale, written under the staff. Keyword-only.
- `with_steps` (*bool, default False*): Also ask for the steps between the notes. Keyword-only.
- `key` (*int, default 0*): The key signature drawn on the staff: that many sharps if positive, flats if negative. It is the staff's, not the scale's: a note placed without a sign takes the sign the signature gives its letter. Keyword-only.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.notes, staff.slots = [Note.parse("C4")], 3
>>> staff.reset_scale("bass", slots=8, caption="D Major")
>>> staff.notes, staff.slots, staff.caption, staff.key
([], 8, 'D Major', 0)
>>> staff.reset_scale("bass", slots=8, key=-2)
>>> staff.key
-2
```

### ScaleInput.complete

```python
@property
def complete() -> bool
```

Report whether every note of the scale has been placed.

**Returns**

- *bool*: True when there are as many notes as places.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=1)
>>> staff.complete
False
>>> staff.notes.append(Note.parse("C4"))
>>> staff.complete
True
```

### ScaleInput.placing_steps

```python
@property
def placing_steps() -> bool
```

Report whether it is the turn of the steps: they are asked for, every note is placed and some step is still to mark.

**Returns**

- *bool*: True while the next click marks a step.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=2, with_steps=True)
>>> staff.notes.extend([Note.parse("C4"), Note.parse("D4")])
>>> staff.placing_steps
True
>>> staff.steps.append("W")
>>> staff.placing_steps
False
```

### ScaleInput.done

```python
@property
def done() -> bool
```

Report whether everything asked for is placed: every note and, if they are asked for, every step.

**Returns**

- *bool*: True when the scale can be handed in.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=2, with_steps=True)
>>> staff.notes.extend([Note.parse("C4"), Note.parse("D4")])
>>> staff.done
False
>>> staff.steps.append("W")
>>> staff.done
True
```

### ScaleInput.show_note

```python
def show_note(
    note: Note | None,
    *,
    color: QColor | None = None,
) -> None
```

Show the pointer's note in the next place, or take it away.

**Parameters**

- `note` (*Note or None*): The note to show; None shows none.
- `color` (*QColor or None, default None*): Unused: the note under the pointer is always drawn in the preview color. Keyword-only.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=4)
>>> staff.show_note(Note.parse("G4"))
>>> staff.columns[0], staff.notes
([Note(octave=4, letter=4, accidental=0)], [])
```

### ScaleInput.set_pending_step

```python
def set_pending_step(step: str) -> None
```

Choose the step that the next click marks.

**Parameters**

- `step` (*str*): "W" for a whole step or "H" for a half step.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=3, with_steps=True)
>>> chosen = []
>>> _ = staff.step_selected.connect(chosen.append)
>>> staff.set_pending_step("H")
>>> staff.pending_step, chosen
('H', ['H'])
```

### ScaleInput.toggle_step

```python
def toggle_step() -> None
```

Switch the step that the next click marks between whole and half.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=3, with_steps=True)
>>> staff.toggle_step()
>>> staff.pending_step
'H'
>>> staff.toggle_step()
>>> staff.pending_step
'W'
```

### ScaleInput.undo

```python
def undo() -> None
```

Take back the last thing placed: the last step if there is one, otherwise the last note.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=4)
>>> staff.notes.append(Note.parse("C4"))
>>> staff.undo()
>>> staff.notes
[]
```

### ScaleInput.wheelEvent

```python
def wheelEvent(event: QWheelEvent) -> None
```

Use the mouse wheel for what comes next: the sign of the note to place, or the step to mark.

While notes are placed each notch asks the owner to move on to the next sign (up) or back to the one before (down).
While steps are marked each notch switches between whole and half. Once everything is placed it does nothing.

**Parameters**

- `event` (*QWheelEvent*): The wheel turn.

**Examples**

```pycon
>>> from PySide6.QtCore import QPoint, QPointF
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=2, with_steps=True)
>>> signs = []
>>> _ = staff.accidental_stepped.connect(signs.append)
>>> here = QPointF(50, 50)
>>> turn = QWheelEvent(here, here, QPoint(0, 0), QPoint(0, 120), Qt.MouseButton.NoButton,
...                    Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False)
>>> staff.wheelEvent(turn)
>>> signs, staff.pending_step
([1], 'W')
>>> staff.notes.extend([Note.parse("C4"), Note.parse("D4")])
>>> staff.wheelEvent(turn)
>>> signs, staff.pending_step
([1], 'H')
```

### ScaleInput.caret_start

```python
def caret_start() -> int
```

Return the staff step the caret starts from: that of the last note placed, or the middle line.

**Returns**

- *int*: Where the keyboard's first move begins.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=8)
>>> str(Note.from_diatonic(staff.caret_start()))  # the middle line
'B4'
>>> staff.notes.append(Note.parse("D4"))
>>> str(Note.from_diatonic(staff.caret_start()))  # the note before
'D4'
```

### ScaleInput.place_next

```python
def place_next(note: Note | None = None) -> None
```

Place the next note, or mark the next step once the notes are placed.

**Parameters**

- `note` (*Note or None, default None*): The note to place; the note at the caret if None. Ignored while steps are marked.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=2, with_steps=True)
>>> staff.place_next(Note.parse("C4"))
>>> staff.place_next(Note.parse("D4"))
>>> staff.place_next()  # the notes are placed: this marks the first step
>>> [str(n) for n in staff.notes], staff.steps
(['C4', 'D4'], ['W'])
```

### ScaleInput.place_caret

```python
def place_caret() -> None
```

Place the next note at the caret, or mark the next step, as a click would.

**Examples**

```pycon
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=2)
>>> staff.move_cursor(2)
>>> staff.place_caret()
>>> [str(n) for n in staff.notes]
['D5']
```

### ScaleInput.mousePressEvent

```python
def mousePressEvent(event: QMouseEvent) -> None
```

Place the next note or mark the next step on a left click; change the sign or the step on a right click.

**Parameters**

- `event` (*QMouseEvent*): The mouse press. Nothing happens while the staff is locked or when everything is placed.

**Examples**

```pycon
>>> from PySide6.QtCore import QPointF
>>> staff = ScaleInput()
>>> staff.reset_scale("treble", slots=1)
>>> staff.resize(600, 300)
>>> point = QPointF(50, staff.staff_bottoms()["treble"])
>>> press = QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.LeftButton,
...                     Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
>>> staff.mousePressEvent(press)
>>> staff.mousePressEvent(press)  # every place is taken
>>> [str(n) for n in staff.notes]
['E4']
```

## ClefInput

```python
ClefInput(parent: QWidget | None = None)
```

Bases: `StaffWidget`

A blank staff on which you put a clef symbol: choose the G, C or F clef, then click where it goes.

The symbol can go on any line or space of the staff and on the three ledger lines and spaces above and below it, and
follows the pointer from place to place, in a lighter color, until you click. Without the mouse, `move_caret` moves it,
`step_symbol` switches the symbol and `place_caret` places it.

**Attributes**

- `placed` (*Signal*): Emitted with the symbol ("G", "C" or "F") and its place when you click: 0 is the bottom line, 1 the space above it, up to 8 for the top line, with -6 to 14 allowed.
- `changed` (*Signal*): Emitted when the symbol chosen or the place the keyboard would use changes.
- `options` (*list of str*): The symbols that can be chosen, in the order the wheel goes through them.
- `selected` (*str*): The symbol chosen now.
- `locked` (*bool*): Ignore the mouse and the wheel (while feedback is showing).
- `caret` (*int or None*): The place the keyboard would put the symbol; None until the keyboard has moved it.
- `placed_symbol` (*str or None*): The symbol that has been placed and is drawn solid, with `placed_step` its place; None until one is.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G", "F"])
>>> staff.step_symbol(1)
>>> staff.selected
'F'
```

**Constructor**

Create the staff.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the staff.

**Constructor examples**

```pycon
>>> ClefInput().hasMouseTracking()
True
```

### ClefInput.reset

```python
def reset(
    options: list[str],
    *,
    caption: str = '',
) -> None
```

Clear the staff for a new question and offer some symbols to choose from.

**Parameters**

- `options` (*list of str*): The symbols the wheel goes through, any of "G", "C" and "F"; the first is chosen to begin with.
- `caption` (*str, default ""*): The question, written under the staff. Keyword-only.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["C", "F"], caption="Place the alto clef.")
>>> staff.selected, staff.placed_symbol, staff.caption
('C', None, 'Place the alto clef.')
```

### ClefInput.select

```python
def select(symbol: str) -> None
```

Choose a symbol.

**Parameters**

- `symbol` (*str*): "G", "C" or "F"; one that is not among the options is ignored.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G", "C", "F"])
>>> staff.select("F")
>>> staff.selected
'F'
```

### ClefInput.step_symbol

```python
def step_symbol(direction: int) -> None
```

Choose the next symbol of the options, or the one before, going around.

**Parameters**

- `direction` (*int*): 1 for the next, -1 for the one before.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G", "C", "F"])
>>> staff.step_symbol(-1)
>>> staff.selected
'F'
```

### ClefInput.step_at

```python
def step_at(y: float) -> int
```

Return the line or space nearest to a height in the widget.

**Parameters**

- `y` (*float*): The height, in pixels.

**Returns**

- *int*: The place, 0 for the bottom line and 1 for the space above it, up to 8 for the top line; from the first ledger line below the staff (-6) to the third above it (14).

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.resize(400, 300)
>>> floor = staff.staff_bottoms()["treble"]
>>> staff.step_at(floor), staff.step_at(floor - 1.4 * staff.GAP), staff.step_at(0), staff.step_at(10_000)
(0, 3, 14, -6)
```

### ClefInput.move_caret

```python
def move_caret(steps: int) -> None
```

Move the place the keyboard would put the symbol.

**Parameters**

- `steps` (*int*): How many lines and spaces up (positive) or down, stopping at the last ledger lines; the first move starts from the middle line.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.move_caret(1)
>>> staff.caret
5
>>> staff.move_caret(20)
>>> staff.caret
14
```

### ClefInput.place

```python
def place(step: int) -> None
```

Put the chosen symbol in a place, drawn solid, and say so.

**Parameters**

- `step` (*int*): The place, 0 for the bottom line, 1 for the space above it and so on.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["F"])
>>> got = []
>>> _ = staff.placed.connect(lambda symbol, where: got.append((symbol, where)))
>>> staff.place(6)
>>> got, staff.placed_symbol, staff.placed_step
([('F', 6)], 'F', 6)
```

### ClefInput.place_caret

```python
def place_caret() -> None
```

Place the symbol where the keyboard put it, or on the middle line if it has not moved.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.move_caret(-2)
>>> staff.place_caret()
>>> staff.placed_step
2
```

### ClefInput.clear_placed

```python
def clear_placed() -> None
```

Take the placed symbol off the staff, so another can be tried.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.place(1)
>>> staff.clear_placed()
>>> staff.placed_symbol is None
True
```

### ClefInput.set_clef_color

```python
def set_clef_color(color: QColor | None) -> None
```

Draw the placed symbol in a color, for feedback, or back in black.

**Parameters**

- `color` (*QColor or None*): The color; None for black.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.set_clef_color(QColor("#2e7d32"))
>>> staff.clef_color == QColor("#2e7d32")
True
```

### ClefInput.mouseMoveEvent

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

Show the symbol in the place under the pointer, in a lighter color.

**Parameters**

- `event` (*QMouseEvent*): The mouse move.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.resize(400, 300)
>>> from PySide6.QtCore import QPointF
>>> point = QPointF(50, staff.staff_bottoms()["treble"] - 2 * staff.GAP)
>>> staff.mouseMoveEvent(QMouseEvent(QEvent.Type.MouseMove, point, point, Qt.MouseButton.NoButton,
...                                  Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier))
>>> staff._hover
4
```

### ClefInput.leaveEvent

```python
def leaveEvent(event: QEvent) -> None
```

Stop following the pointer when it leaves the staff.

**Parameters**

- `event` (*QEvent*): The leave event.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff._hover = 2
>>> staff.leaveEvent(QEvent(QEvent.Type.Leave))
>>> staff._hover is None
True
```

### ClefInput.mousePressEvent

```python
def mousePressEvent(event: QMouseEvent) -> None
```

Place the symbol on a left click, or choose the next symbol on a right click.

**Parameters**

- `event` (*QMouseEvent*): The mouse press. Nothing happens while the staff is locked.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G", "F"])
>>> staff.resize(400, 300)
>>> from PySide6.QtCore import QPointF
>>> point = QPointF(50, staff.staff_bottoms()["treble"])
>>> staff.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.RightButton,
...                                   Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier))
>>> staff.selected
'F'
```

### ClefInput.wheelEvent

```python
def wheelEvent(event: QWheelEvent) -> None
```

Choose the next symbol for each notch of the wheel turned up, and the one before for each turned down.

**Parameters**

- `event` (*QWheelEvent*): The wheel turn.

**Examples**

```pycon
>>> from PySide6.QtCore import QPoint, QPointF
>>> staff = ClefInput()
>>> staff.reset(["G", "F"])
>>> here = QPointF(50, 50)
>>> staff.wheelEvent(QWheelEvent(here, here, QPoint(0, 0), QPoint(0, 120), Qt.MouseButton.NoButton,
...                              Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False))
>>> staff.selected
'F'
```

### ClefInput.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw the staff, then the symbol that was placed or, until one is, the one that would be placed.

A symbol on a ledger line has the ledger lines it needs drawn behind it.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```pycon
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.place(1)
>>> staff.grab().isNull()
False
```
{% endraw %}
