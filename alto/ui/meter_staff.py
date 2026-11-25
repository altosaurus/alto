"""Staffless rhythm notation for lesson and glossary examples."""

from dataclasses import dataclass
from itertools import groupby
from math import ceil

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QResizeEvent,
)
from PySide6.QtWidgets import QWidget

from alto.settings import RHYTHM_DURATIONS
from alto.ui import engraving
from alto.ui.notation import current
from alto.ui.pictures import REST_GLYPHS, RHYTHM_SYMBOL_NAMES
from alto.ui.zoom import px


@dataclass(frozen=True)
class _Symbol:
    """A written symbol with its sounding onset and place in the bar."""

    value: str
    onset: int
    offset: float
    count: str
    tie_forward: bool


class MeterStaff(QWidget):
    """Lay out rhythm on one baseline and wrap at bar lines."""

    def __init__(self) -> None:
        """Create an empty rhythm example."""
        super().__init__()
        self.meter = (4, 4)
        self.values: tuple[str, ...] = ()
        self.bar_line = ""
        self.playback_column: int | None = None
        self._measures: list[list[_Symbol]] = []
        self._bar_length = 16.0
        self._beat_length = 4.0
        self._bars_per_row = 1
        self._counts_visible = False

    def show_score(
        self,
        values: tuple[str, ...],
        *,
        meter: tuple[int, int] = (4, 4),
        counts: tuple[str, ...] = (),
        bar_line: str = "",
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
        """
        self.values = values
        self.meter = meter
        self.bar_line = bar_line
        self.playback_column = None
        numerator, denominator = meter
        unit = RHYTHM_DURATIONS["whole"] / denominator
        self._bar_length = numerator * unit
        self._beat_length = (
            3 * unit if meter in ((6, 8), (9, 8), (12, 8)) else unit
        )
        self._measures.clear()
        offset = 0.0
        description = []
        for onset, group in enumerate(values):
            parts = group.split("~")
            description.append(
                " tied to ".join(RHYTHM_SYMBOL_NAMES[v] for v in parts),
            )
            for i, value in enumerate(parts):
                if offset == 0:
                    self._measures.append([])
                count = (
                    counts[onset] if counts and i == 0 else self._count(offset)
                )
                symbol = _Symbol(
                    value,
                    onset,
                    offset,
                    count,
                    i < len(parts) - 1,
                )
                self._measures[-1].append(symbol)
                offset = (offset + RHYTHM_DURATIONS[value]) % self._bar_length
        self.setAccessibleName(f"{numerator}/{denominator} rhythm")
        self.setAccessibleDescription(", ".join(description))
        self.setMaximumWidth(self.sizeHint().width())
        self._fit()
        self.updateGeometry()
        self.update()

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
        width = px(40) + len(self._measures) * self._bar_width()
        return QSize(width, self._row_height())

    def _bar_width(self) -> int:
        """
        Give longer measures more horizontal space.

        Returns
        -------
        int
            Width of one measure at the current zoom.
        """
        return px(14 + self._bar_length * 10)

    def _row_height(self) -> int:
        """
        Leave room for upward stems, ties, and optional counts.

        Returns
        -------
        int
            Height of a single row at the current zoom.
        """
        return px(88 if self._counts_visible else 70)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Reflow whole measures at the available width."""
        super().resizeEvent(event)
        if event.size().width() != event.oldSize().width():
            self._fit()

    def _fit(self) -> None:
        """Fit complete bars and reserve the height of all systems."""
        bars = len(self._measures)
        self._bars_per_row = max(
            1,
            min(bars, (self.width() - px(40)) // self._bar_width()),
        )
        while bars % self._bars_per_row:
            self._bars_per_row -= 1
        self.setFixedHeight(
            max(1, ceil(bars / self._bars_per_row)) * self._row_height(),
        )

    def paintEvent(self, _: QPaintEvent) -> None:
        """Draw the time signature and a line at each bar boundary."""
        with QPainter(self) as p:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("white"))
            p.drawRoundedRect(self.rect(), px(6), px(6))
            font = current().font or "bravura"
            gap = px(10)
            count_font = self.font()
            count_font.setPixelSize(px(12))
            p.setFont(count_font)
            for i, measure in enumerate(self._measures):
                row, col = divmod(i, self._bars_per_row)
                y = row * self._row_height() + px(48)
                header = px(32 if row == 0 else 8)
                width = min(
                    self._bar_width(),
                    (self.width() - header - px(8)) / self._bars_per_row,
                )
                left = header + col * width
                if i == 0:
                    self._signature(
                        p,
                        font=font,
                        x=px(16),
                        bottom=y + gap / 2,
                        gap=gap,
                    )
                self._draw_measure(
                    p,
                    measure=measure,
                    left=left,
                    width=width,
                    y=y,
                )
                end = left + width
                bar_ink = (
                    self.palette().highlight().color()
                    if self.bar_line
                    else QColor("black")
                )
                p.setPen(QPen(bar_ink, gap * 0.14))
                p.drawLine(
                    QPointF(end, y - 3.7 * gap),
                    QPointF(end, y + 0.7 * gap),
                )
                if self.bar_line == "Double barline":
                    end -= 0.5 * gap
                    p.drawLine(
                        QPointF(end, y - 3.7 * gap),
                        QPointF(end, y + 0.7 * gap),
                    )

    def _draw_measure(
        self,
        p: QPainter,
        *,
        measure: list[_Symbol],
        left: float,
        width: float,
        y: float,
    ) -> None:
        """Space symbols by time and beam eighth notes within a beat."""
        gap = px(10)
        font = current().font or "bravura"
        ink = QColor("black")
        accent = self.palette().highlight().color()
        scale = (width - px(14)) / self._bar_length
        for (_, eighths), group in groupby(
            measure,
            key=lambda s: (s.offset // self._beat_length, s.value == "eighth"),
        ):
            symbols = list(group)
            heads = [
                QPointF(left + px(10) + s.offset * scale, y) for s in symbols
            ]
            colors = [
                accent if s.onset == self.playback_column else ink
                for s in symbols
            ]
            beamed = eighths and len(heads) > 1
            if beamed:
                engraving.draw_beamed_eighths(
                    p,
                    font=font,
                    heads=heads,
                    colors=colors,
                    gap=gap,
                    middle=y,
                    ink=ink,
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
                    reach = RHYTHM_DURATIONS[symbol.value] * scale
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
        if value in REST_GLYPHS:
            path = engraving.notation_glyph(font, codepoint=REST_GLYPHS[value])
            p.save()
            p.translate(x, y - 1.4 * gap)
            p.scale(gap / 25, gap / 25)
            p.translate(-path.boundingRect().center())
            p.fillPath(path, color)
            p.restore()
            return
        engraving.draw_note(
            p,
            font=font,
            value=value.removeprefix("dotted-"),
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

    def _signature(
        self,
        p: QPainter,
        *,
        font: str,
        x: float,
        bottom: float,
        gap: float,
    ) -> None:
        """Stack both numbers at the start of the phrase."""
        for row, number in enumerate(self.meter):
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
            p.save()
            p.translate(x, bottom - (3 - row * 2) * gap)
            p.scale(gap / 25, gap / 25)
            center = line.boundingRect().center()
            p.fillPath(
                line.translated(-center.x(), -center.y()),
                QColor("black"),
            )
            p.restore()
