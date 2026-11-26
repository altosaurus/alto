"""Staffless rhythm notation for lesson and glossary examples."""

from collections.abc import Iterator
from dataclasses import dataclass
from fractions import Fraction
from itertools import groupby
from math import ceil

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFocusEvent,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
    QResizeEvent,
)
from PySide6.QtWidgets import QPushButton, QStyle, QStyleOptionButton, QWidget

from alto.settings import (
    BEAT_TUPLET_NAMES,
    RHYTHM_BEAM_COUNTS,
    RHYTHM_DURATIONS,
    beat_note,
)
from alto.ui import engraving
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.notation import current
from alto.ui.pictures import REST_GLYPHS, RHYTHM_SYMBOL_NAMES
from alto.ui.zoom import px

_BARLINE_ABOVE = 3.7  # staff spaces above and below the noteheads
_BARLINE_BELOW = 0.7
_SYMBOL_NAMES = RHYTHM_SYMBOL_NAMES | {
    f"dotted-{rest}": f"Dotted {RHYTHM_SYMBOL_NAMES[rest].lower()}"
    for rest in REST_GLYPHS
}


def _draw_signature(
    painter: QPainter,
    *,
    meter: tuple[int, int],
    center: QPointF,
    gap: float,
    color: QColor,
    row_padding: float = 0.0,
) -> None:
    """
    Engrave the time signature with each number centered in its row.

    Parameters
    ----------
    painter : QPainter
        The painter receiving the two rows of music glyphs.
    meter : tuple of int
        The numerator and denominator.
    center : QPointF
        The midpoint between the two rows.
    gap : float
        The engraving scale in staff-space units.
    color : QColor
        The ink color.
    row_padding : float
        Extra distance from the midpoint to each row.

    Examples
    --------
    >>> MeterButton("12/8", meter=(12, 8)).grab().isNull()
    False
    """
    font = current().font or "bravura"
    for row, number in enumerate(meter):
        line = QPainterPath()
        for char in str(number):
            digit = engraving.notation_glyph(
                font,
                codepoint=0xE080 + int(char),
            )
            line.addPath(
                digit.translated(
                    line.boundingRect().right()
                    + 3
                    - digit.boundingRect().left(),
                    0,
                ),
            )
        painter.save()
        y = center.y() + (2 * row - 1) * (gap + row_padding)
        painter.translate(center.x(), y)
        painter.scale(gap / 25, gap / 25)
        ink_center = line.boundingRect().center()
        painter.fillPath(
            line.translated(-ink_center.x(), -ink_center.y()),
            color,
        )
        painter.restore()


class MeterButton(QPushButton):
    """
    Draw a stacked time signature in a standard answer button.

    Examples
    --------
    >>> MeterButton("12/8", meter=(12, 8)).accessibleName()
    '12/8'
    """

    def __init__(self, text: str, *, meter: tuple[int, int]) -> None:
        """
        Keep the plain signature as the text and accessible name.

        Parameters
        ----------
        text : str
            The time signature written with a slash.
        meter : tuple of int
            The numerator and denominator to engrave.

        Examples
        --------
        >>> MeterButton("3/4", meter=(3, 4)).text()
        '3/4'
        """
        super().__init__(text)
        self.meter = meter
        self.setAccessibleName(text)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw the styled button chrome and engrave its label.

        Parameters
        ----------
        event : QPaintEvent
            The paint request.

        Examples
        --------
        >>> MeterButton("6/8", meter=(6, 8)).grab().isNull()
        False
        """
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ""
        with QPainter(self) as painter:
            self.style().drawControl(
                QStyle.ControlElement.CE_PushButton,
                option,
                painter,
                self,
            )
            rect = self.style().subElementRect(
                QStyle.SubElement.SE_PushButtonContents,
                option,
                self,
            )
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            _draw_signature(
                painter,
                meter=self.meter,
                center=QRectF(rect).center(),
                gap=px(8),
                row_padding=px(2),
                color=option.palette.color(QPalette.ColorRole.ButtonText),
            )


@dataclass(frozen=True)
class _Symbol:
    """A written symbol with its sounding onset and place in the bar."""

    value: str
    tuplet: int
    duration: float
    onset: int
    offset: float
    space: float  # horizontal position in staff spaces from the first note
    advance: float  # staff spaces allocated to this symbol
    count: str
    tie_forward: bool


@dataclass(frozen=True)
class _BarLayout:
    """A fitted bar with its pixel scale and note baseline."""

    left: float
    width: float
    baseline: float
    scale: float

    def x(self, space: float) -> float:
        """
        Locate a notehead or beat marker within the fitted bar.

        Parameters
        ----------
        space : float
            Distance from the first notehead in staff spaces.

        Returns
        -------
        float
            Horizontal coordinate in the widget.
        """
        return self.left + px(16) + space * self.scale


class MeterStaff(QWidget):
    """Lay out rhythm on one baseline and wrap at bar lines."""

    _min_eighth_spaces = 0.0
    _space_below = _BARLINE_BELOW

    def __init__(self) -> None:
        """Create an empty rhythm example."""
        super().__init__()
        self.meter = (4, 4)
        self.values: tuple[str, ...] = ()
        self.bar_line = ""
        self.playback_column: int | None = None
        self.playback_ink: QColor | None = None
        self._measures: list[list[_Symbol]] = []
        self._bar_length = 16.0
        self._beat_length = 4.0
        self._bars_per_row = 1
        self._fitting_height = False
        self._counts_visible = False
        self._signature_visible = True
        self._has_tuplets = False

    def show_score(
        self,
        values: tuple[str, ...],
        *,
        meter: tuple[int, int] = (4, 4),
        counts: tuple[str, ...] = (),
        bar_line: str = "",
        show_signature: bool = True,
    ) -> None:
        """
        Show the rhythm. Tilde-joined notes share a playback step.

        Parameters
        ----------
        values : tuple of str
            Note values and rests in playback order.
        meter : tuple of int
            Numerator and denominator of the time signature.
        counts : tuple of str
            Optional spoken labels for each onset.
        bar_line : str
            Single or double bar line to emphasize in the glossary.
        show_signature : bool
            Draw and announce the time signature.
        """
        self.values = values
        self.meter = meter
        self.bar_line = bar_line
        self._signature_visible = show_signature
        self.playback_column = None
        numerator, denominator = meter
        unit = RHYTHM_DURATIONS["whole"] / denominator
        self._bar_length = numerator * unit
        self._beat_length = (
            3 * unit if meter in ((6, 8), (9, 8), (12, 8)) else unit
        )
        self._measures.clear()
        bar_length = Fraction(self._bar_length)
        offset = Fraction(0)
        self._has_tuplets = False
        description = []
        for onset, group in enumerate(values):
            parts = group.split("~")
            names = []
            for i, token in enumerate(parts):
                value, tuplet, duration = beat_note(token)
                names.append(_SYMBOL_NAMES[value])
                if tuplet:
                    self._has_tuplets = True
                if offset == 0:
                    self._measures.append([])
                measure = self._measures[-1]
                base = value.removeprefix("dotted-").removesuffix("-rest")
                advance = engraving.NOTE_ADVANCE[base]
                if value.startswith("dotted-"):
                    advance += 0.5
                space = (
                    measure[-1].space + measure[-1].advance if measure else 0
                )
                min_advance = (
                    self._min_eighth_spaces
                    * duration
                    / RHYTHM_DURATIONS["eighth"]
                )
                count = (
                    counts[onset]
                    if counts and i == 0
                    else self._count(float(offset))
                )
                symbol = _Symbol(
                    value,
                    tuplet,
                    float(duration),
                    onset,
                    float(offset),
                    space,
                    max(advance, min_advance),
                    count,
                    i < len(parts) - 1,
                )
                measure.append(symbol)
                offset = (offset + duration) % bar_length
            description.append(" tied to ".join(names))
        if show_signature:
            self.setAccessibleName(f"{numerator}/{denominator} rhythm")
        else:
            self.setAccessibleName("Written rhythm")
        if show_signature and not self._has_tuplets:
            self.setAccessibleDescription(", ".join(description))
        else:
            self.setAccessibleDescription(
                ". ".join(
                    f"Measure {i}: " + self._describe_measure(measure)
                    for i, measure in enumerate(self._measures, 1)
                ),
            )
        self.setMaximumWidth(self.sizeHint().width())
        self._fit()
        self.updateGeometry()
        self.update()

    def _groups(self, measure: list[_Symbol]) -> Iterator[list[_Symbol]]:
        """
        Group ordinary subdivisions by beat and tuplets by their number.

        Parameters
        ----------
        measure : list of _Symbol
            Symbols in one measure.

        Yields
        ------
        list of _Symbol
            Symbols sharing a beam or a numbered tuplet bracket.
        """
        for (count, _, _), run in groupby(
            measure,
            key=lambda s: (
                s.tuplet,
                0 if s.tuplet else s.offset // self._beat_length,
                s.value.removesuffix("-rest") if s.tuplet else s.value,
            ),
        ):
            symbols = list(run)
            size = count or len(symbols)
            for start in range(0, len(symbols), size):
                yield symbols[start : start + size]

    def _describe_measure(self, measure: list[_Symbol]) -> str:
        """
        Describe the note values and any visible beam groups.

        Parameters
        ----------
        measure : list of _Symbol
            The symbols drawn between two bar lines.

        Returns
        -------
        str
            A spoken description of the written rhythm.

        Examples
        --------
        >>> MeterStaff()._describe_measure([])
        ''
        """
        readout = []
        for group in self._groups(measure):
            names = [_SYMBOL_NAMES[s.value] for s in group]
            if group[0].tuplet:
                kind = BEAT_TUPLET_NAMES[group[0].tuplet]
                readout.append(f"{kind} of " + " and ".join(names))
            elif group[0].value in RHYTHM_BEAM_COUNTS and len(names) > 1:
                readout.append("beamed group of " + " and ".join(names))
            else:
                readout.extend(names)
        return ", ".join(readout)

    def _count(self, offset: float) -> str:
        """
        Return the beat number or subdivision at a written onset.

        Returns
        -------
        str
            The count at this position in the measure.
        """
        beat, remainder = divmod(offset, self._beat_length)
        if remainder == 0:
            return str(int(beat) + 1)
        if remainder == self._beat_length / 2:
            return "&"
        return {1.0: "la", 2.0: "li"}.get(
            3 * remainder / self._beat_length,
            "",
        )

    def set_counts_visible(self, visible: bool) -> None:
        """Show or hide the counts below the notes."""
        self._counts_visible = visible
        self._fit()
        self.update()

    def highlight_column(self, column: int | None) -> None:
        """Highlight the symbols that share a sounding onset."""
        self.playback_column = column
        self.update()

    def sizeHint(self) -> QSize:
        """
        Prefer one line at the natural rhythmic spacing.

        Returns
        -------
        QSize
            Preferred size for one line.
        """
        width = (
            self._header_width()
            + px(8)
            + sum(self._bar_width(bar) for bar in range(len(self._measures)))
        )
        return QSize(width, self._row_height())

    def _header_width(self) -> int:
        """
        Reserve only the left margin when the signature is hidden.

        Returns
        -------
        int
            Width before the first measure.

        Examples
        --------
        >>> MeterStaff()._header_width() > 0
        True
        """
        return px(32 if self._signature_visible else 8)

    def minimumSizeHint(self) -> QSize:
        """
        Keep dense subdivisions legible when measures wrap.

        Returns
        -------
        QSize
            Width for one bar at a readable scale and one row of music.
        """
        width = max(
            (self._bar_width(bar) for bar in range(len(self._measures))),
            default=0,
        )
        return QSize(
            self._header_width() + round(width * 0.8) + px(8),
            self._row_height(),
        )

    def _bar_width(self, index: int) -> int:
        """
        Fit the written symbols and leave clearance at the bar line.

        Parameters
        ----------
        index : int
            Measure in reading order.

        Returns
        -------
        int
            Width of one measure at the current zoom.
        """
        last = self._measures[index][-1]
        return px(16) + ceil((last.space + last.advance) * px(10))

    def _row_height(self) -> int:
        """
        Leave room for upward stems, ties, and optional counts.

        Returns
        -------
        int
            Height of a single row at the current zoom.
        """
        return px(88 if self._counts_visible else 70) + self._tuplet_height()

    def _tuplet_height(self) -> int:
        """
        Reserve room above the stems for a tuplet bracket and number.

        Returns
        -------
        int
            Extra row height in pixels.
        """
        return px(18) if self._has_tuplets else 0

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Reflow whole measures at the available width."""
        super().resizeEvent(event)
        if event.size().width() != event.oldSize().width():
            self._fit()

    def _fit(self) -> None:
        """Fit complete bars and reserve the height of all systems."""
        if self._fitting_height:
            return
        # Setting the height can make the parent change our width before
        # Qt has finished updating both height constraints.
        self._fitting_height = True
        try:
            while True:
                width = self.width()
                self._bars_per_row = self._bars_that_fit(width)
                rows = max(1, ceil(len(self._measures) / self._bars_per_row))
                self.setFixedHeight(rows * self._row_height())
                if self.width() == width:
                    break
        finally:
            self._fitting_height = False

    def _bars_that_fit(self, width: int) -> int:
        """
        Count the bars per row at the available width.

        Parameters
        ----------
        width : int
            Width available for the rhythm in pixels.

        Returns
        -------
        int
            Number of bars per row for a balanced layout.
        """
        bars = len(self._measures)
        widths = [self._bar_width(i) for i in range(bars)]
        for count in range(bars, 1, -1):
            if bars % count == 0 and all(
                sum(widths[i : i + count])
                + (self._header_width() if i == 0 else px(8))
                + px(8)
                <= width
                for i in range(0, bars, count)
            ):
                return count
        return 1

    def _measure_geometry(self, index: int) -> _BarLayout:
        """
        Share the engraved bar placement with hit testing.

        Parameters
        ----------
        index : int
            Zero-based measure index in reading order.

        Returns
        -------
        _BarLayout
            Bar edges, note baseline, and fitted horizontal scale.

        Examples
        --------
        >>> MeterStaff()._measure_geometry(0).baseline > 0
        True
        """
        row, col = divmod(index, self._bars_per_row)
        below = 3.1 if self._counts_visible else self._space_below
        center_y = (row + 0.5) * self._row_height()
        y = (
            center_y
            + ((_BARLINE_ABOVE - below) * px(10) + self._tuplet_height()) / 2
        )
        header = self._header_width() if row == 0 else px(8)
        left = header + sum(
            self._bar_width(i) for i in range(index - col, index)
        )
        if not self._measures:
            return _BarLayout(left, 0, y, px(10))
        last = self._measures[index][-1]
        spaces = last.space + last.advance
        available = max(0, self.width() - left - px(8) - px(16))
        scale = min(px(10), available / spaces)
        return _BarLayout(left, px(16) + ceil(spaces * scale), y, scale)

    def paintEvent(self, _: QPaintEvent) -> None:
        """Draw the time signature and a line at each bar boundary."""
        with QPainter(self) as p:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("white"))
            p.drawRoundedRect(self.rect(), px(6), px(6))
            gap = px(10)
            count_font = self.font()
            count_font.setPixelSize(px(12))
            p.setFont(count_font)
            for i, measure in enumerate(self._measures):
                bar = self._measure_geometry(i)
                y = bar.baseline
                if i == 0 and self._signature_visible:
                    _draw_signature(
                        p,
                        meter=self.meter,
                        center=QPointF(px(16), y - 1.5 * gap),
                        gap=gap,
                        color=QColor("black"),
                    )
                self._draw_measure(p, measure=measure, bar=bar)
                end = bar.left + bar.width
                bar_ink = (
                    self.palette().highlight().color()
                    if self.bar_line
                    else QColor("black")
                )
                p.setPen(QPen(bar_ink, gap * 0.14))
                p.drawLine(
                    QPointF(end, y - _BARLINE_ABOVE * gap),
                    QPointF(end, y + _BARLINE_BELOW * gap),
                )
                if self.bar_line == "Double barline":
                    end -= 0.5 * gap
                    p.drawLine(
                        QPointF(end, y - _BARLINE_ABOVE * gap),
                        QPointF(end, y + _BARLINE_BELOW * gap),
                    )

    def _draw_measure(
        self,
        p: QPainter,
        *,
        measure: list[_Symbol],
        bar: _BarLayout,
    ) -> None:
        """Engrave each symbol and beam subdivisions within a beat."""
        gap = px(10)
        font = current().font or "bravura"
        ink = QColor("black")
        accent = self.playback_ink or self.palette().highlight().color()
        y = bar.baseline
        for symbols in self._groups(measure):
            value = symbols[0].value
            heads = [QPointF(bar.x(s.space), y) for s in symbols]
            colors = [
                accent if s.onset == self.playback_column else ink
                for s in symbols
            ]
            beamed = (
                value in RHYTHM_BEAM_COUNTS
                and len(heads) > 1
                and all(s.value == value for s in symbols)
            )
            if symbols[0].tuplet:
                self._draw_tuplet(p, heads=heads, number=symbols[0].tuplet)
            if beamed:
                engraving.draw_beamed_notes(
                    p,
                    font=font,
                    heads=heads,
                    colors=colors,
                    gap=gap,
                    middle=y,
                    ink=ink,
                    beams=RHYTHM_BEAM_COUNTS[value],
                )
            for symbol, head, color in zip(
                symbols,
                heads,
                colors,
                strict=True,
            ):
                if not beamed:
                    self._draw_symbol(
                        p,
                        value=symbol.value,
                        head=head,
                        color=color,
                    )
                x = head.x()
                if symbol.tie_forward:
                    reach = symbol.advance * bar.scale
                    tie = QPainterPath(QPointF(x + gap / 3, y + gap / 2))
                    tie.quadTo(
                        x + reach / 2,
                        y + gap * 1.5,
                        x + reach - gap / 3,
                        y + gap / 2,
                    )
                    p.strokePath(tie, QPen(color, gap * 0.15))
                if self._counts_visible:
                    p.setPen(color)
                    rect = QRectF(x - px(18), y + px(13), px(36), px(18))
                    p.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignCenter,
                        symbol.count,
                    )

    @staticmethod
    def _draw_tuplet(
        p: QPainter,
        *,
        heads: list[QPointF],
        number: int,
    ) -> None:
        """Place a numbered bracket above the notes it groups."""
        p.save()
        gap = px(10)
        y = heads[0].y() - 4.5 * gap
        left, right = heads[0].x(), heads[-1].x()
        middle = (left + right) / 2
        p.setPen(QPen(QColor("black"), gap * 0.12))
        for end, inner in (
            (left, middle - gap * 0.6),
            (right, middle + gap * 0.6),
        ):
            p.drawLine(QPointF(end, y + gap * 0.4), QPointF(end, y))
            p.drawLine(QPointF(end, y), QPointF(inner, y))
        p.drawText(
            QRectF(middle - gap, y - gap, 2 * gap, 2 * gap),
            Qt.AlignmentFlag.AlignCenter,
            str(number),
        )
        p.restore()

    @staticmethod
    def _draw_symbol(
        p: QPainter,
        *,
        value: str,
        head: QPointF,
        color: QColor,
    ) -> None:
        """Engrave a rest or an upward-stemmed note and its dot."""
        gap = px(10)
        font = current().font or "bravura"
        x, y = head.x(), head.y()
        base = value.removeprefix("dotted-")
        if base in REST_GLYPHS:
            path = engraving.notation_glyph(font, codepoint=REST_GLYPHS[base])
            p.save()
            y -= 1.4 * gap
            p.translate(x, y)
            p.scale(gap / 25, gap / 25)
            bounds = path.boundingRect()
            p.translate(-bounds.center())
            p.fillPath(path, color)
            if base in {"whole-rest", "half-rest"}:
                line = (
                    bounds.top() if base == "whole-rest" else bounds.bottom()
                )
                p.fillRect(
                    QRectF(
                        bounds.left() - 8,
                        line - 2,
                        bounds.width() + 16,
                        4,
                    ),
                    color,
                )
            p.restore()
        else:
            engraving.draw_note(
                p,
                font=font,
                value=base,
                x=x,
                y=y,
                gap=gap,
                color=color,
            )
        if value.startswith("dotted-"):
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawEllipse(
                QPointF(x + 1.1 * gap, y - 0.22 * gap),
                gap * 0.2,
                gap * 0.2,
            )


class BeatPlacementStaff(MeterStaff):
    """
    Let a learner toggle beat markers at eighth-note positions.

    Examples
    --------
    >>> BeatPlacementStaff().marks
    []
    """

    changed = Signal()
    cursor_moved = Signal(QPointF)
    # Leave room for each selectable blank underneath a sustained note.
    _min_eighth_spaces = 1.6
    _space_below = 2.5  # room for the marker and its focus outline

    def __init__(self) -> None:
        """
        Start with no selected or graded positions.

        Examples
        --------
        >>> BeatPlacementStaff().active_slot
        0
        """
        super().__init__()
        self.marks: list[int] = []
        self.active_slot = 0
        self.feedback: bool | None = None
        self.playback_ink = QColor(CORRECT_ANSWER_COLOR)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def reset(
        self,
        values: tuple[str, ...],
        *,
        meter: tuple[int, int],
    ) -> None:
        """
        Replace the score and clear the learner's marks.

        Parameters
        ----------
        values : tuple of str
            The rhythm to engrave.
        meter : tuple of int
            The time signature.

        Examples
        --------
        >>> staff = BeatPlacementStaff()
        >>> staff.reset(("quarter",) * 4, meter=(2, 4))
        >>> staff.slots_per_bar
        4
        """
        self.marks.clear()
        self.active_slot = 0
        self.feedback = None
        self.show_score(values, meter=meter)
        self._announce()

    @property
    def slots_per_bar(self) -> int:
        """
        Count eighth-note positions per measure.

        Returns
        -------
        int
            The number of subdivisions selectable in each measure.

        Examples
        --------
        >>> BeatPlacementStaff().slots_per_bar
        8
        """
        return int(self._bar_length / RHYTHM_DURATIONS["eighth"])

    def _row_height(self) -> int:
        """
        Leave space for the numbered blanks below the score.

        Returns
        -------
        int
            The height of one system at the current zoom.

        Examples
        --------
        >>> base_height = MeterStaff()._row_height()
        >>> BeatPlacementStaff()._row_height() > base_height
        True
        """
        return super()._row_height() + px(8)

    def beat_numbers(self) -> dict[int, int]:
        """
        Return beat numbers in reading order within each measure.

        Returns
        -------
        dict of int to int
            The beat number shown at each selected eighth-note position.

        Examples
        --------
        >>> staff = BeatPlacementStaff()
        >>> staff.marks = [10, 4, 8, 0]
        >>> staff.beat_numbers()
        {0: 1, 4: 2, 8: 1, 10: 2}
        """
        return {
            slot: number
            for _, measure in groupby(
                sorted(self.marks),
                key=lambda slot: slot // self.slots_per_bar,
            )
            for number, slot in enumerate(measure, 1)
        }

    def position(self, slot: int) -> QPointF:
        """
        Locate a selectable position below its corresponding rhythm.

        Parameters
        ----------
        slot : int
            Zero-based eighth-note position across the score.

        Returns
        -------
        QPointF
            The center of the marker.

        Examples
        --------
        >>> BeatPlacementStaff().position(0).y() > 0
        True
        """
        bar, offset = divmod(slot, self.slots_per_bar)
        layout = self._measure_geometry(bar)
        space = 0.0
        if self._measures:
            measure = self._measures[bar]
            time = offset * RHYTHM_DURATIONS["eighth"]
            symbol = next(s for s in reversed(measure) if s.offset <= time)
            fraction = (time - symbol.offset) / symbol.duration
            space = symbol.space + fraction * symbol.advance
        return QPointF(layout.x(space), layout.baseline + px(17))

    def _announce(self) -> None:
        """
        Announce the focused position and mark count.

        Examples
        --------
        >>> staff = BeatPlacementStaff()
        >>> staff._announce()
        >>> "Measure 1" in staff.accessibleName()
        True
        """
        bar, offset = divmod(self.active_slot, self.slots_per_bar)
        number = self.beat_numbers().get(self.active_slot)
        status = "Blank" if number is None else f"Beat {number}"
        self.setAccessibleName(
            f"{self.meter[0]}/{self.meter[1]} rhythm. Measure {bar + 1}, "
            f"eighth-note position {offset + 1}. {status}. "
            f"{len(self.marks)} marks.",
        )

    def _toggle(self) -> None:
        """
        Add or remove a mark at the active position.

        Examples
        --------
        >>> staff = BeatPlacementStaff()
        >>> staff._toggle()
        >>> staff.marks
        [0]
        """
        if self.active_slot in self.marks:
            self.marks.remove(self.active_slot)
        else:
            self.marks.append(self.active_slot)
        self.feedback = None
        self._announce()
        self.update()
        self.changed.emit()

    def undo(self) -> None:
        """
        Remove the most recently added beat marker.

        Examples
        --------
        >>> staff = BeatPlacementStaff()
        >>> staff._toggle()
        >>> staff.undo()
        >>> staff.marks
        []
        """
        if self.marks:
            self.active_slot = self.marks[-1]
            self._toggle()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Toggle the nearest subdivision in the clicked measure.

        Parameters
        ----------
        event : QMouseEvent
            The click in local coordinates.

        Examples
        --------
        Tested with clicks on notes and beneath sustained notes.
        """
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        point = event.position()
        for bar in range(len(self._measures)):
            layout = self._measure_geometry(bar)
            top = (bar // self._bars_per_row) * self._row_height()
            if (
                layout.left <= point.x() < layout.left + layout.width
                and top <= point.y() < top + self._row_height()
            ):
                start = bar * self.slots_per_bar
                self.active_slot = min(
                    range(start, start + self.slots_per_bar),
                    key=lambda slot: abs(self.position(slot).x() - point.x()),
                )
                self._toggle()
                return

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Move the active position with arrows and toggle it with Space.

        Parameters
        ----------
        event : QKeyEvent
            The key pressed while the rhythm has focus.

        Examples
        --------
        Keyboard input reaches the same subdivisions as a click.
        """
        key = event.key()
        steps: dict[int, int] = {
            Qt.Key.Key_Left: -1,
            Qt.Key.Key_Right: 1,
            Qt.Key.Key_Up: -self.slots_per_bar,
            Qt.Key.Key_Down: self.slots_per_bar,
        }
        if key in steps and self._measures:
            self.active_slot = max(
                0,
                min(
                    len(self._measures) * self.slots_per_bar - 1,
                    self.active_slot + steps[key],
                ),
            )
            self._announce()
            self.cursor_moved.emit(self.position(self.active_slot))
            self.update()
        elif key == Qt.Key.Key_Space and self._measures:
            self._toggle()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        """
        Repaint the keyboard cursor when the rhythm receives focus.

        Parameters
        ----------
        event : QFocusEvent
            The focus change.

        Examples
        --------
        The focused score outlines the current selectable position.
        """
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """
        Hide the keyboard cursor when focus leaves the rhythm.

        Parameters
        ----------
        event : QFocusEvent
            The focus change.

        Examples
        --------
        Placed beats remain visible when focus moves to Answer.
        """
        super().focusOutEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw the subdivision blanks, beat numbers, and keyboard focus.

        Parameters
        ----------
        event : QPaintEvent
            The paint request.

        Examples
        --------
        >>> BeatPlacementStaff().grab().isNull()
        False
        """
        super().paintEvent(event)
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            font = painter.font()
            font.setPixelSize(px(12))
            painter.setFont(font)
            numbers = self.beat_numbers()
            ink = (
                QColor(CORRECT_ANSWER_COLOR)
                if self.feedback is True
                else QColor("#c62828")
                if self.feedback is False
                else QColor("#235a96")
            )
            blank_radii = [
                min(px(6), self._measure_geometry(i).scale * 0.6)
                for i in range(len(self._measures))
            ]
            for slot in range(len(self._measures) * self.slots_per_bar):
                point = self.position(slot)
                radius = blank_radii[slot // self.slots_per_bar]
                number = numbers.get(slot)
                rect = QRectF(
                    point.x() - px(8),
                    point.y() - px(8),
                    px(16),
                    px(16),
                )
                color = ink if number is not None else QColor("#858585")
                painter.setPen(QPen(color, px(1)))
                painter.drawLine(
                    point + QPointF(-radius, px(7)),
                    point + QPointF(radius, px(7)),
                )
                if number is not None:
                    painter.drawText(
                        rect,
                        Qt.AlignmentFlag.AlignCenter,
                        str(number),
                    )
                if self.hasFocus() and slot == self.active_slot:
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(QColor("#235a96"), px(1)))
                    painter.drawRoundedRect(rect, px(3), px(3))
