"""
The staffs you click to place notes or a clef.

One note for the note construction exercise, a row of them for scale construction, and a clef for the clef exercise.

Examples
--------
>>> staff = StaffInput()
>>> staff.accidental is None and not staff.locked
True
"""

from __future__ import annotations

from PySide6.QtCore import (
    QEvent,
    QPointF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QWheelEvent,
)
from PySide6.QtWidgets import QWidget

from alto.settings import (
    CLEF_SYMBOL_NAMES,
    RANGE_LIMITS,
)
from alto.theory.key_signatures import written_signature
from alto.theory.pitch import (
    Note,
    key_accidental,
)
from alto.ui import engraving
from alto.ui.notation import current as current_style
from alto.ui.staff import (
    BOTTOM_LINE,
    KEY_OFFSET,
    KEY_STEP,
    MAX_STEP,
    MIDDLE_C,
    SYMBOL_CLEF,
    StaffWidget,
    draw_signature_sign,
)

WHEEL_NOTCH = 120  # the angle delta of one notch of a mouse wheel
MAX_ACCIDENTALS = 7  # a key signature has at most seven sharps or flats
PREVIEW = QColor(
    53,
    132,
    228,
    170,
)  # the note that follows the pointer


class StaffInput(StaffWidget):
    """
    A single staff you click to place a note, or place a note on with the keyboard.

    The note snaps to the nearest line or space and follows the pointer until you click. Without the mouse, a caret marks
    the note that would be placed: `move_cursor` and `jump_to_letter` move it, and `place_caret` places it.

    Attributes
    ----------
    placed : Signal
        Emitted with the `Note` when you click, using the current `accidental`.
    accidental_cycled : Signal
        Emitted on a right click: the owner steps through natural, sharp and flat.
    caret_moved : Signal
        Emitted when the caret moves.
    accidental : int or None
        The sign you chose (-1 flat, 0 natural, 1 sharp); None follows the key signature.
    locked : bool
        Ignore the mouse (while feedback is showing).
    caret : int or None
        The staff step of the note that the keyboard would place, as `Note.diatonic` counts them; None until the keyboard
        or a click has put it somewhere. Once it has a place the note is shown in the preview color while the pointer is
        away.

    Examples
    --------
    >>> staff = StaffInput()
    >>> staff.reset("treble", key=0)
    >>> staff.resize(400, 300)
    >>> str(staff.note_at(staff.staff_bottoms()["treble"]))  # the bottom line of the treble staff
    'E4'
    """

    placed = Signal(object)
    accidental_cycled = Signal()  # right click: the owner steps through natural, sharp and flat
    caret_moved = Signal()  # the keyboard moved the note that would be placed

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create the staff.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the staff.

        Examples
        --------
        >>> StaffInput().hasMouseTracking()
        True
        """
        super().__init__(parent, max_step=MAX_STEP)
        self.accidental: int | None = None  # the sign you chose (-1 flat, 0 natural, +1 sharp); None follows the key signature
        self.locked = False  # ignore the mouse (while feedback is showing)
        self.caret: int | None = None  # the staff step of the note that the keyboard would place
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def reset(
        self,
        clef: str,
        *,
        key: int = 0,
        caption: str = "",
    ) -> None:
        """
        Clear the staff for a new question, drawing a key signature.

        Parameters
        ----------
        clef : str
            The clef to draw.
        key : int, default 0
            The key signature: that many sharps if positive, flats if negative. Keyword-only.
        caption : str, default ""
            Text to write under the staff. Keyword-only.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.accidental, staff.locked = 1, True
        >>> staff.reset("bass", key=-2)
        >>> staff.accidental is None, staff.locked, staff.key
        (True, False, -2)
        """
        self.accidental, self.locked, self.caret = None, False, None
        self.show_notes([], clef=clef, key=key, caption=caption)

    def note_at(self, y: float) -> Note:
        """
        Return the note on the line or space nearest to a height on the staff.

        The note is kept within five ledger lines of the staff. On a grand staff, a click in the upper half is on the treble
        staff and the lower half on the bass staff.

        Parameters
        ----------
        y : float
            The height in the widget, in pixels from the top.

        Returns
        -------
        Note
            The note, with the chosen accidental or, if none is chosen, the one the key signature gives it.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.reset("treble", key=1)  # G major: F is sharp
        >>> staff.resize(400, 300)
        >>> bottom = staff.staff_bottoms()["treble"]
        >>> str(staff.note_at(bottom - 3 * staff.GAP / 2))  # three steps above E4
        'A4'
        >>> str(staff.note_at(bottom - staff.GAP / 2))  # one step above E4: F, sharp in this key
        'F♯4'
        """
        gap, bottoms = self.GAP, self.staff_bottoms()
        if self.clef == "grand":
            # halfway between middle C as written on the treble staff and the B below it on the bass staff
            top_bottom, bass_bottom = bottoms["treble"], bottoms["bass"]
            c4 = top_bottom - (MIDDLE_C - BOTTOM_LINE["treble"]) * gap / 2
            b3 = bass_bottom - (MIDDLE_C - 1 - BOTTOM_LINE["bass"]) * gap / 2
            if y <= (c4 + b3) / 2:
                diatonic = max(BOTTOM_LINE["treble"] + round((top_bottom - y) / (gap / 2)), MIDDLE_C)
            else:
                diatonic = min(BOTTOM_LINE["bass"] + round((bass_bottom - y) / (gap / 2)), MIDDLE_C - 1)
        else:
            diatonic = BOTTOM_LINE[self.clef] + round((bottoms[self.clef] - y) / (gap / 2))
        return self.note_for(diatonic)

    def note_for(self, diatonic: int) -> Note:
        """
        Return the note on a staff step, with the chosen sign or the one the key signature gives it.

        The step is kept within five ledger lines of the staff, as clicking is.

        Parameters
        ----------
        diatonic : int
            The staff step, as `Note.diatonic` counts them.

        Returns
        -------
        Note
            The note.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.reset("treble", key=1)  # G major: F is sharp
        >>> str(staff.note_for(Note.parse("F4").diatonic))
        'F♯4'
        >>> staff.accidental = 0
        >>> str(staff.note_for(Note.parse("F4").diatonic))
        'F4'
        """
        low, high = RANGE_LIMITS[self.clef]
        diatonic = min(max(diatonic, low), high)
        accidental = self.accidental if self.accidental is not None else key_accidental(diatonic % 7, count=self.key)
        return Note.from_diatonic(diatonic, accidental=accidental)

    def caret_start(self) -> int:
        """
        Return the staff step the caret starts from, when the keyboard first moves it.

        Returns
        -------
        int
            The middle line of the staff, or middle C on a grand staff.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.reset("treble")
        >>> str(Note.from_diatonic(staff.caret_start()))
        'B4'
        >>> staff.reset("grand")
        >>> str(Note.from_diatonic(staff.caret_start()))
        'C4'
        """
        return MIDDLE_C if self.clef == "grand" else BOTTOM_LINE[self.clef] + 4

    def caret_note(self) -> Note | None:
        """
        Return the note that the keyboard would place.

        Returns
        -------
        Note or None
            The note at the caret, with the chosen sign; None if the caret has not been put anywhere.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.reset("bass")
        >>> staff.caret_note() is None
        True
        >>> staff.move_cursor(0)
        >>> str(staff.caret_note())
        'D3'
        """
        return None if self.caret is None else self.note_for(self.caret)

    def move_cursor(self, steps: int) -> None:
        """
        Move the caret up (positive) or down (negative) by staff steps, and show the note there.

        The first move starts from `caret_start`. The caret stays within the furthest ledger lines.

        Parameters
        ----------
        steps : int
            How many lines and spaces to move; 7 is an octave.

        Examples
        --------
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
        """
        low, high = RANGE_LIMITS[self.clef]
        here = self.caret if self.caret is not None else self.caret_start()
        self.caret = min(max(here + steps, low), high)
        self.show_note(self.caret_note(), color=PREVIEW)
        self.caret_moved.emit()

    def jump_to_letter(self, letter: int) -> None:
        """
        Move the caret to the nearest note with a letter name, above or below where it is.

        Parameters
        ----------
        letter : int
            The letter, counting from C as 0: D is 1, E is 2, F is 3, G is 4, A is 5 and B is 6.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.reset("treble")
        >>> staff.move_cursor(0)  # B4, the middle line
        >>> staff.jump_to_letter(0)
        >>> str(staff.caret_note())  # the nearest C is the one just above
        'C5'
        >>> staff.jump_to_letter(4)
        >>> str(staff.caret_note())  # and the nearest G is the one just below
        'G4'
        """
        low, high = RANGE_LIMITS[self.clef]
        here = self.caret if self.caret is not None else self.caret_start()
        reachable = [d for d in range(low, high + 1) if d % 7 == letter]
        self.caret = min(reachable, key=lambda d: (abs(d - here), -d))  # a tie goes to the higher note
        self.show_note(self.caret_note(), color=PREVIEW)
        self.caret_moved.emit()

    def place_caret(self) -> None:
        """
        Place the note at the caret, as a click would.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.reset("treble")
        >>> placed = []
        >>> _ = staff.placed.connect(placed.append)
        >>> staff.place_caret()  # the first press places the note at the start
        >>> [str(n) for n in placed]
        ['B4']
        """
        if self.locked:
            return
        caret = self.caret_start() if self.caret is None else self.caret
        self.caret = caret
        note = self.note_for(caret)
        self.show_note(note)  # solid black: the note you placed
        self.placed.emit(note)

    def show_note(
        self,
        note: Note | None,
        *,
        color: QColor | None = None,
    ) -> None:
        """
        Draw a single note on the staff, or clear it.

        Parameters
        ----------
        note : Note or None
            The note to draw; None clears the staff.
        color : QColor or None, default None
            The color to draw it in; the notation's own ink if None. Keyword-only.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.show_note(Note.parse("C4"))
        >>> len(staff.columns)
        1
        >>> staff.show_note(None)
        >>> staff.columns
        []
        """
        self.columns = [[note]] if note else []
        self.note_color = QColor(color) if color else None
        self.update()

    def refresh_preview(self) -> None:
        """
        Redraw the note that would be placed, for example after the accidental changes.

        It is the pointer's note while the pointer is over the staff, and otherwise the note at the caret, once the keyboard
        has put the caret somewhere.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.refresh_preview()  # the pointer is not over the staff, and there is no caret: nothing to redraw
        >>> staff.columns
        []
        >>> staff.reset("treble")
        >>> staff.move_cursor(0)
        >>> len(staff.columns)  # the note at the caret
        1
        """
        if self.locked:
            return
        if self.underMouse():
            self.show_note(self.note_at(self.mapFromGlobal(self.cursor().pos()).y()), color=PREVIEW)
        elif self.caret is not None:
            self.show_note(self.caret_note(), color=PREVIEW)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Show the note under the pointer, in a lighter color.

        Parameters
        ----------
        event : QMouseEvent
            The mouse move.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.reset("treble")
        >>> staff.resize(400, 300)
        >>> from PySide6.QtCore import QPointF
        >>> point = QPointF(50, staff.staff_bottoms()["treble"])
        >>> staff.mouseMoveEvent(QMouseEvent(QEvent.Type.MouseMove, point, point, Qt.MouseButton.NoButton,
        ...                                  Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier))
        >>> str(staff.columns[0][0])
        'E4'
        """
        if not self.locked:
            self.show_note(self.note_at(event.position().y()), color=PREVIEW)

    def leaveEvent(self, event: QEvent) -> None:
        """
        Remove the pointer's note when the pointer leaves the staff, showing the note at the caret instead if there is one.

        Parameters
        ----------
        event : QEvent
            The leave event.

        Examples
        --------
        >>> staff = StaffInput()
        >>> staff.show_note(Note.parse("C4"))
        >>> staff.leaveEvent(QEvent(QEvent.Type.Leave))
        >>> staff.columns
        []
        """
        if not self.locked:
            self.show_note(self.caret_note(), color=PREVIEW)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Place the note on a left click, or step through the accidentals on a right click.

        Parameters
        ----------
        event : QMouseEvent
            The mouse press. Nothing happens while the staff is locked.

        Examples
        --------
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
        """
        if event.button() == Qt.MouseButton.RightButton and not self.locked:
            self.accidental_cycled.emit()
        elif event.button() == Qt.MouseButton.LeftButton and not self.locked:
            note = self.note_at(event.position().y())
            self.caret = None  # a click leaves nothing behind: the keyboard starts afresh
            self.show_note(note)  # solid black: the note you placed
            self.placed.emit(note)


class ScaleInput(StaffInput):
    """
    A staff you click to place the notes of a scale one after another, left to right, and then, if asked, its steps.

    The next note follows the pointer, snapped to a line or space, in the place it will take. Each click puts it there and
    moves on to the next place. The places are all drawn from the start, so the notes do not move as more are placed.

    When steps are asked for, once all the notes are placed two lines rise from each pair of neighboring notes to a point
    above them (a wedge). The step to be marked next is shown there, in the preview color, as "W" (whole) or "H" (half).
    The mouse wheel or a right click changes it, and a left click marks it and moves on to the next pair.

    Attributes
    ----------
    notes_changed : Signal
        Emitted when a note or a step is placed or taken back.
    step_selected : Signal
        Emitted with "W" or "H" when the step to be marked next changes.
    accidental_stepped : Signal
        Emitted with 1 or -1 for each notch of the mouse wheel while notes are placed: the owner moves on to the next sign
        (1) or back to the one before (-1).
    notes : list of Note
        The notes placed so far, left to right.
    steps : list of str
        The steps marked so far, each "W" or "H".
    slots : int
        How many notes the scale has.
    with_steps : bool
        Whether the steps are asked for too.
    pending_step : str
        The step that a left click would mark next, "W" or "H".

    Examples
    --------
    >>> from PySide6.QtCore import QPointF
    >>> staff = ScaleInput()
    >>> staff.reset_scale("treble", slots=8)
    >>> staff.resize(600, 300)
    >>> point = QPointF(50, staff.staff_bottoms()["treble"])
    >>> staff.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.LeftButton,
    ...                                   Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
    >>> [str(n) for n in staff.notes], len(staff.columns)
    (['E4'], 8)
    """

    notes_changed = Signal()
    step_selected = Signal(str)
    accidental_stepped = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create the staff.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the staff.

        Examples
        --------
        >>> ScaleInput().notes
        []
        """
        super().__init__(parent)
        self.notes: list[Note] = []
        self.steps: list[str] = []
        self.slots = 8
        self.with_steps = False
        self.pending_step = "W"
        self._wheel = 0  # the part of a wheel notch not yet used

    def reset_scale(
        self,
        clef: str,
        *,
        slots: int,
        caption: str = "",
        with_steps: bool = False,
        key: int = 0,
    ) -> None:
        """
        Clear the staff for a new scale: a staff with room for its notes, and the key signature it is to have.

        Parameters
        ----------
        clef : str
            The clef to draw.
        slots : int
            How many notes the scale has. Keyword-only.
        caption : str, default ""
            The name of the scale, written under the staff. Keyword-only.
        with_steps : bool, default False
            Also ask for the steps between the notes. Keyword-only.
        key : int, default 0
            The key signature drawn on the staff: that many sharps if positive, flats if negative. It is the staff's, not
            the scale's: a note placed without a sign takes the sign the signature gives its letter. Keyword-only.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.notes, staff.slots = [Note.parse("C4")], 3
        >>> staff.reset_scale("bass", slots=8, caption="D Major")
        >>> staff.notes, staff.slots, staff.caption, staff.key
        ([], 8, 'D Major', 0)
        >>> staff.reset_scale("bass", slots=8, key=-2)
        >>> staff.key
        -2
        """
        self.notes, self.steps, self.slots, self.with_steps, self.pending_step = [], [], slots, with_steps, "W"
        self.key_room = MAX_ACCIDENTALS  # the staff keeps its width whatever signature it is given
        self.reset(clef, key=key, caption=caption)
        self.set_note_color(None)
        self._redraw(None)

    @property
    def complete(self) -> bool:
        """
        Report whether every note of the scale has been placed.

        Returns
        -------
        bool
            True when there are as many notes as places.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=1)
        >>> staff.complete
        False
        >>> staff.notes.append(Note.parse("C4"))
        >>> staff.complete
        True
        """
        return len(self.notes) >= self.slots

    @property
    def placing_steps(self) -> bool:
        """
        Report whether it is the turn of the steps: they are asked for, every note is placed and some step is still to mark.

        Returns
        -------
        bool
            True while the next click marks a step.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=2, with_steps=True)
        >>> staff.notes.extend([Note.parse("C4"), Note.parse("D4")])
        >>> staff.placing_steps
        True
        >>> staff.steps.append("W")
        >>> staff.placing_steps
        False
        """
        return self.with_steps and self.complete and len(self.steps) < self.slots - 1

    @property
    def done(self) -> bool:
        """
        Report whether everything asked for is placed: every note and, if they are asked for, every step.

        Returns
        -------
        bool
            True when the scale can be handed in.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=2, with_steps=True)
        >>> staff.notes.extend([Note.parse("C4"), Note.parse("D4")])
        >>> staff.done
        False
        >>> staff.steps.append("W")
        >>> staff.done
        True
        """
        return self.complete and (not self.with_steps or len(self.steps) >= self.slots - 1)

    def _redraw(self, preview: Note | None) -> None:
        """
        Draw the placed notes, the pointer's note in the next place, the steps, and empty places for the rest.

        Parameters
        ----------
        preview : Note or None
            The note under the pointer, or None for none.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=4)
        >>> staff.notes.append(Note.parse("C4"))
        >>> staff._redraw(Note.parse("D4"))
        >>> [len(column) for column in staff.columns], sorted(staff.column_colors)
        ([1, 1, 0, 0], [1])
        """
        columns = [[n] for n in self.notes]
        self.column_colors = {}
        if preview is not None and not self.complete:
            self.column_colors[len(columns)] = PREVIEW
            columns.append([preview])
        self.columns = columns + [[] for _ in range(self.slots - len(columns))]
        self.wedges = [*self.steps]
        self.wedge_colors = {}
        if self.placing_steps:  # the step a click would mark, in the next place
            self.wedge_colors[len(self.steps)] = PREVIEW
            self.wedges.append(self.pending_step)
        self.wedges += [""] * (self.slots - 1 - len(self.wedges))
        self._fit_width()
        self.update()

    def show_note(
        self,
        note: Note | None,
        *,
        color: QColor | None = None,
    ) -> None:
        """
        Show the pointer's note in the next place, or take it away.

        Parameters
        ----------
        note : Note or None
            The note to show; None shows none.
        color : QColor or None, default None
            Unused: the note under the pointer is always drawn in the preview color. Keyword-only.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=4)
        >>> staff.show_note(Note.parse("G4"))
        >>> staff.columns[0], staff.notes
        ([Note(octave=4, letter=4, accidental=0)], [])
        """
        self._redraw(note)

    def set_pending_step(self, step: str) -> None:
        """
        Choose the step that the next click marks.

        Parameters
        ----------
        step : str
            "W" for a whole step or "H" for a half step.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=3, with_steps=True)
        >>> chosen = []
        >>> _ = staff.step_selected.connect(chosen.append)
        >>> staff.set_pending_step("H")
        >>> staff.pending_step, chosen
        ('H', ['H'])
        """
        if step != self.pending_step:
            self.pending_step = step
            self._redraw(None)
            self.step_selected.emit(step)

    def toggle_step(self) -> None:
        """
        Switch the step that the next click marks between whole and half.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=3, with_steps=True)
        >>> staff.toggle_step()
        >>> staff.pending_step
        'H'
        >>> staff.toggle_step()
        >>> staff.pending_step
        'W'
        """
        self.set_pending_step("H" if self.pending_step == "W" else "W")

    def undo(self) -> None:
        """
        Take back the last thing placed: the last step if there is one, otherwise the last note.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=4)
        >>> staff.notes.append(Note.parse("C4"))
        >>> staff.undo()
        >>> staff.notes
        []
        """
        if self.locked or not (self.steps or self.notes):
            return
        if self.steps:
            self.steps.pop()
        else:
            self.notes.pop()
        self._redraw(None)
        self.notes_changed.emit()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Use the mouse wheel for what comes next: the sign of the note to place, or the step to mark.

        While notes are placed each notch asks the owner to move on to the next sign (up) or back to the one before (down).
        While steps are marked each notch switches between whole and half. Once everything is placed it does nothing.

        Parameters
        ----------
        event : QWheelEvent
            The wheel turn.

        Examples
        --------
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
        """
        if self.locked or self.done:
            event.ignore()
            return
        event.accept()
        self._wheel += event.angleDelta().y()
        notches = int(self._wheel / WHEEL_NOTCH)  # whole notches, toward zero
        self._wheel -= notches * WHEEL_NOTCH
        if self.placing_steps:
            if abs(notches) % 2:  # two notches are back where they started
                self.toggle_step()
        else:
            for _ in range(abs(notches)):
                self.accidental_stepped.emit(1 if notches > 0 else -1)

    def caret_start(self) -> int:
        """
        Return the staff step the caret starts from: that of the last note placed, or the middle line.

        Returns
        -------
        int
            Where the keyboard's first move begins.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=8)
        >>> str(Note.from_diatonic(staff.caret_start()))  # the middle line
        'B4'
        >>> staff.notes.append(Note.parse("D4"))
        >>> str(Note.from_diatonic(staff.caret_start()))  # the note before
        'D4'
        """
        return self.notes[-1].diatonic if self.notes else super().caret_start()

    def place_next(self, note: Note | None = None) -> None:
        """
        Place the next note, or mark the next step once the notes are placed.

        Parameters
        ----------
        note : Note or None, default None
            The note to place; the note at the caret if None. Ignored while steps are marked.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=2, with_steps=True)
        >>> staff.place_next(Note.parse("C4"))
        >>> staff.place_next(Note.parse("D4"))
        >>> staff.place_next()  # the notes are placed: this marks the first step
        >>> [str(n) for n in staff.notes], staff.steps
        (['C4', 'D4'], ['W'])
        """
        if self.locked:
            return
        if not self.complete:
            if note is None:
                caret = self.caret_start() if self.caret is None else self.caret
                self.caret = caret
                note = self.note_for(caret)
            self.notes.append(note)
        elif self.placing_steps:
            self.steps.append(self.pending_step)
            self.pending_step = "W"  # the step is used up, like a sign: most steps are whole
            self.step_selected.emit("W")
        else:
            return
        self._redraw(None)
        if self.caret is not None:  # the keyboard's next note shows where it would go
            self._redraw(self.caret_note())
        self.notes_changed.emit()

    def place_caret(self) -> None:
        """
        Place the next note at the caret, or mark the next step, as a click would.

        Examples
        --------
        >>> staff = ScaleInput()
        >>> staff.reset_scale("treble", slots=2)
        >>> staff.move_cursor(2)
        >>> staff.place_caret()
        >>> [str(n) for n in staff.notes]
        ['D5']
        """
        self.place_next()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Place the next note or mark the next step on a left click; change the sign or the step on a right click.

        Parameters
        ----------
        event : QMouseEvent
            The mouse press. Nothing happens while the staff is locked or when everything is placed.

        Examples
        --------
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
        """
        if self.locked:
            return
        if event.button() == Qt.MouseButton.RightButton:
            if self.placing_steps:
                self.toggle_step()
            else:
                self.accidental_cycled.emit()
        elif event.button() == Qt.MouseButton.LeftButton:
            self.caret = None  # a click leaves nothing behind: the keyboard carries on from the last note
            self.place_next(None if self.complete else self.note_at(event.position().y()))


class SignatureInput(ScaleInput):
    """
    Place accidentals in consecutive key-signature slots immediately after the clef.

    Examples
    --------
    >>> staff = SignatureInput()
    >>> staff.reset_scale("treble", slots=7, caption="D major")
    >>> staff.place_next(Note.parse("F#5"))
    >>> staff.notes, staff.columns
    ([Note(octave=5, letter=3, accidental=1)], [])
    """

    preview: Note | None = None

    template: tuple[Note | None, ...] = (None,) * MAX_ACCIDENTALS

    def reset_signature(self, clef: str, *, key: int, caption: str, starting_slots: list[int]) -> None:
        """
        Set the fixed signs for this question and clear the learner’s entries.

        Parameters
        ----------
        clef : str
            Clef used to read the positions.
        key : int
            Target signature.
        caption : str
            Name of the key under the staff.
        starting_slots : list of int
            Positions to fill before the learner begins.

        Examples
        --------
        >>> staff = SignatureInput()
        >>> staff.reset_signature("treble", key=2, caption="D major", starting_slots=[1])
        >>> len(staff.template), staff.template[1]
        (7, Note(octave=5, letter=0, accidental=1))
        """
        slots: list[Note | None] = [None] * MAX_ACCIDENTALS
        if starting_slots:
            for i, note in enumerate(written_signature(clef, key=key)):
                if i in starting_slots:
                    slots[i] = note
        self.template = tuple(slots)
        self.reset_scale(clef, slots=self.template.count(None), caption=caption)

    def entered_signature(self) -> list[Note | None]:
        """
        Combine the fixed signs and the learner's entries in staff order.

        Returns
        -------
        list of Note or None
            One pitch per occupied slot, with None in each remaining gap.

        Examples
        --------
        >>> staff = SignatureInput()
        >>> staff.reset_signature("treble", key=2, caption="D major", starting_slots=[1])
        >>> staff.place_next(Note.parse("F#5"))
        >>> [str(n) for n in staff.entered_signature() if n is not None]
        ['F♯5', 'C♯5']
        """
        entered = iter(self.notes)
        return [fixed if fixed is not None else next(entered, None) for fixed in self.template]

    def _redraw(self, preview: Note | None) -> None:
        """
        Update the next sign without adding any noteheads to the staff.

        Parameters
        ----------
        preview : Note or None
            Pitch under the pointer or keyboard caret.

        Examples
        --------
        >>> staff = SignatureInput()
        >>> staff._redraw(Note.parse("C#5"))
        >>> str(staff.preview)
        'C♯5'
        """
        self.preview = None if self.complete else preview
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw the blank staff and caption, then the placed signs and the next sign under the pointer.

        Parameters
        ----------
        event : QPaintEvent
            The paint request.

        Examples
        --------
        >>> staff = SignatureInput()
        >>> staff.reset_scale("bass", slots=7)
        >>> staff.place_next(Note.parse("Bb2"))
        >>> staff.grab().isNull()
        False
        """
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bottom = self.staff_bottoms()[self.clef]
        font = (self.notation_style or current_style()).font
        signs = self.entered_signature()
        preview_slot = signs.index(None) if self.preview is not None and not self.locked and None in signs else -1
        for i, note in enumerate(signs):
            ink = QColor("black") if self.template[i] is not None else self.note_color or QColor("black")
            if i == preview_slot:
                note, ink = self.preview, PREVIEW
            if note is None:
                continue
            y = bottom - (note.diatonic - BOTTOM_LINE[self.clef]) * self.GAP / 2
            draw_signature_sign(
                painter,
                sign=note.accidental,
                x=self.side + KEY_OFFSET + i * KEY_STEP,
                y=y,
                gap=self.GAP,
                color=ink,
                font=font,
            )
        painter.end()


class ClefInput(StaffWidget):
    """
    A blank staff on which you put a clef symbol: choose the G, C or F clef, then click where it goes.

    The symbol can go on any line or space of the staff and on the three ledger lines and spaces above and below it, and
    follows the pointer from place to place, in a lighter color, until you click. Without the mouse, `move_caret` moves it,
    `step_symbol` switches the symbol and `place_caret` places it.

    Attributes
    ----------
    placed : Signal
        Emitted with the symbol ("G", "C" or "F") and its place when you click: 0 is the bottom line, 1 the space above it, up to
        8 for the top line, with -6 to 14 allowed.
    changed : Signal
        Emitted when the symbol chosen or the place the keyboard would use changes.
    options : list of str
        The symbols that can be chosen, in the order the wheel goes through them.
    selected : str
        The symbol chosen now.
    locked : bool
        Ignore the mouse and the wheel (while feedback is showing).
    caret : int or None
        The place the keyboard would put the symbol; None until the keyboard has moved it.
    placed_symbol : str or None
        The symbol that has been placed and is drawn solid, with `placed_step` its place; None until one is.

    Examples
    --------
    >>> staff = ClefInput()
    >>> staff.reset(["G", "F"])
    >>> staff.step_symbol(1)
    >>> staff.selected
    'F'
    """

    placed = Signal(str, int)
    changed = Signal()
    LOWEST, HIGHEST = -6, 14  # the third ledger line below the staff and the third above it

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create the staff.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the staff.

        Examples
        --------
        >>> ClefInput().hasMouseTracking()
        True
        """
        super().__init__(parent, max_step=MAX_STEP, margin=10.0)  # room above and below for the symbol on the ledger lines
        self.options = ["G"]
        self.selected = "G"
        self.locked = False
        self.caret: int | None = None
        self.placed_symbol: str | None = None
        self.placed_step = 0
        self.clef_color: QColor | None = None  # the color of the symbol placed, for feedback; None is black
        self._hover: int | None = None  # the place under the pointer
        self._wheel = 0  # the part of a wheel notch not yet used
        self.clef_hidden = True
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def reset(
        self,
        options: list[str],
        *,
        caption: str = "",
    ) -> None:
        """
        Clear the staff for a new question and offer some symbols to choose from.

        Parameters
        ----------
        options : list of str
            The symbols the wheel goes through, any of "G", "C" and "F"; the first is chosen to begin with.
        caption : str, default ""
            The question, written under the staff. Keyword-only.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["C", "F"], caption="Place the alto clef.")
        >>> staff.selected, staff.placed_symbol, staff.caption
        ('C', None, 'Place the alto clef.')
        """
        self.options = options or ["G"]
        self.selected = self.options[0]
        self.locked, self.caret, self.placed_symbol, self.clef_color, self._hover = False, None, None, None, None
        self.show_notes([], clef="treble", caption=caption)
        self.setToolTip(f"{CLEF_SYMBOL_NAMES[self.selected]} chosen")
        self.update()

    def select(self, symbol: str) -> None:
        """
        Choose a symbol.

        Parameters
        ----------
        symbol : str
            "G", "C" or "F"; one that is not among the options is ignored.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G", "C", "F"])
        >>> staff.select("F")
        >>> staff.selected
        'F'
        """
        if self.locked or symbol not in self.options or symbol == self.selected:
            return
        self.selected = symbol
        self.setToolTip(f"{CLEF_SYMBOL_NAMES[symbol]} chosen")  # for a screen reader and the pointer
        self.update()
        self.changed.emit()

    def step_symbol(self, direction: int) -> None:
        """
        Choose the next symbol of the options, or the one before, going around.

        Parameters
        ----------
        direction : int
            1 for the next, -1 for the one before.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G", "C", "F"])
        >>> staff.step_symbol(-1)
        >>> staff.selected
        'F'
        """
        index = self.options.index(self.selected) if self.selected in self.options else 0
        self.select(self.options[(index + direction) % len(self.options)])

    def step_at(self, y: float) -> int:
        """
        Return the line or space nearest to a height in the widget.

        Parameters
        ----------
        y : float
            The height, in pixels.

        Returns
        -------
        int
            The place, 0 for the bottom line and 1 for the space above it, up to 8 for the top line; from the first ledger line
            below the staff (-6) to the third above it (14).

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G"])
        >>> staff.resize(400, 300)
        >>> floor = staff.staff_bottoms()["treble"]
        >>> staff.step_at(floor), staff.step_at(floor - 1.4 * staff.GAP), staff.step_at(0), staff.step_at(10_000)
        (0, 3, 14, -6)
        """
        base = self.staff_bottoms()["treble"]
        return max(self.LOWEST, min(self.HIGHEST, round((base - y) / (self.GAP / 2))))

    def move_caret(self, steps: int) -> None:
        """
        Move the place the keyboard would put the symbol.

        Parameters
        ----------
        steps : int
            How many lines and spaces up (positive) or down, stopping at the last ledger lines; the first move starts from the
            middle line.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G"])
        >>> staff.move_caret(1)
        >>> staff.caret
        5
        >>> staff.move_caret(20)
        >>> staff.caret
        14
        """
        if self.locked:
            return
        self.caret = max(self.LOWEST, min(self.HIGHEST, (4 if self.caret is None else self.caret) + steps))
        self.update()
        self.changed.emit()

    def place(self, step: int) -> None:
        """
        Put the chosen symbol in a place, drawn solid, and say so.

        Parameters
        ----------
        step : int
            The place, 0 for the bottom line, 1 for the space above it and so on.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["F"])
        >>> got = []
        >>> _ = staff.placed.connect(lambda symbol, where: got.append((symbol, where)))
        >>> staff.place(6)
        >>> got, staff.placed_symbol, staff.placed_step
        ([('F', 6)], 'F', 6)
        """
        if self.locked:
            return
        self.caret = None
        self.placed_symbol, self.placed_step, self.clef_color = self.selected, step, None
        self.update()
        self.placed.emit(self.selected, step)

    def place_caret(self) -> None:
        """
        Place the symbol where the keyboard put it, or on the middle line if it has not moved.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G"])
        >>> staff.move_caret(-2)
        >>> staff.place_caret()
        >>> staff.placed_step
        2
        """
        self.place(4 if self.caret is None else self.caret)

    def clear_placed(self) -> None:
        """
        Take the placed symbol off the staff, so another can be tried.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.place(1)
        >>> staff.clear_placed()
        >>> staff.placed_symbol is None
        True
        """
        self.placed_symbol, self.clef_color = None, None
        self.update()

    def set_clef_color(self, color: QColor | None) -> None:
        """
        Draw the placed symbol in a color, for feedback, or back in black.

        Parameters
        ----------
        color : QColor or None
            The color; None for black.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.set_clef_color(QColor("#2e7d32"))
        >>> staff.clef_color == QColor("#2e7d32")
        True
        """
        self.clef_color = QColor(color) if color is not None else None
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Show the symbol in the place under the pointer, in a lighter color.

        Parameters
        ----------
        event : QMouseEvent
            The mouse move.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G"])
        >>> staff.resize(400, 300)
        >>> from PySide6.QtCore import QPointF
        >>> point = QPointF(50, staff.staff_bottoms()["treble"] - 2 * staff.GAP)
        >>> staff.mouseMoveEvent(QMouseEvent(QEvent.Type.MouseMove, point, point, Qt.MouseButton.NoButton,
        ...                                  Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier))
        >>> staff._hover
        4
        """
        if not self.locked:
            self._hover = self.step_at(event.position().y())
            self.update()

    def leaveEvent(self, event: QEvent) -> None:
        """
        Stop following the pointer when it leaves the staff.

        Parameters
        ----------
        event : QEvent
            The leave event.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff._hover = 2
        >>> staff.leaveEvent(QEvent(QEvent.Type.Leave))
        >>> staff._hover is None
        True
        """
        self._hover = None
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Place the symbol on a left click, or choose the next symbol on a right click.

        Parameters
        ----------
        event : QMouseEvent
            The mouse press. Nothing happens while the staff is locked.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G", "F"])
        >>> staff.resize(400, 300)
        >>> from PySide6.QtCore import QPointF
        >>> point = QPointF(50, staff.staff_bottoms()["treble"])
        >>> staff.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.RightButton,
        ...                                   Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier))
        >>> staff.selected
        'F'
        """
        if self.locked:
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.step_symbol(1)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.place(self.step_at(event.position().y()))

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Choose the next symbol for each notch of the wheel turned up, and the one before for each turned down.

        Parameters
        ----------
        event : QWheelEvent
            The wheel turn.

        Examples
        --------
        >>> from PySide6.QtCore import QPoint, QPointF
        >>> staff = ClefInput()
        >>> staff.reset(["G", "F"])
        >>> here = QPointF(50, 50)
        >>> staff.wheelEvent(QWheelEvent(here, here, QPoint(0, 0), QPoint(0, 120), Qt.MouseButton.NoButton,
        ...                              Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False))
        >>> staff.selected
        'F'
        """
        if self.locked:
            event.ignore()
            return
        event.accept()
        self._wheel += event.angleDelta().y()
        notches = int(self._wheel / WHEEL_NOTCH)
        self._wheel -= notches * WHEEL_NOTCH
        for _ in range(abs(notches)):
            self.step_symbol(1 if notches > 0 else -1)

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the staff, then the symbol that was placed or, until one is, the one that would be placed.

        A symbol on a ledger line has the ledger lines it needs drawn behind it.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request; the whole widget is always redrawn.

        Examples
        --------
        >>> staff = ClefInput()
        >>> staff.reset(["G"])
        >>> staff.place(1)
        >>> staff.grab().isNull()
        False
        """
        super().paintEvent(_)
        if self.placed_symbol is not None:
            symbol, step, color = self.placed_symbol, self.placed_step, self.clef_color or QColor("black")
        else:
            step = self._hover if self._hover is not None else self.caret
            if step is None or self.locked:
                return
            symbol, color = self.selected, PREVIEW
        gap = self.GAP
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        look = self.notation_style or current_style()
        base = self.staff_bottoms()["treble"]
        left = self.side + 8
        ink = QColor("black")
        p.setPen(QPen(ink, 1.2))
        for ledger in range(-2, step - 1, -2) if step < 0 else range(10, step + 1, 2):  # the lines the symbol sits on or beyond
            p.drawLine(QPointF(left - 4, base - ledger * gap / 2), QPointF(left + 4 * gap, base - ledger * gap / 2))
        clef = SYMBOL_CLEF[symbol]
        reference = 2 * engraving.CLEF_SIGNS[clef][1]  # where that clef has its own reference line
        self._draw_clef(
            p,
            clef=clef,
            x=left,
            bottom=base - (step - reference) * gap / 2,  # its reference line goes where the symbol was put
            gap=gap,
            color=color,
            font=look.font,
        )
        p.end()
