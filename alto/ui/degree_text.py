"""
Draw scale-degree carets above their digits without relying on
font-specific combining accents.

Examples
--------
>>> button = DegreeButton("♭3̂")
>>> button.text()
'♭3̂'
"""

from __future__ import annotations

from html import escape
from math import ceil

from PySide6.QtCore import (
    QBuffer,
    QIODevice,
    QPointF,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QFontMetricsF,
    QImage,
    QImageWriter,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QPushButton,
    QStyle,
    QStyleOptionButton,
    QToolTip,
)


def draw_degree_text(
    painter: QPainter,
    *,
    rect: QRectF,
    text: str,
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
) -> None:
    """
    Draw text with each combining circumflex centered above its
    preceding digit.

    Parameters
    ----------
    painter : QPainter
        The active painter, with the desired font and color.
    rect : QRectF
        The rectangle in which to align the text. Keyword-only.
    text : str
        The text, retaining combining circumflexes for copying and
        accessibility. Keyword-only.
    alignment : Qt.AlignmentFlag, default AlignCenter
        Horizontal and vertical alignment. Keyword-only.

    Examples
    --------
    >>> from PySide6.QtGui import QPixmap
    >>> pixmap = QPixmap(100, 40)
    >>> painter_ = QPainter(pixmap)
    >>> draw_degree_text(
    ...     painter_,
    ...     rect=QRectF(0, 0, 100, 40),
    ...     text="3̂",
    ... )
    >>> painter_.end()
    True
    """
    if "̂" not in text:
        painter.drawText(rect, alignment, text)
        return
    metrics = QFontMetricsF(painter.font())
    plain = text.replace("̂", "")
    width = metrics.horizontalAdvance(plain)
    height = metrics.height()
    x = rect.left()
    if alignment & Qt.AlignmentFlag.AlignHCenter:
        x += (rect.width() - width) / 2
    elif alignment & Qt.AlignmentFlag.AlignRight:
        x += rect.width() - width
    y = rect.top() + metrics.ascent()
    if alignment & Qt.AlignmentFlag.AlignVCenter:
        y += (rect.height() - height) / 2
    elif alignment & Qt.AlignmentFlag.AlignBottom:
        y += rect.height() - height
    painter.drawText(QPointF(x, y), plain)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(painter.pen())
    pen.setWidthF(max(0.6, metrics.capHeight() / 12))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    prefix = ""
    for char in text:
        if char != "̂":
            prefix += char
            continue
        if not prefix or prefix[-1] not in "1234567":
            continue
        ink = metrics.tightBoundingRect(prefix[-1])
        center = x + metrics.horizontalAdvance(prefix[:-1]) + ink.center().x()
        bottom = y + ink.top() - max(1.0, metrics.capHeight() * 0.12)
        half_width = max(1.2, ink.width() * 0.4)
        path = QPainterPath(QPointF(center - half_width, bottom))
        path.lineTo(center, bottom - max(1.0, metrics.capHeight() * 0.2))
        path.lineTo(center + half_width, bottom)
        painter.drawPath(path)
    painter.restore()


def degree_tooltip(text: str) -> str:
    """
    Render caret examples as an inline image for Qt's rich-text tooltip.

    Parameters
    ----------
    text : str
        The tooltip text. Text without combining carets is returned
        unchanged.

    Returns
    -------
    str
        Plain text or HTML containing the explicitly centered carets.

    Examples
    --------
    >>> degree_tooltip("Letters")
    'Letters'
    >>> "data:image/png;base64," in degree_tooltip(
    ...     "Caret (1̂ 2̂ 3̂)"
    ... )
    True
    """
    if "̂" not in text:
        return text
    font = QToolTip.font()
    metrics = QFontMetricsF(font)
    width = ceil(metrics.horizontalAdvance(text.replace("̂", ""))) + 8
    height = ceil(metrics.height()) + 8
    image = QImage(
        width * 2,
        height * 2,
        QImage.Format.Format_ARGB32_Premultiplied,
    )
    image.setDevicePixelRatio(2)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setFont(font)
    painter.setPen(QToolTip.palette().color(QPalette.ColorRole.ToolTipText))
    draw_degree_text(painter, rect=QRectF(0, 0, width, height), text=text)
    painter.end()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    QImageWriter(buffer, b"PNG").write(image)
    encoded = bytes(buffer.data().toBase64().data()).decode("ascii")
    return (
        '<img src="data:image/png;base64,'
        f"{encoded}"
        '" width="'
        f"{width}"
        '" height="'
        f"{height}"
        '" alt="'
        f"{escape(text, quote=True)}"
        '">'
    )


class DegreeButton(QPushButton):
    """
    An answer button that draws scale-degree carets directly above the
    digits.

    Examples
    --------
    >>> DegreeButton("2̂").text()
    '2̂'
    """

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Keep the native button appearance and position degree accents
        explicitly.

        Parameters
        ----------
        event : QPaintEvent
            The paint request.

        Examples
        --------
        >>> DegreeButton("2̂").grab().isNull()
        False
        """
        if "̂" not in self.text():
            super().paintEvent(event)
            return
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ""
        painter = QPainter(self)
        self.style().drawControl(
            QStyle.ControlElement.CE_PushButton,
            option,
            painter,
            self,
        )
        painter.setPen(self.palette().color(QPalette.ColorRole.ButtonText))
        rect = self.style().subElementRect(
            QStyle.SubElement.SE_PushButtonContents,
            option,
            self,
        )
        draw_degree_text(painter, rect=QRectF(rect), text=self.text())


class DegreeCheckBox(QCheckBox):
    """
    Draw the scale degree caret centered above the checkbox label's
    digit.
    """

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the native checkbox and use the shared scale degree
        renderer for its label.
        """
        if "̂" not in self.text():
            super().paintEvent(event)
            return
        option = QStyleOptionButton()
        self.initStyleOption(option)
        style = self.style()
        rect = style.subElementRect(
            QStyle.SubElement.SE_CheckBoxContents,
            option,
            self,
        )
        option.text = ""
        painter = QPainter(self)
        style.drawControl(
            QStyle.ControlElement.CE_CheckBox,
            option,
            painter,
            self,
        )
        painter.setPen(self.palette().color(QPalette.ColorRole.WindowText))
        draw_degree_text(
            painter,
            rect=QRectF(rect),
            text=self.text(),
            alignment=Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
        )


class DegreeLabel(QLabel):
    """
    A plain-text label with explicitly positioned scale-degree carets.

    Examples
    --------
    >>> DegreeLabel("Note to place: 2̂ / 4").text()
    'Note to place: 2̂ / 4'
    """

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint degree labels with carets centered above their numbers.

        Parameters
        ----------
        event : QPaintEvent
            The paint request.

        Examples
        --------
        >>> DegreeLabel("2̂").grab().isNull()
        False
        """
        if "̂" not in self.text():
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setPen(self.palette().color(QPalette.ColorRole.WindowText))
        draw_degree_text(
            painter,
            rect=QRectF(self.contentsRect()),
            text=self.text(),
            alignment=self.alignment(),
        )
