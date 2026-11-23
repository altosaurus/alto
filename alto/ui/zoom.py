"""
Zoom: make everything in Alto larger or smaller together.

The zoom is a percentage, 100 by default, that moves through a list of steps. It scales the application font, every pixel
and point length in the stylesheet, and the sizes the interface fixes in pixels, which are written with `px` here so that
they follow it. The notation that is drawn by hand takes its size from the same percentage. Pressing Ctrl and Plus or Ctrl and
Minus, or turning the mouse wheel with Ctrl held, moves one step, and Ctrl and 0 goes back to 100%. The choice is saved.

Examples
--------
>>> set_percent(100)
False
>>> px(20), px(0)
(20, 0)
>>> css("QLabel { font-size: 14pt; border: 1px solid; }")
'QLabel { font-size: 14pt; border: 1px solid; }'
"""

from __future__ import annotations

import re

from PySide6.QtCore import (
    QEvent,
    QObject,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QFont,
    QGuiApplication,
    QWheelEvent,
    QWindow,
)
from PySide6.QtWidgets import QApplication

from alto.ui.store import (
    int_value,
    store,
)

STEPS = (50, 67, 75, 80, 90, 100, 110, 125, 150, 175, 200, 250, 300)  # the zoom levels, as percentages
DEFAULT = 100
SETTING = "ui/zoom"
WHEEL_NOTCH = 120  # the wheel turns by this much for each click

_percent = DEFAULT
_base_font: QFont | None = None  # the application font at 100%, kept so that zooming does not compound
_LENGTH = re.compile(r"(?<![\w#.-])(\d+(?:\.\d+)?)(px|pt)\b")


class _Signals(QObject):
    """
    Tell the interface that the zoom changed.

    Attributes
    ----------
    changed : Signal
        Emitted with the new percentage after it changes.

    Examples
    --------
    >>> seen = []
    >>> _ = signals.changed.connect(seen.append)
    >>> _ = signals.changed.emit(110)
    >>> seen
    [110]
    """

    changed = Signal(int)


signals = _Signals()


def percent() -> int:
    """
    Give the zoom now in force.

    Returns
    -------
    int
        The percentage, one of `STEPS`.

    Examples
    --------
    >>> percent()
    100
    """
    return _percent


def factor() -> float:
    """
    Give the zoom as a multiplier.

    Returns
    -------
    float
        1.0 at 100%.

    Examples
    --------
    >>> factor()
    1.0
    """
    return _percent / 100


def px(value: float) -> int:
    """
    Scale a length in pixels by the zoom.

    Parameters
    ----------
    value : float
        The length at 100%.

    Returns
    -------
    int
        The length now, rounded, and never less than one pixel unless it was zero.

    Examples
    --------
    >>> px(20), px(0), px(-4)
    (20, 0, -4)
    """
    if not value:
        return 0
    scaled = round(value * factor())
    return scaled or (1 if value > 0 else -1)


def css(text: str) -> str:
    """
    Scale every pixel and point length in a stylesheet by the zoom.

    Parameters
    ----------
    text : str
        The stylesheet.

    Returns
    -------
    str
        The same stylesheet with each length such as ``12px`` or ``14pt`` multiplied. A length of zero stays zero.

    Examples
    --------
    >>> css("QLabel { padding: 8px 12px; font-size: 14pt; margin: 0px; }")
    'QLabel { padding: 8px 12px; font-size: 14pt; margin: 0px; }'
    """
    if _percent == DEFAULT:
        return text

    def scale(match: re.Match[str]) -> str:
        """
        Scale one length.

        Parameters
        ----------
        match : re.Match
            A number and its unit.

        Returns
        -------
        str
            The scaled length.
        """
        number, unit = float(match.group(1)), match.group(2)
        scaled = number * factor()
        if unit == "px":
            return f"{px(number)}px"
        return f"{scaled:g}pt" if scaled else "0pt"

    return _LENGTH.sub(scale, text)


def _nearest(value: int) -> int:
    """
    Find the step nearest to a percentage.

    Parameters
    ----------
    value : int
        Any percentage.

    Returns
    -------
    int
        The closest of `STEPS`.

    Examples
    --------
    >>> _nearest(103), _nearest(1), _nearest(1000)
    (100, 50, 300)
    """
    return min(STEPS, key=lambda step: abs(step - value))


def apply_font() -> None:
    """
    Make the application font as large as the zoom says, from the size it had at 100%.

    Examples
    --------
    >>> apply_font()
    """
    global _base_font
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return
    if _base_font is None:
        _base_font = QFont(app.font())
    font = QFont(_base_font)
    if _base_font.pointSizeF() > 0:
        font.setPointSizeF(_base_font.pointSizeF() * factor())
    elif _base_font.pixelSize() > 0:
        font.setPixelSize(px(_base_font.pixelSize()))
    app.setFont(font)


def set_percent(value: int) -> bool:
    """
    Zoom to the step nearest a percentage, save it and say so.

    Parameters
    ----------
    value : int
        The percentage wanted.

    Returns
    -------
    bool
        True if the zoom changed, False if it was already there.

    Examples
    --------
    >>> set_percent(125)
    True
    >>> percent(), factor()
    (125, 1.25)
    >>> set_percent(125)
    False
    >>> set_percent(100)
    True
    """
    global _percent
    chosen = _nearest(value)
    if chosen == _percent:
        return False
    _percent = chosen
    apply_font()
    store().setValue(SETTING, chosen)
    signals.changed.emit(chosen)
    return True


def step(direction: int) -> bool:
    """
    Zoom in or out by one step.

    Parameters
    ----------
    direction : int
        Positive to zoom in, negative to zoom out.

    Returns
    -------
    bool
        True if the zoom changed, False at the largest or smallest step.

    Examples
    --------
    >>> step(1), percent()
    (True, 110)
    >>> step(-1), percent()
    (True, 100)
    >>> while step(-1):
    ...     pass
    >>> percent(), step(-1)
    (50, False)
    >>> reset(), percent()
    (True, 100)
    """
    index = STEPS.index(_percent) + (1 if direction > 0 else -1)
    if not 0 <= index < len(STEPS):
        return False
    return set_percent(STEPS[index])


def reset() -> bool:
    """
    Go back to 100%.

    Returns
    -------
    bool
        True if the zoom changed.

    Examples
    --------
    >>> reset()
    False
    """
    return set_percent(DEFAULT)


def load() -> None:
    """
    Take the saved zoom into force, without announcing it, ignoring anything that is not a step.

    Examples
    --------
    >>> store().setValue(SETTING, 150)
    >>> load()
    >>> percent()
    150
    >>> store().setValue(SETTING, "wide")
    >>> load()
    >>> percent()
    100
    """
    global _percent
    try:
        saved = int_value(store(), key=SETTING, default=DEFAULT)
    except (TypeError, ValueError):
        saved = DEFAULT
    _percent = saved if saved in STEPS else DEFAULT
    apply_font()


class WheelZoom(QObject):
    """
    Zoom when the mouse wheel turns with Ctrl held, wherever the pointer is.

    A touchpad that sends small steps is added up, so that a whole notch is needed to move one step.

    Examples
    --------
    >>> WheelZoom().eventFilter(QObject(), QEvent(QEvent.Type.None_))
    False
    """

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Start with no wheel turned.

        Parameters
        ----------
        parent : QObject or None, default None
            The object that owns the filter.

        Examples
        --------
        >>> WheelZoom()._turned
        0
        """
        super().__init__(parent)
        self._turned = 0

    def follow(self, app: QGuiApplication) -> None:
        """
        Watch the window that has the focus, and each window that gains it later, such as a dialog that opens.

        The filter goes on the windows, not on the application. A window is handed each wheel turn before the widget under the
        pointer is, so a turn anywhere in it is seen, while the many events that pass between the widgets inside it are not:
        a filter on the application runs for every one of those, which made building a page half as slow again.

        Parameters
        ----------
        app : QGuiApplication
            The application whose windows to watch.

        Examples
        --------
        >>> handler = WheelZoom()
        >>> handler.follow(app)
        """
        app.focusWindowChanged.connect(self.watch)
        self.watch(app.focusWindow())

    def watch(self, window: QWindow | None) -> None:
        """
        Zoom when the wheel turns with Ctrl held over a window.

        Parameters
        ----------
        window : QWindow or None
            The window. None, which is what Qt passes when no window has the focus, does nothing.

        Examples
        --------
        >>> from PySide6.QtWidgets import QWidget
        >>> widget = QWidget()
        >>> widget.show()
        >>> handler = WheelZoom()
        >>> handler.watch(widget.windowHandle())
        >>> handler.watch(None)
        """
        if window is not None:
            window.removeEventFilter(self)  # so a window that gains the focus again is not watched twice
            window.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802, PLR0917 (Qt passes both arguments positionally)
        """
        Take a wheel event with Ctrl held as a zoom, and let every other event through.

        Parameters
        ----------
        watched : QObject
            The object the event is for.
        event : QEvent
            The event.

        Returns
        -------
        bool
            True when the event was a zoom, so that nothing under the pointer scrolls.

        Examples
        --------
        >>> WheelZoom().eventFilter(QObject(), QEvent(QEvent.Type.None_))
        False
        """
        del watched
        if event.type() != QEvent.Type.Wheel or not isinstance(event, QWheelEvent):
            return False
        if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._turned = 0
            return False
        delta = event.angleDelta().y()
        if not delta:
            # Some touchpads supply only pixel deltas. Forty pixels gives one zoom step.
            delta = event.pixelDelta().y() * (WHEEL_NOTCH // 40)
        self._turned += delta
        notches = int(self._turned / WHEEL_NOTCH)
        if notches:
            self._turned -= notches * WHEEL_NOTCH
            index = max(0, min(len(STEPS) - 1, STEPS.index(_percent) + notches))
            set_percent(STEPS[index])
        return True
