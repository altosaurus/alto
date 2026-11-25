"""
The reference pane: an interactive circle of fifths to look things up
on, with an explanation under it.

Click a key on either ring, or move with the arrow keys, and the circle
lights that key's chords, shows its key signature in
the middle, and the text underneath explains it.

Examples
--------
>>> circle = ExplorableCircle()
>>> circle.select("outer", place=2)
>>> circle.title, circle.signature
('D major', 2)
"""

from __future__ import annotations

import html
import math
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QEvent,
    QPointF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QKeyEvent,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.exercises.library import (
    CLEF_FACTS,
    CircleOfFifths,
    ClefBasics,
    IntervalConstruction,
    IntervalNames,
    KeyboardIntervals,
    KeyboardNotes,
    KeySignatureConstruction,
    KeySignatures,
    NotationIdentification,
    NoteConstruction,
    NoteNames,
    OrderOfKeys,
    RythmicEquations,
    ScaleIdentification,
)
from alto.exercises.packs import PackExercise
from alto.lessons import (
    LESSONS,
    Lesson,
)
from alto.theory.fifths import (
    INTRO,
    MAJORS,
    MINORS,
    SIGNATURES,
    cells_of_key,
    explain,
)
from alto.theory.scales import format_key_signature
from alto.ui.circle import (
    DISC,
    OUTER_FROM,
    WEDGE,
    FifthsCircle,
)
from alto.ui.pictures import ClefPictures
from alto.ui.scale_explorer import ScaleExplorer
from alto.ui.widgets import vertical_scroll_area
from alto.ui.zoom import px

if TYPE_CHECKING:
    from alto.exercises.base import Exercise

# how bright the cell under the pointer is, so that it shows what a
# click will pick
HOVER_LIFT = 0.2


class ExplorableCircle(FifthsCircle):
    """
    A circle of fifths that shows every key and lets you pick one.

    Attributes
    ----------
    cell : tuple of (str, int) or None
        The cell that is picked: its ring ("outer" or "inner") and its
        place clockwise from the top; None for none.
    hover : tuple of (str, int) or None
        The cell under the pointer.
    interactive : bool
        Whether the circle answers the mouse and the keys. A picture of
        the circle that only the program changes has it off.

    picked : Signal
        Emitted with the ring and place when a cell is picked, or with
        "" and -1 when the pick is cleared.

    Examples
    --------
    >>> circle = ExplorableCircle()
    >>> circle.cell, circle.title
    (None, 'Circle of fifths')
    """

    picked = Signal(str, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the circle with every key named and none picked.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> ExplorableCircle().shown["inner"] == set(
        ...     range(12)
        ... )
        True
        """
        super().__init__(parent)
        self.cell: tuple[str, int] | None = None
        self.hover: tuple[str, int] | None = None
        self.interactive = True
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(px(280), px(280))
        self.clear()

    def set_interactive(self, interactive: bool) -> None:
        """
        Let the circle be clicked and moved with the keys, or make it a
        picture.

        Parameters
        ----------
        interactive : bool
            True to answer the mouse and the keys.

        Examples
        --------
        >>> circle = ExplorableCircle()
        >>> circle.set_interactive(False)
        >>> (
        ...     circle.interactive,
        ...     circle.focusPolicy()
        ...     == Qt.FocusPolicy.NoFocus,
        ... )
        (False, True)
        """
        self.interactive = interactive
        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
            if interactive
            else Qt.FocusPolicy.NoFocus,
        )
        self._hover_over(None)

    def clear(self) -> None:
        """
        Pick nothing: every key is named, none is lit and the middle
        says what to do.

        Examples
        --------
        >>> circle = ExplorableCircle()
        >>> circle.select("outer", place=4)
        >>> circle.clear()
        >>> circle.cell, circle.signature, circle.lit
        (None, None, set())
        """
        self.reset()
        self.cell = None
        everyone = set(range(12))
        self.shown = {"outer": set(everyone), "inner": set(everyone)}
        self.title = "Circle of fifths"
        self.subtitle = "pick a key"
        self.setAccessibleDescription(
            (
                "Outer ring: the twelve major keys. Inner ring: their "
                "relative minors. No key picked."
            ),
        )
        self.update()
        self.picked.emit("", -1)

    def select(
        self,
        ring: str,
        *,
        place: int,
    ) -> None:
        """
        Pick a cell: light the chords of its key, and show its name and
        key signature in the middle.

        A minor key has the key signature, and the chords, of its
        relative major.

        Parameters
        ----------
        ring : str
            "outer" for the major key at the place, "inner" for its
            relative minor.
        place : int
            The place, clockwise from the top. Keyword-only.

        Examples
        --------
        >>> circle = ExplorableCircle()
        >>> circle.select("inner", place=3)
        >>> (
        ...     circle.title,
        ...     circle.subtitle,
        ...     sorted(circle.lit),
        ...     circle.numerals[("outer", 4)],
        ... )
        ('F♯ minor', '3 sharps', [2, 3, 4], 'V')
        """
        place %= 12
        self.reset()
        self.cell = (ring, place)
        everyone = set(range(12))
        # draws the key's six chords lit, with their numerals, and its
        # staff in the middle
        self.kind = "numeral"
        self._place = self._key = place
        self.target = self.cell
        self.shown = {"outer": set(everyone), "inner": set(everyone)}
        self.lit = {(place + step) % 12 for step in (-1, 0, 1)}
        self.numerals = cells_of_key(place)
        self.signature = SIGNATURES[place]
        self.title = (
            f"{MAJORS[place][0]} major"
            if ring == "outer"
            else f"{MINORS[place][0][:-1]} minor"
        )
        self.subtitle = format_key_signature(SIGNATURES[place])
        self._glow = 1.0
        self.setAccessibleDescription(
            f"{self.title}, {self.subtitle}. " + self._describe(answered=True),
        )
        self.update()
        self.picked.emit(ring, place)

    def cell_at(self, point: QPointF) -> tuple[str, int] | None:
        """
        Return the cell under a point.

        Parameters
        ----------
        point : QPointF
            A position in the widget.

        Returns
        -------
        tuple of (str, int) or None
            The ring and place, or None for the middle disc or outside
            the circle.

        Examples
        --------
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
        """
        center, radius = self.geometry_of()
        dx, dy = point.x() - center.x(), point.y() - center.y()
        far = math.hypot(dx, dy) / radius
        if far > 1.0 or far < DISC:
            return None
        angle = math.degrees(math.atan2(dx, -dy))  # clockwise from the top
        place = int(((angle + WEDGE / 2) % 360.0) // WEDGE)
        return ("outer" if far >= OUTER_FROM else "inner"), place

    def lift_of(
        self,
        ring: str,
        *,
        place: int,
    ) -> float:
        """
        Return how bright a cell is drawn: as for any question, and a
        little brighter under the pointer.

        Parameters
        ----------
        ring : str
            "outer" or "inner".
        place : int
            The place clockwise from the top. Keyword-only.

        Returns
        -------
        float
            The brightness, from 0 to 1.

        Examples
        --------
        >>> circle = ExplorableCircle()
        >>> circle.hover = ("outer", 5)
        >>> (
        ...     circle.lift_of("outer", place=5),
        ...     circle.lift_of("outer", place=6),
        ... )
        (0.2, 0.0)
        """
        lift = super().lift_of(ring, place=place)
        return max(lift, HOVER_LIFT) if self.hover == (ring, place) else lift

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Pick the cell that is clicked; a click in the middle clears the
        pick.

        Parameters
        ----------
        event : QMouseEvent
            The click.

        Examples
        --------
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
        """
        if event.button() != Qt.MouseButton.LeftButton or not self.interactive:
            return
        hit = self.cell_at(event.position())
        self.setFocus()
        if hit is not None:
            self.select(hit[0], place=hit[1])
        else:
            self.clear()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Light the cell under the pointer, and show a hand over the ones
        that can be picked.

        Parameters
        ----------
        event : QMouseEvent
            The move.

        Examples
        --------
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
        """
        self._hover_over(
            self.cell_at(event.position()) if self.interactive else None,
        )

    def leaveEvent(self, event: QEvent) -> None:
        """
        Stop lighting a cell once the pointer has left.

        Parameters
        ----------
        event : QEvent
            The event.

        Examples
        --------
        >>> circle = ExplorableCircle()
        >>> circle.hover = ("outer", 1)
        >>> circle.leaveEvent(QEvent(QEvent.Type.Leave))
        >>> circle.hover is None
        True
        """
        self._hover_over(None)
        super().leaveEvent(event)

    def _hover_over(self, cell: tuple[str, int] | None) -> None:
        """
        Note which cell the pointer is over, and redraw if it changed.

        Parameters
        ----------
        cell : tuple of (str, int) or None
            The cell, or None for none.

        Examples
        --------
        >>> circle = ExplorableCircle()
        >>> circle._hover_over(("inner", 2))
        >>> (
        ...     circle.hover,
        ...     circle.cursor().shape()
        ...     == Qt.CursorShape.PointingHandCursor,
        ... )
        (('inner', 2), True)
        """
        if cell != self.hover:
            self.hover = cell
            self.update()
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if cell is not None
            else Qt.CursorShape.ArrowCursor,
        )

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Move the pick with the arrow keys: Left and Right around the
        circle, Up and Down between the rings.

        Escape clears the pick, and Home picks C major.

        Parameters
        ----------
        event : QKeyEvent
            The key.

        Examples
        --------
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
        """
        if not self.interactive:
            super().keyPressEvent(event)
            return
        key = event.key()
        ring, place = self.cell if self.cell is not None else ("outer", -1)
        if key == Qt.Key.Key_Escape:
            self.clear()
        elif key == Qt.Key.Key_Home:
            self.select("outer", place=0)
        elif key in {Qt.Key.Key_Right, Qt.Key.Key_Left}:
            self.select(
                ring,
                place=place + (1 if key == Qt.Key.Key_Right else -1),
            )
        elif key in {Qt.Key.Key_Up, Qt.Key.Key_Down}:
            self.select(
                "inner" if key == Qt.Key.Key_Down else "outer",
                place=max(place, 0),
            )
        else:
            super().keyPressEvent(event)


class ReferencePanel(QWidget):
    """
    The reference for the circle of fifths: a short description, the
    circle to explore, and what the picked key means.

    Attributes
    ----------
    circle : ExplorableCircle
        The circle to pick a key on.
    explanation : QLabel
        The text under the circle, which follows the pick.
    lesson_button : QPushButton
        Opens the lesson on the circle of fifths.
    lesson_requested : Signal
        Emitted with the key of the lesson to open when that button is
        pressed.

    Examples
    --------
    >>> panel = ReferencePanel()
    >>> panel.circle.select("outer", place=1)
    >>> "<b>G major</b>" in panel.explanation.text()
    True
    """

    lesson_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the panel with nothing picked.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> panel = ReferencePanel()
        >>> panel.explanation.text() == ""
        False
        """
        super().__init__(parent)
        intro = QLabel(INTRO)
        intro.setWordWrap(True)
        intro.setTextFormat(Qt.TextFormat.PlainText)
        self.circle = ExplorableCircle()
        self.explanation = QLabel()
        self.explanation.setWordWrap(True)
        self.explanation.setTextFormat(Qt.TextFormat.RichText)
        self.explanation.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.explanation.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse,
        )
        self.explanation.setAccessibleName("About the key")
        scroll = vertical_scroll_area(self.explanation)
        scroll.setMinimumHeight(px(150))
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.lesson_button = QPushButton(
            "New to this? Take the full lesson  →",
        )
        self.lesson_button.setToolTip(
            (
                "A step-by-step lesson on the circle of fifths, with small"
                " exercises"
            ),
        )
        self.lesson_button.clicked.connect(
            lambda: self.lesson_requested.emit("circle-of-fifths"),
        )
        lay.addWidget(
            self.lesson_button,
        )  # at the top, where it is seen before the reading starts
        lay.addWidget(intro)
        lay.addWidget(self.circle, 3)
        lay.addWidget(scroll, 2)
        self.circle.picked.connect(
            lambda ring, place: self._explain(ring, place=place),
        )
        self._explain("", place=-1)

    def _explain(
        self,
        ring: str,
        *,
        place: int,
    ) -> None:
        """
        Write what the picked key means under the circle.

        Parameters
        ----------
        ring : str
            "outer" or "inner"; "" when nothing is picked.
        place : int
            The place on the circle; -1 when nothing is picked.
            Keyword-only.

        Examples
        --------
        >>> panel = ReferencePanel()
        >>> panel._explain("inner", place=0)
        >>> "relative major, <b>C major</b>" in panel.explanation.text()
        True
        """
        if place < 0:
            self.explanation.setText(
                "<p>Pick a key on the circle to see its key signature, "
                "where it comes from, its relative key and its "
                "chords. Click the middle to start again.</p>",
            )
        else:
            self.explanation.setText(explain(ring, place=place))


CLEF_INTRO = (
    "Every clef is one of three symbols put on a line of the staff. The G "
    "clef circles the G above middle C, the F clef has its "
    "dots either side of the F below middle C, and a C clef is centered on "
    "middle C. Which clef it is depends on the line."
)


class ClefReferencePanel(QWidget):
    """
    The reference for the clefs: how they are made, and a picture of
    each with where its symbol goes.

    Attributes
    ----------
    lesson_button : QPushButton
        Opens the lesson on the clefs.
    lesson_requested : Signal
        Emitted with the key of the lesson to open when that button is
        pressed.
    rows : dict of str to QLabel
        The words beside the picture of each clef, by clef.

    Examples
    --------
    >>> panel = ClefReferencePanel()
    >>> "C clef" in panel.rows[
    ...     "mezzo"
    ... ].text() and "bottom line" in panel.rows[
    ...     "french"
    ... ].text()
    True
    """

    lesson_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the panel: the lesson button, a line of explanation and a
        row for each clef.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> len(ClefReferencePanel().rows) == len(
        ...     settings.CLEF_BASICS_CLEFS
        ... )
        True
        """
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.lesson_button = QPushButton(
            "New to this? Take the full lesson  →",
        )
        self.lesson_button.setToolTip(
            "A step-by-step lesson on the clefs, with small exercises",
        )
        self.lesson_button.clicked.connect(
            lambda: self.lesson_requested.emit("clef-basics"),
        )
        lay.addWidget(
            self.lesson_button,
        )  # at the top, where it is seen before the reading starts
        intro = QLabel(CLEF_INTRO)
        intro.setWordWrap(True)
        intro.setTextFormat(Qt.TextFormat.PlainText)
        lay.addWidget(intro)
        body = QWidget()
        rows = QVBoxLayout(body)
        rows.setContentsMargins(0, 0, 0, 0)
        self.rows: dict[str, QLabel] = {}
        for clef in settings.CLEF_BASICS_CLEFS:
            line = QHBoxLayout()
            line.addWidget(
                ClefPictures([clef], scale=1.2),
                0,
                Qt.AlignmentFlag.AlignTop,
            )
            words = QLabel(
                f"<b>{settings.CLEF_NAMES[clef]}</b><br>{CLEF_FACTS[clef]}",
            )
            words.setWordWrap(True)
            words.setTextFormat(Qt.TextFormat.RichText)
            words.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse,
            )
            line.addWidget(words, 1)
            rows.addLayout(line)
            self.rows[clef] = words
        rows.addStretch(1)
        scroll = vertical_scroll_area(body)
        lay.addWidget(scroll, 1)


class ScaleReferencePanel(QWidget):
    """Scale identification hints and a link to the guided lesson."""

    lesson_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build a scrollable guide to tonic reading and scale patterns.
        """
        super().__init__(parent)
        lay = QVBoxLayout(self)
        self.lesson_button = QPushButton(
            "New to this? Take the full lesson  →",
        )
        self.lesson_button.clicked.connect(
            lambda: self.lesson_requested.emit("scale-identification"),
        )
        lay.addWidget(self.lesson_button)
        text = QLabel(
            "<h3>Identifying a scale</h3><p>Read the clef and first note to"
            " find the tonic. Apply the staff key signature "
            "and any written accidentals, then count the gaps between "
            "notes.</p>"
            "<p>W = whole step (2 semitones); H = half step (1 semitone); "
            "3H = 3 semitones. "
            "The key signature alone does not identify the scale.</p>"
            "<p>Melodic minor uses its ascending form here. Change the "
            "example below to compare scales.</p>",
        )
        text.setWordWrap(True)
        text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse,
        )
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        contents = QVBoxLayout(body)
        contents.addWidget(text)
        self.explorer = ScaleExplorer()
        contents.addWidget(self.explorer)
        contents.addStretch()
        scroll.setWidget(body)
        lay.addWidget(scroll, 1)


_READING_HINTS = {
    RythmicEquations: (
        "<p>Count each side in the same units. With a quarter note as "
        "one beat, a half note counts as two and a whole note as four. "
        "A rest counts for the same time as its matching note.</p>"
    ),
    KeySignatures: (
        "<p>For major, go a half step above the last sharp or read the "
        "next-to-last flat. One flat gives F major, "
        "and an empty signature gives C major. For minor, take the sixth "
        "note of that major scale. "
        "For Dorian, take its second note.</p>"
    ),
    OrderOfKeys: (
        "<p>Write sharps in the order F C G D A E B. Write flats in the "
        "reverse order, B E A D G C F. "
        "Stop once you have written all the signs for the key. In treble "
        "clef, start sharps on the top line "
        "and flats on the middle line. In bass clef, start sharps on the "
        "fourth line and flats on the second line.</p>"
    ),
    KeySignatureConstruction: (
        "<p>D major needs F♯ and C♯, so choose two sharps. E♭ major needs "
        "B♭, E♭, and A♭, so choose three flats. "
        "A minor shares the signature of C major. Choose ♮ to leave the "
        "staff empty.</p>"
    ),
    IntervalConstruction: (
        "<p>Count the starting note as one. For a major third above C, "
        "count C, D, E. "
        "C to E spans four half steps. For a minor third, lower E to E♭ to "
        "make three half steps.</p>"
    ),
    IntervalNames: (
        "<p>Count letter names from the lower note to the higher, including"
        " both notes. "
        "C to E and C to E♭ are both thirds. Count half steps to find the "
        "quality. "
        "A major third (M3) spans four half steps, and a minor third (m3) "
        "spans three.</p>"
        "<p>With <b>Inversions</b> on, read the written interval first. For"
        " C up to E, move C up an octave. "
        "E up to C is a minor sixth. Simple interval numbers add up to nine"
        " with their inversions. "
        "Major and minor swap, augmented and diminished swap, and perfect "
        "stays perfect.</p>"
    ),
    KeyboardIntervals: (
        "<p>Start at zero on the lower highlighted key. Count each move to "
        "the next key, black or white. "
        "Choose m3 for three half steps, M3 for four, P4 for five, or P5 "
        "for seven. "
        "At six half steps, use the combined A4 / d5 answer.</p>"
    ),
    NotationIdentification: (
        "<p>Look at the shape and what it touches. The <b>notehead</b> is "
        "the oval that sits on a line or in a space. "
        "The <b>stem</b> is the vertical stroke attached to it and can "
        "point up or down.</p>"
        "<p>A <b>staff line</b> runs horizontally across the music. The "
        "<b>clef</b> at the left tells you which "
        "pitches the lines and spaces represent.</p>"
        "<p>For other symbols, look at their position. Accidentals sit "
        "immediately before a note, articulations sit near "
        "the note, and dynamic markings such as <i>p</i> and <i>f</i> "
        "usually sit below the staff. A tie joins notes "
        "of the same pitch. A slur groups notes into a phrase.</p>"
    ),
    KeyboardNotes: (
        "<p>Find a pair of black keys. The white key just to its left is C."
        " Moving right, the white keys are "
        "C D E F G A B, then C again. F is just left of a group of three "
        "black keys.</p>"
        "<p>For a black key, look at both neighbors. The black key between "
        "C and D can be called C♯ or D♭. "
        "If the question shows a key signature, use it to help choose the "
        "spelling.</p>"
    ),
    NoteNames: (
        "<p>Start at a line you know. In treble clef the second line is G4."
        " In bass clef the fourth line is F3. "
        "The center of a C clef marks middle C. Count lines from the "
        "bottom.</p>"
        "<p>Trace each line and space from your landmark to the notehead, "
        "moving one letter at a time. "
        "Apply the sharps or flats after the clef, then any sign beside the"
        " note. If asked for an octave, "
        "remember that the number changes at C.</p>"
    ),
    NoteConstruction: (
        "<p>For Notes Only, read the requested note name. For Scale and "
        "Degree, start on the first note of the "
        "named scale (the tonic) and count it as degree 1. For example, "
        "degree 2 in C major is D.</p>"
        "<p>Find the letter’s line or space using the clef. If an octave is"
        " given, choose that occurrence. "
        "Check the key signature at the start of the staff. If it makes "
        "every F sharp and you need F natural, "
        "choose the natural sign (♮) before placing the note.</p>"
    ),
}


class NoteReferencePanel(QWidget):
    """
    Hints for reading notes or intervals and a link to the associated
    lesson.
    """

    lesson_requested = Signal(str)

    def __init__(self, exercise: Exercise) -> None:
        """
        Show the hints for the current note exercise.

        Parameters
        ----------
        exercise : Exercise
            The note exercise whose reference was opened.

        Examples
        --------
        >>> NoteReferencePanel(
        ...     KeyboardNotes()
        ... ).lesson_button.text()
        'New to this? Take the full lesson  →'
        """
        super().__init__()
        layout = QVBoxLayout(self)
        self.lesson_button = QPushButton(
            "New to this? Take the full lesson  →",
        )
        name = type(exercise).__name__
        lesson = next(
            lesson
            for lesson in LESSONS
            if name in (lesson.exercise, *lesson.related_exercises)
        )
        self.lesson_button.setToolTip(f"Open {lesson.title}")
        self.lesson_button.clicked.connect(
            lambda: self.lesson_requested.emit(lesson.key),
        )
        layout.addWidget(self.lesson_button)
        hints = QLabel(
            f"<h3>{exercise.name}</h3>{_READING_HINTS[type(exercise)]}",
        )
        hints.setWordWrap(True)
        hints.setAlignment(Qt.AlignmentFlag.AlignTop)
        hints.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse,
        )
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setWidget(hints)
        layout.addWidget(scroll, 1)


class PluginReferencePanel(QWidget):
    """
    What a plugin's exercise offers to look up: what it asks, and a
    button for each lesson that teaches it.
    """

    lesson_requested = Signal(str)

    def __init__(self, exercise: Exercise, *, lessons: list[Lesson]) -> None:
        """
        Show the exercise's description and a button for each lesson
        that goes with it.

        Parameters
        ----------
        exercise : Exercise
            The plugin's exercise whose reference was opened.
        lessons : list of Lesson
            At least one lesson that names the exercise as practice, or
            that the exercise names. Keyword-only.

        Examples
        --------
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
        """
        super().__init__()
        layout = QVBoxLayout(self)
        self.lesson_buttons: list[QPushButton] = []
        for lesson in lessons:
            button = QPushButton(
                f"New to this? Take the lesson: {lesson.title}  →",
            )
            button.setToolTip(f"Open {lesson.title}")
            button.clicked.connect(
                lambda _=False, key=lesson.key: self.lesson_requested.emit(
                    key,
                ),
            )
            layout.addWidget(button)
            self.lesson_buttons.append(button)
        self.lesson_button = self.lesson_buttons[
            0
        ]  # the first lesson, as the built-in panels' one button
        about = QLabel(
            f"<h3>{html.escape(exercise.name)}</h3><p>{html.escape(exercise.description)}</p>",
        )
        about.setWordWrap(True)
        about.setAlignment(Qt.AlignmentFlag.AlignTop)
        about.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse,
        )
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setWidget(about)
        layout.addWidget(scroll, 1)


def reference_panel_for(
    exercise: Exercise,
) -> (
    ReferencePanel
    | ClefReferencePanel
    | ScaleReferencePanel
    | NoteReferencePanel
    | PluginReferencePanel
    | None
):
    """
    Return the reference pane for an exercise.

    Parameters
    ----------
    exercise : Exercise
        The exercise.

    Returns
    -------
    ReferencePanel or ClefReferencePanel or ScaleReferencePanel or
    NoteReferencePanel or None
        The panel, or None for an exercise with nothing to look up.

    Examples
    --------
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
    """
    if isinstance(exercise, PackExercise):
        name = type(exercise).__name__
        taught = [
            lesson
            for lesson in LESSONS
            if name in (lesson.exercise, *lesson.related_exercises)
        ]
        return (
            PluginReferencePanel(exercise, lessons=taught) if taught else None
        )
    if type(exercise) in _READING_HINTS:
        return NoteReferencePanel(exercise)
    if isinstance(exercise, CircleOfFifths):
        return ReferencePanel()
    if isinstance(exercise, ClefBasics):
        return ClefReferencePanel()
    if isinstance(exercise, ScaleIdentification):
        return ScaleReferencePanel()
    return None
