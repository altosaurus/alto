"""
Paint the engraved score and locate symbols from a pixel map made from
the same SVG.
"""

from __future__ import annotations

import array
import re
from functools import lru_cache

from PySide6.QtCore import QByteArray, QPoint, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

from alto.notation_excerpts import Excerpt


class ScoreExcerpt:
    """
    The score artwork and its per-pixel index into the excerpt's target
    list.
    """

    def __init__(self, excerpt: Excerpt) -> None:
        """Read the SVG and its aligned 16-bit hit map."""
        self.excerpt = excerpt

        image = QImage(str(excerpt.folder / "hits.png")).convertToFormat(
            QImage.Format.Format_Grayscale16,
        )
        bits, stride = bytes(image.constBits()), image.bytesPerLine()
        self.hits: list[
            array.array[int]
            # one row per line of pixels: 0 for paper, else 1 + the
            # target's
            # index
        ] = []
        for y in range(image.height()):
            row = array.array("H")
            row.frombytes(
                bits[y * stride : y * stride + 2 * image.width()],
            )  # both use the computer's byte order
            self.hits.append(row)

    def music_rect(self, paper: QRectF) -> QRectF:
        """
        Fit the music inside its paper, leaving one line for the source
        credit.

        Returns
        -------
        QRectF
            Destination rectangle shared by display and pointer hit
            testing.
        """
        area = paper.adjusted(10, 8, -10, -27)
        height, width = len(self.hits), len(self.hits[0]) if self.hits else 0
        scale = max(0.0, min(area.width() / width, area.height() / height))
        rect = QRectF(0, 0, width * scale, height * scale)
        rect.moveCenter(area.center())
        return rect

    def component_at(
        self,
        point: QPoint,
        *,
        rect: QRectF,
    ) -> tuple[str, int] | None:
        """
        Look up the visible ink under a point in the scaled engraving.

        Returns
        -------
        tuple or None
            Term and marker index, or None on blank paper.
        """
        if rect.contains(point) and rect.width() and rect.height():
            height, width = (
                len(self.hits),
                len(self.hits[0]) if self.hits else 0,
            )
            x = min(
                width - 1,
                int((point.x() - rect.left()) * width / rect.width()),
            )
            y = min(
                height - 1,
                int((point.y() - rect.top()) * height / rect.height()),
            )
            index = self.hits[y][x] - 1
            if index >= 0:
                return self.excerpt.targets[index], index
        return None

    def paint(
        self,
        painter: QPainter,
        *,
        paper: QRectF,
        index: int | None,
        color: QColor,
    ) -> None:
        """
        Draw the excerpt and its attribution at the current paper size.
        """
        rect = self.music_rect(paper)
        _renderer(self.excerpt, index=index, color=color.name()).render(
            painter,
            rect,
        )
        credit = QRectF(
            paper.left() + 6,
            rect.bottom() + 2,
            paper.width() - 12,
            22,
        )
        painter.setPen(QColor("#494949"))
        font = painter.font()
        font.setStyleStrategy(QFont.StyleStrategy.NoSubpixelAntialias)
        painter.setFont(font)
        text = painter.fontMetrics().elidedText(
            self.excerpt.credit,
            Qt.TextElideMode.ElideRight,
            int(credit.width()),
        )
        painter.drawText(credit, Qt.AlignmentFlag.AlignCenter, text)


@lru_cache(maxsize=12)
def _renderer(
    excerpt: Excerpt,
    *,
    index: int | None,
    color: str,
) -> QSvgRenderer:
    """
    Tint a component in place, preserving the original shapes and draw
    order.

    Returns
    -------
    QSvgRenderer
        Engraving with the given marker in the requested ink.
    """
    data = _source(excerpt)
    if index is not None:
        marker = f'id="mark-{index}"'.encode()
        start = data.index(marker)
        end = data.index(b"</g>", start)
        group = data[start:end].replace(
            marker,
            marker + f' fill="{color}" color="{color}"'.encode(),
            1,
        )
        if excerpt.targets[index] in {"Staff line", "Ledger line", "Stem"}:
            # Keep a hairline legible when the full piano system fits a
            # narrow window.
            group = re.sub(
                rb'stroke-width="[0-9]+"',
                b'stroke-width="36"',
                group,
            )
        data = data[:start] + group + data[end:]
    return QSvgRenderer(QByteArray(data))


@lru_cache(maxsize=4)
def _source(excerpt: Excerpt) -> bytes:
    """
    Read the versioned SVG.

    Returns
    -------
    bytes
        Engraving with black ink for all markers.
    """
    return (excerpt.folder / "score.svg").read_bytes()


@lru_cache(maxsize=4)
def score_artwork(excerpt: Excerpt) -> ScoreExcerpt:
    """
    Load the music and hit map once per recently viewed passage.

    Returns
    -------
    ScoreExcerpt
        The passage artwork.
    """
    return ScoreExcerpt(excerpt)
