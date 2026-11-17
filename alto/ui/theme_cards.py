"""
The card of a theme in the settings.

A card is one theme: its name, three pictures of the window one above another that can be clicked (light, dark, and System,
which is cut through on a slant to show it is light or dark as the desktop is) and the squares of its colors.

Examples
--------
>>> card = ThemeCard("sage")
>>> sorted(card.thumbs)
['sage', 'sage_auto', 'sage_dark']
"""

from __future__ import annotations

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alto.ui.theme import (
    USER_PREFIX,
    CustomTheme,
    custom_theme,
    families,
    preview_colors,
    variant_key,
)

THUMB_W, THUMB_H = 116, 78  # the size of a clickable picture
SLANT = 10  # how far the cut through the System picture leans, in pixels
VERSIONS = (("light", "Light"), ("dark", "Dark"), ("system", "System"))  # the three pictures of a card, in order
LIGHT = dict(
    window="#efefef",
    panel="#ffffff",
    line="#c9c9c9",
    ink="#2a2a2a",
    faint="#b9b9b9",
    accent="#3b8ed0",
    tint="#c9dce8",
)  # the colors of the picture of the desktop's light theme
TIPS = {
    "light": "Always light.",
    "dark": "Always dark.",
    "system": "Light or dark as the desktop is.",
}  # what each picture says when hovered
DARK = dict(
    window="#2b2b2b",
    panel="#232323",
    line="#454545",
    ink="#ececec",
    faint="#5a5a5a",
    accent="#2f7fe0",
    tint="#22364f",
)  # and of its dark theme


def colors_of(key: str) -> dict[str, str]:
    """
    Give the colors of a theme's picture.

    Parameters
    ----------
    key : str
        A theme's key: "light", "dark", or a theme with colors of its own, light or dark.

    Returns
    -------
    dict of str to str
        The window, panel, outline, text, faint and chosen colors, and a tint for the chosen row.

    Examples
    --------
    >>> colors_of("dark")["window"], colors_of("studio")["window"]
    ('#2b2b2b', '#eceef1')
    """
    custom = custom_theme(key)
    if custom is not None:
        return preview_colors(custom)
    return DARK if key == "dark" else LIGHT


class ThemeThumb(QPushButton):
    """
    A small picture of the window in a theme, to click to choose the theme.

    Attributes
    ----------
    theme_key : str
        The key of the theme it chooses.
    colors : dict of str to str
        The colors it is drawn in.
    other : dict of str to str or None
        The colors of the dark half, for a picture that is cut through on a slant; None for a plain one.
    scale_by : float
        How many times bigger than the smallest size it is drawn.

    Examples
    --------
    >>> ThemeThumb("dark", colors=DARK).theme_key
    'dark'
    """

    def __init__(
        self,
        key: str,
        *,
        colors: dict[str, str],
        other: dict[str, str] | None = None,
        scale: float = 1.0,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the picture.

        Parameters
        ----------
        key : str
            The theme it chooses.
        colors : dict of str to str
            The colors of the picture, or of its light half.
        other : dict of str to str or None, default None
            The colors of its dark half, for a picture cut through on a slant. Keyword-only.
        scale : float, default 1.0
            How many times bigger than the smallest size to draw it. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> ThemeThumb("system", colors=LIGHT, other=DARK).width(), ThemeThumb("light", colors=LIGHT, scale=2.0).width()
        (116, 232)
        """
        super().__init__(parent)
        self.theme_key = key
        self.colors = colors
        self.other = other
        self.scale_by = scale
        self.setCheckable(True)
        self.setFixedSize(round(THUMB_W * scale), round(THUMB_H * scale))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the window, cut through on a slant if it has two halves, with an outline that is heavier when it is chosen.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request.

        Examples
        --------
        >>> ThemeThumb("light", colors=LIGHT).grab().isNull()
        False
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.scale(self.scale_by, self.scale_by)  # it is drawn at the smallest size, and enlarged
        area = QRectF(0, 0, THUMB_W, THUMB_H).adjusted(2, 2, -2, -2)
        clip = QPainterPath()
        clip.addRoundedRect(area, 7, 7)
        painter.setClipPath(clip)
        self._mock(painter, area=area, colors=self.colors)
        if self.other is not None:
            half = QPainterPath()
            half.addPolygon(
                QPolygonF(
                    [
                        QPointF(area.center().x() + SLANT, area.top()),
                        area.topRight(),
                        area.bottomRight(),
                        QPointF(area.center().x() - SLANT, area.bottom()),
                    ],
                ),
            )
            painter.setClipPath(half.intersected(clip))
            self._mock(painter, area=area, colors=self.other)
        painter.setClipping(False)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        chosen = self.isChecked()
        edge = self.palette().color(QPalette.ColorRole.Highlight) if chosen else QColor(128, 128, 128, 150)
        painter.setPen(QPen(edge, (3.0 if chosen else 1.0) / self.scale_by**0.5))
        painter.drawRoundedRect(area, 7, 7)
        painter.end()

    @staticmethod
    def _mock(
        painter: QPainter,
        *,
        area: QRectF,
        colors: dict[str, str],
    ) -> None:
        """
        Draw a small picture of a window: a list on the left, a staff with notes and a button on the right.

        Parameters
        ----------
        painter : QPainter
            The painter to draw with.
        area : QRectF
            Where to draw it. Keyword-only.
        colors : dict of str to str
            The colors to draw it in. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(120, 80, QImage.Format.Format_ARGB32)
        >>> brush = QPainter(image)
        >>> ThemeThumb._mock(brush, area=QRectF(0, 0, 120, 80), colors=LIGHT)
        >>> brush.end()
        True
        >>> image.pixelColor(2, 2).name()
        '#efefef'
        """
        painter.fillRect(area, QColor(colors["window"]))
        side = QRectF(area.left() + 6, area.top() + 6, 32, area.height() - 12)
        painter.setPen(QPen(QColor(colors["line"]), 1))
        painter.setBrush(QColor(colors["panel"]))
        painter.drawRoundedRect(side, 4, 4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors["tint"]))
        painter.drawRoundedRect(QRectF(side.left() + 3, side.top() + 5, side.width() - 6, 8), 3, 3)
        painter.setBrush(QColor(colors["faint"]))
        for number in range(3):
            line = QRectF(side.left() + 5, side.top() + 19 + number * 10, side.width() - 14 - number * 4, 3.5)
            painter.drawRoundedRect(line, 2, 2)
        card = QRectF(side.right() + 6, area.top() + 6, area.right() - side.right() - 12, area.height() - 12)
        painter.setPen(QPen(QColor(colors["line"]), 1))
        painter.setBrush(QColor(colors["panel"]))
        painter.drawRoundedRect(card, 4, 4)
        painter.setPen(QPen(QColor(colors["ink"]), 0.7))
        top = card.top() + 10
        for number in range(5):
            painter.drawLine(QPointF(card.left() + 5, top + number * 4.5), QPointF(card.right() - 5, top + number * 4.5))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors["ink"]))
        for x, row in ((14, 4), (27, 3), (40, 1), (53, 2)):
            painter.drawEllipse(QPointF(card.left() + x, top + row * 2.25), 2.8, 2.2)
        painter.setBrush(QColor(colors["accent"]))
        painter.drawRoundedRect(QRectF(card.left() + 5, card.bottom() - 15, 26, 9), 3.5, 3.5)


class ThemeCard(QFrame):
    """
    The card of one theme: its name, three clickable pictures one above another, and with each the squares of its colors.

    The pictures are Light, Dark and System. The System one is cut through on a slant, light on one side and dark on the other,
    because that version is light or dark as the desktop is.

    Attributes
    ----------
    family : str
        The key of the theme's family: "default" for System, Light and Dark.
    thumbs : dict of str to ThemeThumb
        The three pictures, by the key of the theme each chooses.
    change_button : QPushButton or None
        Opens the editor; only a theme the user made has one.
    chosen : Signal
        Emitted with the key of the theme when one of the pictures is clicked.
    edit_requested : Signal
        Emitted with the key of the theme when its Change colors button is pressed; only a theme the user made has one.

    Examples
    --------
    >>> card = ThemeCard("default")
    >>> list(card.thumbs)
    ['light', 'dark', 'system']
    """

    chosen = Signal(str)
    edit_requested = Signal(str)

    def __init__(
        self,
        family: str,
        *,
        scale: float = 1.0,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the card of a family.

        Parameters
        ----------
        family : str
            The key of the family: "default", "studio" or one of the generated themes.
        scale : float, default 1.0
            How many times bigger than the smallest size to draw the pictures. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> ThemeCard("studio").family
        'studio'
        """
        super().__init__(parent)
        self.family = family
        self.change_button: QPushButton | None = None
        label, note = next((label, note) for key, label, note in families() if key == family)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            12,
            10,
            12,
            10,
        )
        lay.setSpacing(8)
        name = QLabel(f"<b>{label}</b>")
        about = QLabel(note)
        about.setStyleSheet("color: gray; font-size: 9pt;")
        lay.addWidget(name)
        lay.addWidget(about)
        self.thumbs: dict[str, ThemeThumb] = {}
        self._captions: dict[str, QLabel] = {}
        for version, caption in VERSIONS:  # the three pictures are one above another, each with what it is beside it
            key = variant_key(family, version=version)
            colors = colors_of(variant_key(family, version="dark" if version == "dark" else "light"))
            other = colors_of(variant_key(family, version="dark")) if version == "system" else None
            thumb = ThemeThumb(key, colors=colors, other=other, scale=scale)
            thumb.clicked.connect(lambda _=False, k=key: self.chosen.emit(k))
            thumb.setAccessibleName(f"{label}, {caption}")
            thumb.setToolTip(TIPS[version])
            text = QLabel(caption)
            words = QVBoxLayout()
            words.addStretch(1)
            words.addWidget(text)
            custom = custom_theme(key)
            if custom is not None and version != "system":  # a theme's own colors, as squares, and written out as the page did
                words.addLayout(self._chips(custom))
                values = QLabel(f"window {custom.window}   accent {custom.accent}   ink {custom.ink}")
                values.setStyleSheet("color: gray; font-family: monospace; font-size: 9pt;")
                values.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                words.addWidget(values)
            else:  # nothing of its own to show: say what the picture is
                what = QLabel(TIPS[version])
                what.setStyleSheet("color: gray; font-size: 9pt;")
                words.addWidget(what)
            words.addStretch(1)
            row = QHBoxLayout()
            row.setSpacing(14)
            row.addWidget(thumb)
            row.addLayout(words, 1)
            lay.addLayout(row)
            self.thumbs[key] = thumb
            self._captions[key] = text
        if family.startswith(USER_PREFIX):
            change = self.change_button = QPushButton("Change colors…")
            change.setToolTip("Change the name and colors of this theme, or delete it")
            change.clicked.connect(lambda: self.edit_requested.emit(family))
            lay.addWidget(change, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch(1)  # a card that is shorter than its neighbor keeps its contents together at the top

    @staticmethod
    def _chips(theme: CustomTheme) -> QHBoxLayout:
        """
        Make the row of squares of one theme's colors.

        Parameters
        ----------
        theme : CustomTheme
            The theme, light or dark.

        Returns
        -------
        QHBoxLayout
            A square for the window, panel, outline, quiet text, text, accent and track colors.

        Examples
        --------
        >>> from alto.ui.theme import CUSTOM_THEMES
        >>> ThemeCard._chips(CUSTOM_THEMES[0]).count() > 7
        True
        """
        row = QHBoxLayout()
        row.setSpacing(3)
        for part in ("window", "panel", "line", "muted", "ink", "accent", "track"):
            chip = QFrame()
            chip.setFixedSize(18, 18)
            color = getattr(theme, part)
            chip.setToolTip(f"{part} {color}")
            chip.setStyleSheet(f"background: {color}; border: 1px solid rgba(128, 128, 128, 90); border-radius: 4px;")
            row.addWidget(chip)
        row.addStretch(1)
        return row

    def show_current(self, key: str) -> None:
        """
        Mark the picture of the theme that is in use, and outline the card that has it.

        Parameters
        ----------
        key : str
            The key of the theme in use.

        Examples
        --------
        >>> card = ThemeCard("sage")
        >>> card.show_current("sage_dark")
        >>> [k for k, picture in card.thumbs.items() if picture.isChecked()]
        ['sage_dark']
        """
        here = key in self.thumbs
        for thumb_key, thumb in self.thumbs.items():
            thumb.setChecked(thumb_key == key)
            font = self._captions[thumb_key].font()
            font.setBold(thumb_key == key)
            self._captions[thumb_key].setFont(font)
        self.setStyleSheet("ThemeCard { border: 2px solid palette(highlight); border-radius: 8px; }" if here else "")
