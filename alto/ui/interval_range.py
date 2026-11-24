"""
A two-handle slider for selecting interval distances without changing
the keyboard range.

Examples
--------
>>> slider = IntervalRangeSlider()
>>> slider.set_range(3, high=12, maximum=24)
>>> slider.low, slider.high
(3, 12)
"""

from __future__ import annotations

from PySide6.QtCore import (
    QPointF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
)

from alto.ui.zoom import px


class IntervalRangeSlider(QWidget):
    """
    A draggable interval range with keyboard controls for either
    endpoint.

    Attributes
    ----------
    edited : Signal
        Emits the selected lower and upper distances in half steps.
    low, high : int
        The selected distances, inclusive.
    minimum, maximum : int
        The smallest and largest available interval distances.
    active : bool
        Whether the current selection contains any intervals.

    Examples
    --------
    >>> slider = IntervalRangeSlider()
    >>> slider.low, slider.high, slider.maximum
    (1, 12, 24)
    """

    edited = Signal(int, int)
    PADDING = 12.0

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create the slider with a one-octave selection.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the slider.

        Examples
        --------
        >>> IntervalRangeSlider().height()
        36
        """
        super().__init__(parent)
        self.minimum = 1
        self.low, self.high, self.maximum = 1, 12, 24
        self.active = True
        self._endpoint = "low"
        self._dragging = False
        self.setFixedHeight(px(36))
        self.setMinimumWidth(px(120))
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Interval range")
        self.setToolTip(
            (
                "Drag either handle. Left and Right adjust it; Down "
                "selects the lower handle and Up the upper handle."
            ),
        )

    def set_range(
        self,
        low: int,
        *,
        high: int,
        maximum: int,
        minimum: int = 1,
        active: bool = True,
    ) -> None:
        """
        Synchronize the slider without emitting an edit.

        Parameters
        ----------
        low : int
            The lowest selected interval distance.
        high : int
            The highest selected interval distance. Keyword-only.
        maximum : int
            The largest available distance. Keyword-only.
        minimum : int, default 1
            The smallest available distance. Keyword-only.
        active : bool, default True
            Whether any intervals are selected. Keyword-only.

        Examples
        --------
        >>> slider = IntervalRangeSlider()
        >>> slider.set_range(3, high=7, maximum=12)
        >>> slider.low, slider.high
        (3, 7)
        """
        self.minimum = minimum
        self.maximum = max(minimum, maximum)
        self.low = min(max(minimum, low), self.maximum)
        self.high = min(max(self.low, high), self.maximum)
        self.active = active
        self.setAccessibleDescription(
            f"Intervals {self.low} through {self.high}"
            if active
            else "No intervals selected",
        )
        self.update()

    def move_endpoint(self, which: str, *, delta: int) -> None:
        """
        Move an endpoint by a number of half-step distances.

        Parameters
        ----------
        which : str
            The endpoint, "low" or "high".
        delta : int
            The number of interval distances to move. Keyword-only.

        Examples
        --------
        >>> slider = IntervalRangeSlider()
        >>> slider.move_endpoint("low", delta=2)
        >>> slider.low
        3
        """
        self._endpoint = which
        value = (self.low if which == "low" else self.high) + delta
        self._commit(value)

    def _position(self, value: int) -> float:
        """
        Convert an interval distance to a horizontal position.

        Parameters
        ----------
        value : int
            The interval distance.

        Returns
        -------
        float
            The handle position in pixels.

        Examples
        --------
        >>> IntervalRangeSlider()._position(1)
        12.0
        """
        fraction = (value - self.minimum) / max(1, self.maximum - self.minimum)
        if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            fraction = 1.0 - fraction
        return self.PADDING + fraction * max(
            1.0,
            self.width() - 2 * self.PADDING,
        )

    def _commit(self, value: int) -> None:
        """
        Clamp an endpoint and emit one edit when the selection changes.

        Parameters
        ----------
        value : int
            The proposed endpoint distance.

        Examples
        --------
        >>> slider = IntervalRangeSlider()
        >>> slider._commit(99)
        >>> slider.low
        12
        """
        value = min(max(self.minimum, value), self.maximum)
        before = self.low, self.high, self.active
        if not self.active:
            self.low = self.high = value
        elif self._endpoint == "low":
            self.low = min(value, self.high)
        else:
            self.high = max(value, self.low)
        self.active = True
        if before != (self.low, self.high, self.active):
            self.edited.emit(self.low, self.high)
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw the track, selected span, and both handles.

        Parameters
        ----------
        event : QPaintEvent
            The repaint request.

        Examples
        --------
        >>> IntervalRangeSlider().grab().isNull()
        False
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        y = self.height() / 2
        painter.setPen(
            QPen(
                self.palette().color(QPalette.ColorRole.Mid),
                4,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            ),
        )
        painter.drawLine(
            QPointF(self.PADDING, y),
            QPointF(self.width() - self.PADDING, y),
        )
        color = self.palette().color(
            QPalette.ColorRole.Highlight
            if self.active
            else QPalette.ColorRole.Mid,
        )
        painter.setPen(
            QPen(color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap),
        )
        if self.active:
            painter.drawLine(
                QPointF(self._position(self.low), y),
                QPointF(self._position(self.high), y),
            )
        endpoints = (
            ("high", "low") if self._endpoint == "low" else ("low", "high")
        )
        for endpoint in endpoints:
            value = self.low if endpoint == "low" else self.high
            border = (
                self.palette().color(QPalette.ColorRole.Text)
                if self.hasFocus() and endpoint == self._endpoint
                else color
            )
            painter.setPen(QPen(border, 2))
            painter.setBrush(self.palette().color(QPalette.ColorRole.Window))
            painter.drawEllipse(QPointF(self._position(value), y), 7, 7)
        super().paintEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Choose the nearest handle and start dragging it.

        Parameters
        ----------
        event : QMouseEvent
            The mouse press.

        Examples
        --------
        >>> IntervalRangeSlider()._dragging
        False
        """
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        x = event.position().x()
        low, high = self._position(self.low), self._position(self.high)
        if low == high:
            self._endpoint = "high" if x >= high else "low"
        else:
            self._endpoint = "low" if abs(x - low) < abs(x - high) else "high"
        self._dragging = True
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.mouseMoveEvent(event)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Move the active handle while dragging.

        Parameters
        ----------
        event : QMouseEvent
            The pointer movement.

        Examples
        --------
        >>> IntervalRangeSlider().maximum
        24
        """
        if not self._dragging:
            super().mouseMoveEvent(event)
            return
        fraction = (event.position().x() - self.PADDING) / max(
            1.0,
            self.width() - 2 * self.PADDING,
        )
        if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            fraction = 1.0 - fraction
        self._commit(
            self.minimum + round(fraction * (self.maximum - self.minimum)),
        )
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Finish dragging a handle.

        Parameters
        ----------
        event : QMouseEvent
            The mouse release.

        Examples
        --------
        >>> IntervalRangeSlider()._dragging
        False
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Adjust the active endpoint with arrow keys, Home, or End.

        Parameters
        ----------
        event : QKeyEvent
            The keyboard input. Up selects the upper handle and Down the
            lower handle.

        Examples
        --------
        >>> (
        ...     IntervalRangeSlider().focusPolicy()
        ...     == Qt.FocusPolicy.StrongFocus
        ... )
        True
        """
        key = event.key()
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            self._endpoint = "high" if key == Qt.Key.Key_Up else "low"
            self.update()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            delta = 1 if key == Qt.Key.Key_Right else -1
            if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
                delta = -delta
            self.move_endpoint(self._endpoint, delta=delta)
        elif key in (Qt.Key.Key_Home, Qt.Key.Key_End):
            self._commit(
                self.minimum if key == Qt.Key.Key_Home else self.maximum,
            )
        else:
            super().keyPressEvent(event)
            return
        event.accept()
