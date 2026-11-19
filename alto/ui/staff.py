"""
The staff: lines, clefs, key signatures and notes, drawn on a rounded white "paper".

`StaffWidget` draws one staff, or a grand staff with a brace, in any of the seven clefs. Notes and key signatures are
placed by their staff step (`Note.diatonic`) measured from the bottom line of the clef, and are engraved in the notation
font chosen in the settings.

Examples
--------
>>> key_signature_positions("treble", sign=1)
['F5', 'C5', 'G5', 'D5', 'A4', 'E5', 'B4']
>>> staff = StaffWidget()
>>> staff.show_notes([[Note.parse("C4")]], clef="treble", key=2)
>>> staff.clef, staff.key
('treble', 2)
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from functools import lru_cache
from weakref import WeakSet

import numpy as np
from PySide6.QtCore import (
    QEvent,
    QPoint,
    QPointF,
    QRectF,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetricsF,
    QImage,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QPicture,
    QResizeEvent,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QSizePolicy,
    QWidget,
)

from alto.notation_excerpts import excerpts
from alto.notation_terms import MARKS
from alto.theory.key_signatures import BOTTOM_LINE, key_signature_positions
from alto.theory.pitch import (
    ACCIDENTAL_SYMBOLS,
    Note,
    key_accidental,
)
from alto.ui import engraving
from alto.ui.degree_text import draw_degree_text
from alto.ui.notation import (
    NotationStyle,
    clef_shape,
    on_redraw,
)
from alto.ui.notation import current as current_style
from alto.ui.notes import draw_note
from alto.ui.score_excerpt import ScoreExcerpt, score_artwork

# Chord noteheads also carry their pitch so each head can be pointed to separately.
Component = tuple[str, int] | tuple[str, int, int]
PICK_RADIUS = 4
PICK_OFFSETS = sorted(
    ((x, y) for x in range(-PICK_RADIUS, PICK_RADIUS + 1) for y in range(-PICK_RADIUS, PICK_RADIUS + 1)),
    key=lambda offset: offset[0] ** 2 + offset[1] ** 2,
)

CLEF_GLYPH = {
    "treble": "𝄞",
    "bass": "𝄢",
    "alto": "𝄡",
    "tenor": "𝄡",
    "soprano": "𝄡",
    "mezzo": "𝄡",
    "baritone_c": "𝄡",
    "baritone_f": "𝄢",
    "french": "𝄞",
    "subbass": "𝄢",
}
# (glyph top, glyph bottom) measured upward from the bottom staff line, in staff gaps
CLEF_EXTENT = {
    "treble": (6.6, -2.2),
    "bass": (4.0, 0.7),
    "alto": (4.0, 0.0),
    "tenor": (5.0, 1.0),
    "soprano": (2.0, -2.0),
    "mezzo": (3.0, -1.0),
    "baritone_c": (6.0, 2.0),
    "baritone_f": (3.0, -0.3),
    "french": (5.6, -3.2),  # the treble clef, a gap lower
    "subbass": (5.0, 1.7),  # the bass clef, a gap higher
}
MIDDLE_C = Note(4, letter=0).diatonic


SYMBOL_CLEF = {"G": "treble", "C": "alto", "F": "bass"}  # a clef drawn with each symbol, to draw the symbol by


def clef_targets(clef: str) -> set[tuple[str, int]]:
    """
    Return the ways a clef can be written: the symbol and where on the staff it goes.

    Parameters
    ----------
    clef : str
        A clef name such as "treble", "mezzo" or "baritone".

    Returns
    -------
    set of tuple of (str, int)
        Each is a symbol, "G", "C" or "F", and the place of its reference line (the G, F or middle C) counted in lines and spaces
        up from the bottom line at 0: the bottom line is 0, the space above it 1, the second line 2, up to the top line at 8. Most
        clefs have one. The baritone clef has two: the F clef on the middle line and the C clef on the top line.

    Examples
    --------
    >>> clef_targets("treble") == {("G", 2)} and clef_targets("mezzo") == {("C", 2)}
    True
    >>> sorted(clef_targets("baritone"))
    [('C', 8), ('F', 4)]
    >>> sorted(clef_targets("french") | clef_targets("subbass"))
    [('F', 8), ('G', 0)]
    """
    if clef == "baritone":
        return {clef_target_of("baritone_f"), clef_target_of("baritone_c")}
    return {clef_target_of(clef)}


def clef_target_of(shape: str) -> tuple[str, int]:
    """
    Return the symbol and the place of one way of writing a clef.

    Parameters
    ----------
    shape : str
        A key of `engraving.CLEF_SIGNS`, such as "alto" or "baritone_c".

    Returns
    -------
    tuple of (str, int)
        The symbol and its place, as for `clef_targets`.

    Examples
    --------
    >>> clef_target_of("bass"), clef_target_of("soprano")
    (('F', 6), ('C', 0))
    """
    glyph, line = engraving.CLEF_SIGNS[shape]
    return glyph[0].upper(), 2 * line


_KEY_POSITIONS = {(clef, sign): " ".join(key_signature_positions(clef, sign=sign)) for clef in BOTTOM_LINE for sign in (1, -1)}
KEY_OFFSET = 56.0  # distance from the left end of an exercise staff to its first signature sign
KEY_STEP = 13.0  # horizontal spacing between key-signature accidentals
# A staff with few notes should not stretch across a wide window: each column of notes gets at most this much width, and the
# staff is never made narrower than MIN_COLUMNS columns would need.
MAX_STEP = 120.0
MIN_COLUMNS = 3

# Grand staff layout, in staff gaps: margin above/below the pair and the distance between them.
GRAND_BETWEEN = 3.5
CORNER_RADIUS = 14


def draw_key_signature(
    p: QPainter,
    *,
    clef: str,
    key: int,
    x: float,
    bottom: float,
    gap: float,
    color: QColor,
    step: float = KEY_STEP,
    size: float = 2.0,
    font: str | None = None,
) -> None:
    """
    Draw the sharps or flats of a key signature, left to right.

    Parameters
    ----------
    p : QPainter
        The painter to draw with.
    clef : str
        The clef, which decides where on the staff each accidental goes. Keyword-only.
    key : int
        The key signature: that many sharps if positive, flats if negative; nothing is drawn for 0. Keyword-only.
    x : float
        The left edge of the first accidental, in pixels. Keyword-only.
    bottom : float
        The y position of the staff's bottom line, in pixels. Keyword-only.
    gap : float
        The distance between staff lines, in pixels. Keyword-only.
    color : QColor
        The color to draw in. Keyword-only.
    step : float, default KEY_STEP
        The horizontal spacing between accidentals. Keyword-only.
    size : float, default 2.0
        The size of the built-in characters, in staff gaps. Keyword-only.
    font : str or None, default None
        A SMuFL font to engrave them in; None uses the built-in sharp and flat characters. Keyword-only.

    Examples
    --------
    >>> from PySide6.QtGui import QImage
    >>> image = QImage(200, 120, QImage.Format.Format_ARGB32)
    >>> image.fill(QColor("white"))
    >>> painter = QPainter(image)
    >>> draw_key_signature(painter, clef="treble", key=3, x=10, bottom=80, gap=12, color=QColor("black"), font="bravura")
    >>> painter.end()
    True
    >>> any(image.pixelColor(x_, y_).lightness() < 128 for x_ in range(10, 60) for y_ in range(20, 100))
    True
    """
    if key:
        sign = 1 if key > 0 else -1
        for i, name in enumerate(_KEY_POSITIONS[clef, sign].split()[: abs(key)]):
            y = bottom - (Note.parse(name).diatonic - BOTTOM_LINE[clef]) * gap / 2
            draw_signature_sign(p, sign=sign, x=x + i * step, y=y, gap=gap, color=color, step=step, size=size, font=font)


def draw_signature_sign(
    p: QPainter,
    *,
    sign: int,
    x: float,
    y: float,
    gap: float,
    color: QColor,
    step: float = KEY_STEP,
    size: float = 2.0,
    font: str | None = None,
) -> None:
    """
    Draw one sharp or flat at its written position in a key signature.

    Parameters
    ----------
    p : QPainter
        Active staff painter.
    sign : int
        Sharp (1) or flat (-1).
    x, y : float
        Left edge and staff pitch position in pixels.
    gap : float
        Distance between staff lines.
    color : QColor
        Ink for this sign.
    step, size : float
        Slot width in pixels and built-in glyph size in staff gaps.
    font : str or None
        SMuFL font, or None for the built-in notation.

    Examples
    --------
    Both the printed signature and signs placed by the learner use this drawing.
    """
    if font:
        engraving.draw_accidental(p, font=font, sign=sign, x=x, y=y, gap=gap, color=color, fit=step - 1)
        return
    p.save()
    p.setPen(QPen(color, 1.4))
    sign_font = QFont("DejaVu Sans")
    sign_font.setPixelSize(max(int(gap * size * 1.33), 6))
    p.setFont(sign_font)
    p.drawText(QPointF(x, y + gap * 0.5), ACCIDENTAL_SYMBOLS[sign])
    p.restore()


# Distances in staff spaces for short examples (docs/development.md, Engraving lesson examples).
_SIGNATURE_GAP = 1.0
_SIGN_GAP = 0.25
_FIRST_NOTE_GAP = 1.5
_END_GAP = 2.0
_NOTE_ADVANCE = {"breve": 6.5, "whole": 5.5, "half": 4.5, "quarter": 3.5, "eighth": 3, "sixteenth": 2.5, "thirty_second": 2}


@dataclass
class _LessonSystem:
    """
    Positions for one line of a lesson example, in widget coordinates.

    Examples
    --------
    >>> _LessonSystem(key_x=40, key_step=9, right=80).centers
    []
    """

    key_x: float
    key_step: float
    right: float
    first: int = 0
    centers: list[float] = field(default_factory=list)
    signs: list[list[float]] = field(default_factory=list)
    bottoms: dict[str, float] = field(default_factory=dict)
    height: float = 0
    caption_rect: QRectF = field(default_factory=QRectF)


@lru_cache(maxsize=256)
def _lesson_note_bounds(font: str | None, *, value: str, gap: float, down: bool) -> QRectF:
    """
    Measure the same note glyph that the staff will paint, including its stem and flag.

    Parameters
    ----------
    font : str or None
        Selected music font.
    value : str
        Written note duration.
    gap : float
        Staff space in pixels.
    down : bool
        Whether the stem points down.

    Returns
    -------
    QRectF
        Ink bounds relative to the notehead center.

    Examples
    --------
    >>> _lesson_note_bounds("bravura", value="quarter", gap=8, down=False).width() > 0
    True
    """
    picture = QPicture()
    with QPainter(picture) as painter:
        StaffWidget._note(painter, x=0, y=0, gap=gap, value=value, color=QColor("black"), stem_down=down, font=font)
    return QRectF(picture.boundingRect())


@lru_cache(maxsize=128)
def _lesson_header_bounds(clef: str, *, font: str | None, gap: float, key: int, hidden: bool) -> tuple[float, QRectF]:
    """
    Measure the clef's right edge and the vertical extent of the staff, clef, and signature.

    Parameters
    ----------
    clef : str
        Staff clef.
    font : str or None
        Selected music font.
    gap : float
        Staff space in pixels.
    key : int
        Number of sharps or negative number of flats.
    hidden : bool
        Hide the clef for a staff-reading question.

    Returns
    -------
    tuple of float, QRectF
        End of the clef and ink bounds relative to the bottom staff line.

    Examples
    --------
    >>> end, bounds = _lesson_header_bounds("bass", font="bravura", gap=8, key=-3, hidden=False)
    >>> end > 0 and bounds.top() <= -32
    True
    """
    picture = QPicture()
    with QPainter(picture) as painter:
        if not hidden:
            StaffWidget._draw_clef(painter, clef=clef, x=0, bottom=0, gap=gap, font=font)
    clef_bounds = QRectF(picture.boundingRect())
    bounds = clef_bounds.united(QRectF(0, -4 * gap, gap, 4 * gap))
    if key:
        picture = QPicture()
        with QPainter(picture) as painter:
            draw_key_signature(painter, clef=clef, key=key, x=0, bottom=0, gap=gap, color=QColor("black"), font=font)
        bounds = bounds.united(QRectF(picture.boundingRect()))
    return clef_bounds.right(), bounds


class StaffWidget(QWidget):
    """
    A staff with notes, a clef, a key signature and, optionally, a caption.

    Attributes
    ----------
    GAP : float
        The distance between staff lines, in pixels.
    side : float
        The space at the left and right edges.
    note_offset : float
        Where the notes start, from the left edge.
    margin : float
        The space kept above and below the staff for ledger lines, in gaps.
    compact : bool
        Size the widget to fit instead of the 220 px default.
    max_step : float or None
        The most width each column of notes may take.
    clef : str
        The clef being drawn ("treble", "bass", "alto", "tenor", "soprano", "mezzo", "baritone" or "grand").
    columns : list of list of Note
        The notes drawn; each inner list is one chord or note.
    interval_voices : bool
        Draw harmonic interval endpoints with their written duration and opposing stems.
    note_color : QColor or None
        Feedback color for the highlighted notation component, or for the notes in other exercises.
    column_colors : dict of int to QColor
        The color of particular columns of notes, by position from 0; they are drawn in these instead of `note_color`.
    wedges : list of str
        The step between each column and the next, such as "W" or "H", drawn as two lines rising from the notes to a point
        above them, with the letter over the point; "" for none there.
    wedge_colors : dict of int to QColor
        The color of particular wedges, by position from 0. The others take the color of the note on their right,
        or `note_color`.
    notation_style : NotationStyle or None
        A style to use instead of the one chosen in the settings.
    clef_hidden : bool
        Draw the staff without its clef, for a clef the learner places.
    key : int
        The key signature drawn: sharps if positive, flats if negative.
    key_room : int
        How many sharps or flats' worth of room to keep for the signature at least, so that a capped staff does not change
        width as the signature does. 0 keeps room only for the one drawn.
    value : str
        The note value drawn.
    caption : str
        Text written under the staff, inside the paper.

    Examples
    --------
    >>> staff = StaffWidget()
    >>> staff.show_notes([[Note.parse("E4")], [Note.parse("G4")]], clef="treble")
    >>> len(staff.columns)
    2
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        gap: float = 16.0,
        side: float = 20.0,
        note_offset: float = 100.0,
        margin: float = 8.0,
        compact: bool = False,
        max_step: float | None = None,
        lesson_layout: bool = False,
    ) -> None:
        """
        Create an empty treble staff.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the staff.
        gap : float, default 16.0
            The distance between staff lines, in pixels. Keyword-only.
        side : float, default 20.0
            The space at the left and right edges. Keyword-only.
        note_offset : float, default 100.0
            Where the notes start, from the left edge. Keyword-only.
        margin : float, default 8.0
            The space kept above and below the staff for ledger lines, in gaps. Keyword-only.
        compact : bool, default False
            Size the widget to fit instead of the 220 px default. Keyword-only.
        max_step : float or None, default None
            The most width each column of notes may take: the staff then stops growing once its notes would be spread wider than
            that, so a few notes stay easy to read in a wide window. Keyword-only.
        lesson_layout : bool, default False
            Space the excerpt by its printed symbols and wrap at note or chord boundaries. Keyword-only.

        Examples
        --------
        >>> StaffWidget(gap=8.0, compact=True).GAP
        8.0
        """
        super().__init__(parent)
        self.GAP, self.side, self.note_offset, self.margin, self.compact = gap, side, note_offset, margin, compact
        self.lesson_peers: WeakSet[StaffWidget] = WeakSet()
        self.lesson_layout = lesson_layout
        self.max_step = max_step
        self.clef = "treble"
        self.interval_voices = False
        self.columns: list[list[Note]] = []
        self.playback_column: int | None = None
        self.note_color: QColor | None = None  # None draws notes in the style's ink
        self.column_colors: dict[int, QColor] = {}  # a color for a column of notes by its position, over `note_color`
        self.wedges: list[str] = []  # the text of the wedge under each pair of neighboring columns; "" for none
        self.wedge_colors: dict[int, QColor] = {}  # a color for a wedge by its position, over its right-hand note's
        self.notation_style: NotationStyle | None = None  # None follows the style chosen in settings
        self.key = 0
        self.key_room = 0  # sharps or flats' worth of room to keep for the signature, so the width need not follow it
        self.value = "whole"
        self.caption = ""  # text written under the staff, inside the paper
        self.notation_target: tuple[str, int] | None = None
        self.excerpt: ScoreExcerpt | None = None
        self._clicked_component: Component | None = None
        self.locate_notation = False
        self._hover_point: QPoint | None = None
        self._pick_geometry: tuple | None = None
        self._pick_map = np.empty((0, 0), dtype=np.uint16)
        self._pick_parts: list[Component] = []
        self.clef_hidden = False  # draw the staff without its clef, for a clef the learner places
        self._fit_height("treble")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def show_notes(
        self,
        columns: list[list[Note]],
        *,
        clef: str = "treble",
        key: int = 0,
        value: str = "whole",
        caption: str = "",
        notation_target: tuple[str, int] | None = None,
        locate_notation: bool = False,
        notation_excerpt: str | None = None,
    ) -> None:
        """
        Show some notes, with a clef and a key signature.

        Parameters
        ----------
        columns : list of list of Note
            The notes: each inner list is one note or chord, drawn left to right.
        clef : str, default "treble"
            The clef, or "grand" for a grand staff. Keyword-only.
        key : int, default 0
            The key signature: that many sharps if positive, flats if negative. Keyword-only.
        value : str, default "whole"
            The written duration for single notes and interval voices. Keyword-only.
        caption : str, default ""
            Text to write under the staff. Keyword-only.
        notation_target : tuple of (str, int) or None
            Part and position to highlight in a notation question. Keyword-only.
        notation_excerpt : str or None
            Versioned score to show for a repertoire question. Keyword-only.
        locate_notation : bool, default False
            Render the target in ordinary ink for the learner to find. Keyword-only.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff.show_notes([[Note.parse("C4")]], clef="bass", key=-1, value="quarter", caption="_ Major")
        >>> staff.clef, staff.key, staff.value, staff.caption
        ('bass', -1, 'quarter', '_ Major')
        """
        self.playback_column = None
        self.notation_target = notation_target
        self.excerpt = score_artwork(excerpts()[notation_excerpt]) if notation_excerpt else None
        self._clicked_component = None
        self.setToolTip(self.excerpt.excerpt.credit if self.excerpt else "")
        if locate_notation != self.locate_notation:
            self.setMouseTracking(locate_notation)
        self.locate_notation = locate_notation
        self._pick_geometry = None
        self._hover_point = None
        self.columns, self.clef, self.key, self.value, self.caption = columns, clef, key, value, caption
        self.note_color = None
        self._fit_height(clef)
        self._fit_width()
        if self.excerpt:
            self.setMaximumWidth(760)
        self.update()

    def _fit_width(self) -> None:
        """
        Size lesson paper to its music and caption, or limit exercise columns using `max_step`.

        A lesson can shrink until its widest chord and longest caption word fit.
        For an exercise, reserve room for the drawn signature or `key_room`, whichever is larger.

        Examples
        --------
        >>> staff = StaffWidget(max_step=120.0)
        >>> staff.show_notes([[Note.parse("C4")]])
        >>> staff.maximumWidth()  # room for the clef and at least three columns of notes
        500
        >>> staff.key_room = 7  # keep the room of a signature of seven sharps or flats, whatever is drawn
        >>> staff.show_notes([[Note.parse("C4")]])
        >>> staff.maximumWidth() - 500
        91
        """
        if self.lesson_layout:
            # A note or chord and its opening signature must fit together on one line.
            smallest = self._lesson_systems(1)
            self.setMinimumWidth(math.ceil(max(max(row.right, row.caption_rect.right()) for row in smallest) + self.side))
            # A short example asks for just enough paper for the unwrapped music and caption.
            (full,) = self._lesson_systems(16777215)  # Qt's maximum widget dimension
            self.setMaximumWidth(math.ceil(max(full.right, full.caption_rect.right()) + self.side))
            return
        if self.max_step is None:
            return
        left = self.side + (18.0 if self.clef == "grand" else 0.0)  # the same left edge the drawing uses
        columns = max(len(self.columns), MIN_COLUMNS)
        self.setMaximumWidth(
            round(left + self.note_offset + KEY_STEP * max(abs(self.key), self.key_room) + columns * self.max_step + self.side),
        )

    def sizeHint(self) -> QSize:
        """
        Return the size the staff would like.

        A capped staff asks for its full capped width, so a layout that centers it gives it that much.

        Returns
        -------
        QSize
            The capped width and minimum height for a lesson or a staff with a `max_step`. Other staves use Qt's default.

        Examples
        --------
        >>> staff = StaffWidget(max_step=120.0)
        >>> staff.show_notes([[Note.parse("C4")]])
        >>> staff.sizeHint().width()
        500
        """
        if self.max_step is None and not self.lesson_layout:
            return super().sizeHint()
        return QSize(self.maximumWidth(), self.minimumHeight())

    def _positioned_notes(self, column: list[Note]) -> Iterator[tuple[Note, str, int, float]]:
        """
        Place chord tones on their staves, displacing adjacent noteheads as needed.

        Parameters
        ----------
        column : list of Note
            Pitches at one rhythmic position.

        Yields
        ------
        tuple of Note, str, int, float
            Pitch, staff clef, diatonic steps above its bottom line, and horizontal displacement.

        Examples
        --------
        >>> list(StaffWidget()._positioned_notes([Note.parse("E4")]))[0][1:]
        ('treble', 0, 0.0)
        """
        previous = None
        previous_clef = ""
        shifted = False
        for note in sorted(column):
            clef = self.clef
            if clef == "grand":
                clef = "treble" if note.diatonic >= MIDDLE_C else "bass"
            shifted = not shifted and previous is not None and clef == previous_clef and note.diatonic - previous.diatonic <= 1
            yield note, clef, note.diatonic - BOTTOM_LINE[clef], 1.55 * self.GAP if shifted else 0.0
            previous, previous_clef = note, clef

    def _lesson_systems(self, width: int, *, align: bool = True) -> list[_LessonSystem]:
        """
        Lay out lesson notes and their signs from left to right, repeating the opening on wrapped lines.

        Parameters
        ----------
        width : int
            Available width in pixels.
        align : bool, default True
            Align the noteheads of paired single-note illustrations.

        Returns
        -------
        list of _LessonSystem
            The origin of each note, offsets for its accidentals, staff ends, and vertical positions.

        Examples
        --------
        >>> StaffWidget(lesson_layout=True)._lesson_systems(280)[0].right < 280
        True
        """
        gap = self.GAP
        font = (self.notation_style or current_style()).font
        grand = self.clef == "grand"
        clefs = ("treble", "bass") if grand else (self.clef,)
        left = self.side + (18 if grand else 0)
        bass_offset = (4 + GRAND_BETWEEN) * gap if grand else 0
        opening = left
        above = below = 0.0
        for clef in clefs:
            end, bounds = _lesson_header_bounds(clef, font=font, gap=gap, key=self.key, hidden=self.clef_hidden)
            if not self.clef_hidden:
                opening = max(opening, left + gap + end)
            offset = bass_offset if clef == "bass" else 0
            above = max(above, -bounds.top() - offset)
            below = max(below, bounds.bottom() + offset - bass_offset)

        def sign_width(sign: int) -> float:
            """
            Measure an accidental in the staff's notation style.

            Parameters
            ----------
            sign : int
                Alteration in half steps.

            Returns
            -------
            float
                Width in pixels.

            Examples
            --------
            >>> StaffWidget(lesson_layout=True)._lesson_systems(300)[0].key_step > 0
            True
            """
            if font:
                return engraving.accidental_width(font=font, sign=sign, gap=gap)
            sign_font = QFont("DejaVu Sans")
            sign_font.setPixelSize(max(int(gap * 2 * 1.33), 6))
            return QFontMetricsF(sign_font).horizontalAdvance(ACCIDENTAL_SYMBOLS[sign] or "♮")

        key_x = opening + _SIGNATURE_GAP * gap
        key_step = sign_width(1 if self.key > 0 else -1) + _SIGN_GAP * gap
        if self.key:
            opening = key_x + abs(self.key) * key_step - _SIGN_GAP * gap
        tail = _END_GAP * gap
        empty_end = max(opening + tail, left + (8 if self.clef_hidden else 0) * gap)
        rows = [_LessonSystem(key_x, key_step, empty_end)]
        row = rows[0]
        advance = _NOTE_ADVANCE[self.value] * gap
        column_metrics = []
        for col in self.columns:
            bounds = QRectF()
            offsets = []
            signs = []
            value = self.value if self.interval_voices or len(col) == 1 else "whole"
            for note, clef, steps, x in self._positioned_notes(col):
                y = -steps * gap / 2 + (bass_offset if clef == "bass" else 0)
                down = note == min(col) if self.interval_voices and len(col) == 2 else steps >= 4
                bounds = bounds.united(_lesson_note_bounds(font, value=value, gap=gap, down=down).translated(x, y))
                if steps <= -2 or steps >= 10:
                    bounds = bounds.united(QRectF(x - gap, y, 2 * gap, 1))
                if note.accidental != key_accidental(note.letter, count=self.key):
                    signs.append(note.accidental)
                    above = max(above, 2 * gap - y)
                    below = max(below, y + 2 * gap - bass_offset)
            start = bounds.left()
            for sign in signs:
                start -= _SIGN_GAP * gap + sign_width(sign)
                offsets.append(start)
            above = max(above, -bounds.top() + (5 * gap if self.wedges else 0))
            below = max(below, bounds.bottom() - bass_offset)
            column_metrics.append((start, bounds.right(), offsets))

        first_center = 0.0
        if align:
            for peer in self.lesson_peers:
                other = peer._lesson_systems(width, align=False)[0]
                first_center = max(first_center, other.centers[0])
        for index, (start, end, offsets) in enumerate(column_metrics):
            center = opening + _FIRST_NOTE_GAP * gap - start
            if row.centers:
                center = max(row.centers[-1] + advance, row.right - tail + gap / 2 - start)
                if center + end + tail > width - self.side:
                    row = _LessonSystem(key_x, key_step, empty_end, first=index)
                    rows.append(row)
                    center = opening + _FIRST_NOTE_GAP * gap - start
            if index == 0:
                center = max(first_center, center)
            row.centers.append(center)
            row.signs.append(offsets)
            row.right = center + end + tail

        y = gap
        for row in rows:
            bottom = y + above
            row.bottoms = {clef: bottom + (bass_offset if clef == "bass" else 0) for clef in clefs}
            y = bottom + bass_offset + below + gap
            row.height = y
        if self.caption:
            caption_font = QFont(self.font())
            caption_font.setPixelSize(max(int(gap * 1.6), 12))
            rect = QRectF(left, y, max(1, width - left - self.side), 10000)
            measured = QFontMetricsF(caption_font).boundingRect(rect, Qt.TextFlag.TextWordWrap, self.caption)
            rect.setWidth(math.ceil(measured.width()))
            rect.setHeight(measured.height())
            rows[-1].caption_rect = rect
            rows[-1].height = rect.bottom() + gap
        return rows

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Reflow a lesson excerpt when its available width changes.

        Parameters
        ----------
        event : QResizeEvent
            Previous and current widget size.

        Examples
        --------
        >>> staff = StaffWidget(lesson_layout=True)
        >>> staff.resize(300, staff.height())
        """
        super().resizeEvent(event)
        if self.lesson_layout and event.size().width() != event.oldSize().width():
            self._fit_height(self.clef)

    def _fit_height(self, clef: str) -> None:
        """
        Set the height the staff needs for its clef.

        Parameters
        ----------
        clef : str
            "grand" needs room for two staves; any other clef for one.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff.minimumHeight()
        330
        >>> staff._fit_height("grand")
        >>> staff.minimumHeight()
        450
        """
        if self.lesson_layout:
            self.setFixedHeight(math.ceil(self._lesson_systems(self.width())[-1].height))
            return
        grand_height = 2 * self.margin + 8 + GRAND_BETWEEN  # in gaps
        if self.compact:
            self.setFixedHeight(int((grand_height if clef == "grand" else 4 + 2 * self.margin) * self.GAP))
        else:
            self.setMinimumHeight(int((grand_height if clef == "grand" else 4 + 2 * self.margin) * self.GAP) + 10)

    def highlight_column(self, index: int | None) -> None:
        """
        Highlight a sounding note or chord, preserving the staff's other markings.

        Parameters
        ----------
        index : int or None
            The sounding column, or None to restore its usual ink.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff.highlight_column(0)
        >>> staff.playback_column
        0
        """
        self.playback_column = index
        self.update()

    def set_note_color(self, color: QColor | None) -> None:
        """
        Apply feedback to the highlighted notation component or to the notes when there is no component target.

        Parameters
        ----------
        color : QColor or None
            The feedback color. None restores the usual ink and highlight colors.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff.set_note_color(QColor("#2e7d32"))
        >>> # noinspection PyUnresolvedReferences
        >>> staff.note_color.name()
        '#2e7d32'
        >>> staff.set_note_color(None)
        >>> staff.note_color is None
        True
        """
        self.note_color = QColor(color) if color is not None else None
        self.update()

    def staff_bottoms(self) -> dict[str, float]:
        """
        Return where each staff is drawn.

        Returns
        -------
        dict of str to float
            Clef name to the y position of that staff's bottom line, in pixels. A grand staff has a "treble" and a "bass".

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff.resize(400, 400)
        >>> staff.staff_bottoms()
        {'treble': 232.0}
        """
        gap, h = self.GAP, self.height()
        if self.clef == "grand":
            top = (h - (2 * self.margin + 8 + GRAND_BETWEEN) * gap) / 2 + self.margin * gap
            return {"treble": top + 4 * gap, "bass": top + (8 + GRAND_BETWEEN) * gap}
        return {self.clef: h / 2 + 2 * gap}

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the paper, the staff lines, the clef, the key signature, the notes and the caption.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request; the whole widget is always redrawn.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff.resize(400, 400)
        >>> staff.show_notes([[Note.parse("C4")]], clef="treble")
        >>> staff.grab().toImage().pixelColor(200, 5).name()  # the white paper
        '#ffffff'
        """
        with QPainter(self) as p:
            focused: Component | None = self.notation_target
            if self.locate_notation and self.note_color is None:
                focused = self._notation_at(self._hover_point) if self._hover_point is not None else None
            if self.excerpt:
                if self.note_color is not None and self._clicked_component:
                    focused = self._clicked_component
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor("white"))
                p.drawRoundedRect(self.rect(), CORNER_RADIUS, CORNER_RADIUS)
                self.excerpt.paint(
                    p,
                    paper=QRectF(self.rect()),
                    index=focused[1] if focused else None,
                    color=self.note_color or QColor("#0068af"),
                )
                return
            if focused and focused[0] in {"Notehead", "Stem"} and focused[1] == self.playback_column:
                focused = None  # let the sounding column use playback ink, then restore its notation marking
            accent = self.note_color or QColor("#0068af")
            self._draw_score(p, ink=lambda part: accent if part == focused else None)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Preview the component under the pointer in Click on Staff questions.

        Parameters
        ----------
        event : QMouseEvent
            The pointer position relative to the score.

        Examples
        --------
        >>> StaffWidget().hasMouseTracking()
        False
        """
        if self.locate_notation:
            self._hover_point = event.position().toPoint()
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """
        Clear the component preview when the pointer leaves the music.

        Parameters
        ----------
        event : QEvent
            The pointer leaving the staff.

        Examples
        --------
        >>> StaffWidget().leaveEvent(QEvent(QEvent.Type.Leave))
        """
        if self._hover_point is not None:
            self._hover_point = None
            self.update()
        super().leaveEvent(event)

    def hits_notation(self, point: QPoint) -> bool:
        """
        Check for target ink within four logical pixels of a click on the score.

        Parameters
        ----------
        point : QPoint
            Click position relative to the staff widget.

        Returns
        -------
        bool
            Whether the clicked neighborhood contains the selected marking.

        Examples
        --------
        >>> StaffWidget().hits_notation(QPoint(0, 0))
        False
        """
        component = self._notation_at(point)
        if (
            self.excerpt
            and self.locate_notation
            and component
            and self.notation_target
            and component[0] == self.notation_target[0]
        ):
            self._clicked_component = component
            return True
        return self.notation_target is not None and component == self.notation_target

    def _notation_at(self, point: QPoint) -> Component | None:
        """
        Identify the nearest visible component within the pointer tolerance.

        Parameters
        ----------
        point : QPoint
            Position in the staff widget.

        Returns
        -------
        Component or None
            The nearest marked ink, or None on empty paper.

        Examples
        --------
        >>> StaffWidget()._notation_at(QPoint(0, 0)) is None
        True
        """
        if self.excerpt:
            rect = self.excerpt.music_rect(QRectF(self.rect()))
            for dx, dy in PICK_OFFSETS:
                if component := self.excerpt.component_at(point + QPoint(dx, dy), rect=rect):
                    return component
            return None
        geometry = (self.size(), self.notation_style or current_style(), clef_shape(self.clef), self.font())
        if geometry != self._pick_geometry:
            self._build_pick_map()
            self._pick_geometry = geometry
        for dx, dy in PICK_OFFSETS:
            x, y = point.x() + dx, point.y() + dy
            if 0 <= x < self.width() and 0 <= y < self.height():
                index = self._pick_map[y, x]
                if index:
                    return self._pick_parts[index - 1]
        return None

    def _build_pick_map(self) -> None:
        """
        Record which visible component owns each pixel of the score.

        Each paint pass measures three components in separate color channels on black paper.
        The strongest visible ink wins. Staff lines have lower priority at crossings so a thin
        symbol drawn over a line can still be picked.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff._build_pick_map()
        >>> staff._pick_map.shape == (staff.height(), staff.width())
        True
        """
        parts: defaultdict[Component, int] = defaultdict(lambda: len(parts))
        self._pick_map = np.zeros((self.height(), self.width()), dtype=np.uint16)
        strongest = np.zeros_like(self._pick_map, dtype=np.uint8)
        image = QImage(self.size(), QImage.Format.Format_RGBA8888)
        black = QColor("black")
        first = 0
        while first == 0 or first < len(parts):
            channels = {first + i: QColor(color) for i, color in enumerate(("red", "lime", "blue"))}
            image.fill(black)
            with QPainter(image) as painter:
                painter.setFont(self.font())
                self._draw_score(painter, ink=lambda part, palette=channels: palette.get(parts[part], black), paper=black)
            pixels = np.frombuffer(image.constBits(), dtype=np.uint8).reshape(self.height(), self.width(), 4)
            for channel, part in enumerate(list(parts)[first : first + 3]):
                coverage = pixels[:, :, channel]
                background_line = part[0] == "Staff line" and (self.locate_notation or part != self.notation_target)
                weight = coverage // 3 if background_line else coverage
                visible = (coverage > 32) & (weight > strongest)
                self._pick_map[visible] = first + channel + 1
                strongest[visible] = weight[visible]
            first += 3
        self._pick_parts = list(parts)

    def _draw_score(
        self,
        p: QPainter,
        *,
        ink: Callable[[Component], QColor | None],
        paper: QColor = QColor("white"),
    ) -> None:
        """
        Draw the phrase with the same geometry for display and pointer hit testing.

        Parameters
        ----------
        p : QPainter
            Painter using widget coordinates.
        ink : callable
            Resolve a component's ink, returning None to keep the usual color. Keyword-only.
        paper : QColor, default white
            Background for display or measuring component ink. Keyword-only.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> image = QImage(staff.size(), QImage.Format.Format_RGB32)
        >>> with QPainter(image) as painter:
        ...     staff._draw_score(painter, ink=lambda part: None)
        """
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        look = self.notation_style or current_style()
        font = look.font
        line = engraving.staff_line_width(font, gap=self.GAP) if font else look.line
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(paper)
        p.drawRoundedRect(self.rect(), CORNER_RADIUS, CORNER_RADIUS)  # the rounded "paper" behind the music
        rows = self._lesson_systems(self.width()) if self.lesson_layout else [None]
        for row in rows:
            self._draw_system(p, ink=ink, row=row, font=font, line=line, caption=row is rows[-1])

    def _draw_system(
        self,
        p: QPainter,
        *,
        ink: Callable[[Component], QColor | None],
        row: _LessonSystem | None,
        font: str | None,
        line: float,
        caption: bool,
    ) -> None:
        """
        Paint one system using exercise columns or the measured positions of a lesson excerpt.

        Parameters
        ----------
        p : QPainter
            Painter using widget coordinates.
        ink : callable
            Resolve a component's highlight color.
        row : _LessonSystem or None
            Lesson geometry, or None for exercise spacing.
        font : str or None
            Selected music font.
        line : float
            Staff line thickness.
        caption : bool
            Draw the caption below this system.

        Examples
        --------
        >>> staff = StaffWidget(lesson_layout=True)
        >>> not staff.grab().isNull()
        True
        """
        fg = QColor("black")
        p.setPen(QPen(fg, line))
        gap = self.GAP
        w = self.width()
        grand = self.clef == "grand"
        left, right = self.side + (18.0 if grand else 0.0), w - self.side

        staves = row.bottoms if row else self.staff_bottoms()
        if row:
            right = row.right

        nfg = fg if self.notation_target else (self.note_color or fg)
        term, position = self.notation_target or ("", -1)
        placement, symbol = MARKS.get(term, ("", None))
        for clef, bottom in staves.items():
            for i in range(5):
                part = ("Staff line", i)
                width = 3 * line if part == self.notation_target and not self.locate_notation else line
                p.setPen(QPen(ink(part) or fg, width))
                p.drawLine(QPointF(left, bottom - i * gap), QPointF(right, bottom - i * gap))
            if not self.clef_hidden:
                self._draw_clef(
                    p,
                    clef=clef,
                    x=left + (gap if row else 8),
                    bottom=bottom,
                    gap=gap,
                    color=ink((term, position) if term == "Clef" or placement == "clef" else ("Clef", 0)) or fg,
                    font=font,
                )
            draw_key_signature(
                p,
                clef=clef,
                x=row.key_x if row else left + KEY_OFFSET,
                key=self.key,
                step=row.key_step if row else KEY_STEP,
                bottom=bottom,
                gap=gap,
                color=ink(("Key signature", position)) or fg,
                font=font,
            )
        if grand:
            ys = list(staves.values())
            p.drawLine(QPointF(left, ys[0] - 4 * gap), QPointF(left, ys[1]))
            self._brace(
                p,
                x=left - 3,
                y0=ys[0] - 4 * gap,
                y1=ys[1],
                color=fg,
                font=font,
            )

        if caption and self.caption:
            caption_font = QFont(self.font())
            caption_font.setPixelSize(max(int(gap * 1.6), 12))
            p.setFont(caption_font)
            p.setPen(fg)
            top = max(staves.values()) + 2.5 * gap  # below the lowest staff, clear of its ledger lines
            if row:
                p.drawText(row.caption_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft, self.caption)
            else:
                draw_degree_text(
                    p,
                    rect=QRectF(left, top, right - left, max(self.height() - top - gap, gap * 2)),
                    text=self.caption,
                )

        n = max(len(self.columns), 1)
        x0 = left + self.note_offset + KEY_STEP * abs(self.key)
        step = (right - x0) / n
        p.setBrush(nfg)
        heads: dict[int, QPointF] = {}  # where the top note of each column was drawn, for the steps between them
        indices = range(row.first, row.first + len(row.centers)) if row else range(len(self.columns))
        for ci in indices:
            col = self.columns[ci]
            column_x = row.centers[ci - row.first] if row else x0 + step * (ci + 0.5)
            acc_slot = 0
            ncol = self.palette().highlight().color() if ci == self.playback_column else self.column_colors.get(ci, nfg)
            p.setBrush(ncol)
            for note, clef, steps, shift in self._positioned_notes(col):
                x = column_x + shift
                bottom = staves[clef]
                y = bottom - steps * gap / 2
                heads[ci] = QPointF(x, min(y, heads[ci].y()) if ci in heads else y)
                ledger_ink = ink(("Ledger line", ci)) or fg
                p.setPen(QPen(ledger_ink, engraving.ledger_width(font, gap=gap) if font else line))
                if steps < 0:
                    for s in range(-2, steps - 1, -2):
                        self._ledger(
                            p,
                            x=x,
                            y=bottom - s * gap / 2,
                            gap=gap,
                        )
                elif steps > 8:
                    for s in range(10, steps + 1, 2):
                        self._ledger(
                            p,
                            x=x,
                            y=bottom - s * gap / 2,
                            gap=gap,
                        )
                p.setPen(Qt.PenStyle.NoPen)
                value = self.value if self.interval_voices or len(col) == 1 else "whole"
                stem_down = note == min(col) if self.interval_voices and len(col) == 2 else steps >= 4
                marked_note = placement == "note" and ci == position
                if marked_note:
                    value = str(symbol)
                # For note-value questions the whole note is one choice. Otherwise separate the head and stem.
                if placement == "note":
                    head_color = stem_color = ink((term if marked_note else "Note", ci)) or ncol
                else:
                    head: Component = ("Notehead", ci) if len(col) == 1 else ("Notehead", ci, note.midi)
                    head_color = ink(head) or ncol
                    stem_color = ink(("Stem", ci)) or ncol
                regions: list[tuple[QRectF | None, QColor]] = [(None, head_color)]
                if stem_color != head_color and value not in ("whole", "breve"):
                    split = y + (0.55 if stem_down else -0.55) * gap
                    above, below = QRectF(self.rect()), QRectF(self.rect())
                    above.setBottom(split)
                    below.setTop(split)
                    regions = [(above, head_color if stem_down else stem_color), (below, stem_color if stem_down else head_color)]
                for clip, color in regions:
                    p.save()
                    if clip is not None:
                        p.setClipRect(clip)
                    if term == "Flag" and ci == position:
                        engraving.draw_note(
                            p,
                            font=font or "bravura",
                            value="eighth",
                            x=x,
                            y=y,
                            gap=gap,
                            color=color,
                            stem_down=stem_down,
                            flag_color=ink(("Flag", ci)) or ncol,
                        )
                    else:
                        self._note(p, x=x, y=y, gap=gap, color=color, value=value, stem_down=stem_down, font=font)
                    p.restore()
                p.setPen(QPen(ncol, 1.4))
                # A sign is written only where the note differs from what the key signature already says.
                if note.accidental != key_accidental(note.letter, count=self.key):
                    sign_ink = ink(("Accidental", ci, note.midi)) or ncol
                    ax = column_x - gap * (2.3 + 1.2 * (acc_slot % 3))
                    if row:
                        ax = column_x + row.signs[ci - row.first][acc_slot]
                    if font:
                        engraving.draw_accidental(
                            p,
                            font=font,
                            sign=note.accidental,
                            x=ax,
                            y=y,
                            gap=gap,
                            color=sign_ink,
                        )
                    else:
                        p.setPen(QPen(sign_ink, 1.4))
                        sign = ACCIDENTAL_SYMBOLS[note.accidental] or "♮"
                        sign_font = QFont("DejaVu Sans", int(gap * 2.0))
                        if row:
                            sign_font.setPixelSize(max(int(gap * 2 * 1.33), 6))
                        p.setFont(sign_font)
                        p.drawText(QPointF(ax, y + gap * 0.5), sign)
                    acc_slot += 1
        if self.notation_target:
            self._draw_notation_target(
                p,
                target=self.notation_target,
                heads=heads,
                x=x0 + step * (position + 0.5),
                bottom=staves[self.clef],
                accent=ink(self.notation_target) or fg,
                font=font,
            )
        for i, text in enumerate(self.wedges):  # the steps between neighboring notes, above them
            if text and i in heads and i + 1 in heads:
                self._draw_wedge(
                    p,
                    left=heads[i],
                    right=heads[i + 1],
                    text=text,
                    gap=gap,
                    color=self.wedge_colors.get(i) or self.column_colors.get(i + 1) or nfg,
                )

            elif row and text and i in heads and i + 1 < len(self.columns):
                # The second pitch is on the next line. Keep the interval label with its starting pitch.
                point = heads[i]
                label_font = QFont(self.font())
                label_font.setPixelSize(max(int(gap * 1.25), 11))
                label_font.setBold(True)
                p.setFont(label_font)
                p.setPen(self.wedge_colors.get(i) or self.column_colors.get(i + 1) or nfg)
                bounds = QRectF(point.x() - 2 * gap, point.y() - 5.5 * gap, 4 * gap, 2 * gap)
                p.drawText(bounds, Qt.AlignmentFlag.AlignCenter, f"{text} →")

    def _draw_notation_target(
        self,
        p: QPainter,
        *,
        target: tuple[str, int],
        heads: dict[int, QPointF],
        x: float,
        bottom: float,
        accent: QColor,
        font: str | None,
    ) -> None:
        """
        Draw the selected marking relative to the notes and staff of a notation question.

        Parameters
        ----------
        p : QPainter
            Painter already used for the phrase.
        target : tuple of (str, int)
            Term and position in the phrase. Keyword-only.
        heads : dict of int to QPointF
            Highest notehead in each occupied column. Keyword-only.
        x : float
            Horizontal center of the selected column. Keyword-only.
        bottom : float
            Bottom staff line in screen coordinates. Keyword-only.
        accent : QColor
            Highlight ink on the notation paper. Keyword-only.
        font : str or None
            Selected SMuFL font, or None for the built-in notation. Keyword-only.

        Examples
        --------
        >>> staff = StaffWidget()
        >>> staff.show_notes([[Note.parse("G4")]], notation_target=("Turn", 0))
        >>> staff.grab().isNull()
        False
        """
        term, position = target
        placement, symbol = MARKS[term]
        left, right, gap = self.side, self.width() - self.side, self.GAP
        middle = bottom - 2 * gap
        head = heads.get(position, QPointF(x, middle))
        if isinstance(symbol, int):
            path = engraving.notation_glyph(font or "bravura", codepoint=symbol)
            if placement == "meter digits":
                digits = path.translated(0, -25)
                digits.addPath(path.translated(0, 25))
                path = digits
            bounds = path.boundingRect()
            # Accidentals and rests use the font's pitch origin; other marks are centered in their lane.
            y = head.y()
            center = True
            if placement in ("accidental", "grace", "arpeggio"):
                x -= gap * (0.9 + bounds.width() / 50)
                center = placement == "arpeggio"
                if placement in ("grace", "arpeggio"):
                    y += gap / 2 if placement == "grace" else gap
            elif placement == "on stem":
                down = head.y() <= middle
                x += (-0.55 if down else 0.55) * gap
                y += (2 if down else -2) * gap
            elif placement == "rest":
                y = middle - (gap if term == "Whole rest" else 0)
                center = False
            elif placement in ("meter", "meter digits"):
                x, y = left + 4.5 * gap, middle
            elif placement == "bar":
                x, y = (left + self.note_offset if term == "Start repeat" else right - gap / 2), middle
            elif placement == "below":
                y = bottom + 4 * gap
            else:
                y = min(bottom - 5.5 * gap, head.y() - 4.7 * gap)
            # Long dynamics such as messa di voce must still fit beside the last note in a narrow pane.
            if placement in ("above", "below"):
                half_width = bounds.width() * gap / 50
                x = min(max(x, left + half_width), right - half_width)
            p.save()
            p.translate(x, y)
            p.scale(gap / 25, gap / 25)
            p.translate(-bounds.center().x(), -bounds.center().y() if center else 0)
            p.fillPath(path, accent)
            p.restore()
        elif term in ("Rehearsal mark", "Metronome mark"):
            y = bottom - 7 * gap
            p.setPen(QPen(accent, gap * 0.12))
            p.setBrush(Qt.BrushStyle.NoBrush)
            label_font = QFont(self.font())
            label_font.setPixelSize(round(gap * 1.3))
            p.setFont(label_font)
            rect = QRectF(left, y - gap, 2 * gap, 2 * gap)
            if term == "Rehearsal mark":
                p.drawRect(rect)
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "A")
            else:
                self._note(
                    p,
                    x=left + gap / 2,
                    y=y,
                    gap=gap * 0.55,
                    color=accent,
                    value="quarter",
                    stem_down=False,
                    font=font,
                )
                p.drawText(QPointF(left + 1.3 * gap, y), "= 96")
        elif term == "Augmentation dot":
            y = head.y()
            if round(2 * (bottom - y) / gap) % 2 == 0:
                y -= gap / 2
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(accent)
            p.drawEllipse(QPointF(x + gap, y), gap * 0.17, gap * 0.17)
        elif term in ("Tie", "Slur", "Beam", "Triplet", "Glissando"):
            first, last = heads[0], heads[2 if term == "Triplet" else 1]
            p.setPen(QPen(accent, gap * 0.14))
            if term == "Beam":
                offset = QPointF(gap * 0.56, -3.3 * gap)
                p.setPen(QPen(accent, gap * 0.48, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
                p.drawLine(first + offset, last + offset)
            elif term == "Glissando":
                p.drawLine(first + QPointF(gap, -2), last - QPointF(gap, -2))
            elif term == "Triplet":
                y = bottom - 6 * gap
                mid = (first.x() + last.x()) / 2
                for end, inner in ((first.x(), mid - gap / 2), (last.x(), mid + gap / 2)):
                    p.drawLine(QPointF(end, y + gap / 2), QPointF(end, y))
                    p.drawLine(QPointF(end, y), QPointF(inner, y))
                p.drawText(QRectF(mid - gap, y - gap, 2 * gap, 2 * gap), Qt.AlignmentFlag.AlignCenter, "3")
            else:
                start, end = first + QPointF(3, gap * 0.65), last + QPointF(-3, gap * 0.65)
                curve = QPainterPath(start)
                curve.quadTo((start.x() + end.x()) / 2, max(start.y(), end.y()) + gap * 1.4, end.x(), end.y())
                p.strokePath(curve, QPen(accent, gap * 0.14))

    def _draw_wedge(
        self,
        p: QPainter,
        *,
        left: QPointF,
        right: QPointF,
        text: str,
        gap: float,
        color: QColor,
    ) -> None:
        """
        Draw the step between two neighboring notes: two lines from the notes up to a point, and the letter over the point.

        The lines leave the tops of the two notes and meet above them, so the point is above the higher of the two.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        left : QPointF
            Where the left note was drawn: the middle of its head. Keyword-only.
        right : QPointF
            Where the right note was drawn. Keyword-only.
        text : str
            What to write over the point, such as "W". Keyword-only.
        gap : float
            The distance between staff lines. Keyword-only.
        color : QColor
            The color of the lines and the letter. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(200, 120, QImage.Format.Format_ARGB32)
        >>> image.fill(QColor("white"))
        >>> painter = QPainter(image)
        >>> staff, black = StaffWidget(), QColor("black")
        >>> staff._draw_wedge(painter, left=QPointF(40, 80), right=QPointF(140, 70), text="W", gap=12, color=black)
        >>> painter.end()
        True
        """
        reach, rise = gap * 0.6, gap * 1.3
        start = QPointF(left.x() + reach, left.y() - gap * 0.8)  # just above the left note
        end = QPointF(right.x() - reach, right.y() - gap * 0.8)  # and the right one
        point = QPointF((left.x() + right.x()) / 2, min(start.y(), end.y()) - rise)
        p.setPen(QPen(color, 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(start, point)
        p.drawLine(point, end)
        font = QFont(self.font())
        font.setPixelSize(max(int(gap * 1.25), 11))
        font.setBold(True)
        p.setFont(font)
        label = QRectF(
            point.x() - gap * 0.8,
            point.y() - gap * 1.6,
            gap * 1.6,
            gap * 1.5,
        )
        p.fillRect(label, QColor("white"))  # the paper, so that a staff line does not run through the letter
        p.drawText(label, Qt.AlignmentFlag.AlignCenter, text)

    @staticmethod
    def _note(
        p: QPainter,
        *,
        x: float,
        y: float,
        gap: float,
        color: QColor,
        value: str,
        stem_down: bool,
        font: str | None = None,
    ) -> None:
        """
        Draw a note of a value with its head centered on a point.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        x : float
            The head's center, in pixels. Keyword-only.
        y : float
            The head's center, in pixels. Keyword-only.
        gap : float
            The distance between staff lines, in pixels. Keyword-only.
        color : QColor
            The color to draw in. Keyword-only.
        value : str
            The note value. Keyword-only.
        stem_down : bool
            Draw the stem down. Keyword-only.
        font : str or None, default None
            A SMuFL font to engrave with; None uses the built-in Noto Music drawing.
            The double whole note always uses the square form. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(100, 100, QImage.Format.Format_ARGB32)
        >>> image.fill(QColor("white"))
        >>> painter = QPainter(image)
        >>> StaffWidget._note(painter, x=50, y=50, gap=16, color=QColor("black"), value="quarter", stem_down=False)
        >>> painter.end()
        True
        >>> image.pixelColor(50, 50).lightness() < 128
        True
        """
        if font is None and value not in ("whole", "breve") and not QFontDatabase.hasFamily("Noto Music"):
            font = "bravura"
        if font and value != "breve":  # the double whole note is always the square form, whatever the music font
            engraving.draw_note(
                p,
                font=font,
                value=value,
                x=x,
                y=y,
                gap=gap,
                color=color,
                stem_down=stem_down,
            )
        elif value == "whole":
            StaffWidget._whole_note(
                p,
                x=x,
                y=y,
                gap=gap,
                color=color,
            )
        else:
            draw_note(
                p,
                value=value,
                x=x,
                y=y,
                gap=gap,
                color=color,
                stem_down=stem_down,
            )

    @staticmethod
    def _draw_clef(
        p: QPainter,
        *,
        clef: str,
        x: float,
        bottom: float,
        gap: float,
        color: QColor = QColor("black"),
        font: str | None = None,
    ) -> None:
        """
        Draw a clef.

        From a SMuFL font if one is given, else as a Noto Music path scaled to its extent in gaps. The baritone clef is drawn as
        an F clef or a C clef, whichever is chosen in the settings.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        clef : str
            The clef's name. Keyword-only.
        x : float
            The clef's left edge, in pixels. Keyword-only.
        bottom : float
            The y position of the staff's bottom line, in pixels. Keyword-only.
        gap : float
            The distance between staff lines, in pixels. Keyword-only.
        color : QColor, default black
            The color to draw in. Keyword-only.
        font : str or None, default None
            A SMuFL font to engrave with. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(100, 100, QImage.Format.Format_ARGB32)
        >>> image.fill(QColor("white"))
        >>> painter = QPainter(image)
        >>> StaffWidget._draw_clef(painter, clef="treble", x=10, bottom=70, gap=10)
        >>> painter.end()
        True
        >>> any(image.pixelColor(x_, y).lightness() < 128 for x_ in range(10, 40) for y in range(20, 90))
        True
        """
        clef = clef_shape(clef)  # the baritone clef is an F clef or a C clef, as chosen in the settings
        if font is None and not QFontDatabase.hasFamily("Noto Music"):
            font = "bravura"
        if font:
            engraving.draw_clef(
                p,
                font=font,
                clef=clef,
                x=x,
                bottom=bottom,
                gap=gap,
                color=color,
            )
            return
        top, bot = CLEF_EXTENT[clef]
        path = QPainterPath()
        path.addText(
            0,
            0,
            QFont("Noto Music", 100),
            CLEF_GLYPH[clef],
        )
        r = path.boundingRect()
        scale = (top - bot) * gap / r.height()
        t = QTransform()
        t.translate(x, bottom - top * gap)
        t.scale(scale, scale)
        t.translate(-r.x(), -r.y())
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawPath(t.map(path))
        p.restore()

    @staticmethod
    def _brace(
        p: QPainter,
        *,
        x: float,
        y0: float,
        y1: float,
        color: QColor,
        wd: float = 11.0,
        font: str | None = None,
    ) -> None:
        """
        Draw a curly brace whose point faces left, for a grand staff.

        The music font's brace if it has one, else a drawn one.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        x : float
            The brace's right edge, in pixels. Keyword-only.
        y0 : float
            The top, in pixels. Keyword-only.
        y1 : float
            The bottom, in pixels. Keyword-only.
        color : QColor
            The color to draw in. Keyword-only.
        wd : float, default 11.0
            How wide to draw it, in pixels. Keyword-only.
        font : str or None, default None
            A SMuFL font to take the brace from. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(100, 100, QImage.Format.Format_ARGB32)
        >>> image.fill(QColor("white"))
        >>> painter = QPainter(image)
        >>> StaffWidget._brace(painter, x=40, y0=10, y1=90, color=QColor("black"))
        >>> painter.end()
        True
        >>> any(image.pixelColor(x_, 50).lightness() < 128 for x_ in range(20, 41))
        True
        """
        if font and engraving.draw_brace(
            p,
            font=font,
            x=x,
            y0=y0,
            y1=y1,
            color=color,
            width=wd * 1.25,
        ):
            return
        mid = (y0 + y1) / 2
        path = QPainterPath()
        path.moveTo(x, y0)
        path.cubicTo(
            x - wd,
            y0 + (mid - y0) * 0.25,
            x,
            mid - (mid - y0) * 0.35,
            x - wd,
            mid,
        )
        path.cubicTo(
            x,
            mid + (y1 - mid) * 0.35,
            x - wd,
            y1 - (y1 - mid) * 0.25,
            x,
            y1,
        )
        path.cubicTo(
            x - wd * 0.4,
            y1 - (y1 - mid) * 0.25,
            x - wd * 1.4,
            mid + (y1 - mid) * 0.3,
            x - wd * 1.4,
            mid,
        )
        path.cubicTo(
            x - wd * 1.4,
            mid - (mid - y0) * 0.3,
            x - wd * 0.4,
            y0 + (mid - y0) * 0.25,
            x,
            y0,
        )
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawPath(path)
        p.restore()

    @staticmethod
    def _whole_note(
        p: QPainter,
        *,
        x: float,
        y: float,
        gap: float,
        color: QColor = QColor("black"),
    ) -> None:
        """
        Draw a whole note: a black oval with a tilted hole that the staff line shows through.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        x : float
            The head's center, in pixels. Keyword-only.
        y : float
            The head's center, in pixels. Keyword-only.
        gap : float
            The distance between staff lines, which sets the size. Keyword-only.
        color : QColor, default black
            The color to draw in. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(100, 100, QImage.Format.Format_ARGB32)
        >>> image.fill(QColor("white"))
        >>> painter = QPainter(image)
        >>> StaffWidget._whole_note(painter, x=50, y=50, gap=20)
        >>> painter.end()
        True
        >>> image.pixelColor(62, 50).lightness() < 128  # the ring is dark ...
        True
        >>> image.pixelColor(50, 50).lightness() > 200  # ... and the hole is clear
        True
        """
        outer = QPainterPath()
        outer.addEllipse(QPointF(0, 0), gap * 0.74, gap * 0.5)
        hole = QPainterPath()
        hole.addEllipse(QPointF(0, 0), gap * 0.38, gap * 0.42)
        t = QTransform()
        t.rotate(-35)
        shape = outer.subtracted(t.map(hole))  # transparent hole: staff line shows through
        p.save()
        p.translate(x, y)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawPath(shape)
        p.restore()

    @staticmethod
    def _ledger(
        p: QPainter,
        *,
        x: float,
        y: float,
        gap: float,
    ) -> None:
        """
        Draw a ledger line, a little wider than the note head (which is about 0.74 gap either side of center).

        Parameters
        ----------
        p : QPainter
            The painter to draw with, with its pen already set.
        x : float
            The center of the line, in pixels. Keyword-only.
        y : float
            The line's height, in pixels. Keyword-only.
        gap : float
            The distance between staff lines; the line reaches one gap either side of `x`. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(100, 40, QImage.Format.Format_ARGB32)
        >>> image.fill(QColor("white"))
        >>> painter = QPainter(image)
        >>> painter.setPen(QColor("black"))
        >>> StaffWidget._ledger(painter, x=50, y=20, gap=16)
        >>> painter.end()
        True
        >>> image.pixelColor(40, 20).lightness() < 128
        True
        """
        p.drawLine(QPointF(x - gap, y), QPointF(x + gap, y))


def _repaint_staffs() -> None:
    """
    Paint every staff on screen again, after the notation style changed.

    Examples
    --------
    >>> _repaint_staffs()  # with no staffs open, nothing happens
    """
    _lesson_header_bounds.cache_clear()  # the baritone clef shape can change within a notation style
    for w in QApplication.allWidgets():
        if isinstance(w, StaffWidget):
            if w.lesson_layout:
                w._fit_width()
                w._fit_height(w.clef)
            w.update()


on_redraw(_repaint_staffs)
