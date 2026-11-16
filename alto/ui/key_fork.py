"""
The fork: a picker for a key signature, shaped like a tuning fork lying on its side.

The stem on the left ends in a natural sign (no sharps or flats, C major). At the right the stem opens into two tines:
the top one has the sharps, 1 to 7, and the bottom one the flats, 1 to 7. A circle marks the chosen signature. Click a
number to choose it, drag the circle along the fork, or turn the mouse wheel to move it.

Examples
--------
>>> fork = KeyFork()
>>> fork.set_value(-3)
>>> fork.value
-3
"""

from __future__ import annotations

import math

from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QEvent,
    QPointF,
    QRectF,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
)

from alto.ui.colors import blend

MAX_ACCIDENTALS = 7  # a signature has at most seven sharps or flats
FORK_W, FORK_H = 440, 140
STEM_X, JOINT_X, FIRST_X, STEP = (
    30.0,
    112.0,
    150.0,
    38.0,
)  # the natural sign, where the U meets the tines, the first number, the gap
TOP_Y, MID_Y, BOTTOM_Y = 32.0, 70.0, 108.0  # the sharp tine, the stem, the flat tine
BEND_R = MID_Y - TOP_Y  # the U at the foot of the tines is a half circle of this radius, with the stem at its apex
APEX_X = JOINT_X - BEND_R  # where the stem meets the U
BEND_STEPS = 10  # how many pieces a quarter of the U is cut into, for the circle to travel along
LINE_W = 3.0  # the width of the fork's metal
NODE_R, MARKER_R = 11.0, 15.0  # the radius of a number, and of the circle that marks the chosen one
WHEEL_NOTCH = 120  # the angle delta of one notch of a mouse wheel
SLIDE_MS = 170  # how long the circle takes to move to a new number


def node_position(value: int) -> QPointF:
    """
    Return where a signature sits on the fork.

    Parameters
    ----------
    value : int
        The signature: that many sharps if positive (top tine), flats if negative (bottom tine), 0 for the stem's end.

    Returns
    -------
    QPointF
        The centre of its number, in the widget's coordinates.

    Examples
    --------
    >>> node_position(0).x() < node_position(1).x() < node_position(2).x()
    True
    >>> node_position(3).y() < node_position(0).y() < node_position(-3).y()
    True
    """
    if value == 0:
        return QPointF(STEM_X, MID_Y)
    return QPointF(FIRST_X + STEP * (abs(value) - 1), TOP_Y if value > 0 else BOTTOM_Y)


def route(value: int) -> list[QPointF]:
    """
    Return the way along the fork from the end of the stem to a signature.

    Parameters
    ----------
    value : int
        The signature, as for `node_position`.

    Returns
    -------
    list of QPointF
        The points to pass through: the stem's end, round the bend of the U to the tine and then each number up to the one asked.

    Examples
    --------
    >>> len(route(0)), len(route(2)) > len(route(1)) > len(route(0))
    (1, True)
    >>> route(-1)[-1] == node_position(-1)
    True
    >>> round(route(3)[1].x()) == round(APEX_X)  # it leaves the stem at the apex of the U
    True
    """
    points = [node_position(0)]
    if value == 0:
        return points
    sign = 1 if value > 0 else -1
    for i in range(BEND_STEPS + 1):  # round the U, from the apex to the start of the tine
        angle = math.pi / 2 * i / BEND_STEPS
        points.append(QPointF(JOINT_X - BEND_R * math.cos(angle), MID_Y - sign * BEND_R * math.sin(angle)))
    points += [node_position(sign * k) for k in range(1, abs(value) + 1)]
    return points


def path_between(a: int, *, b: int) -> list[QPointF]:
    """
    Return the way along the fork from one signature to another.

    The circle goes back along the tine it is on, round the U and out along the other, never across the gap between the tines.

    Parameters
    ----------
    a : int
        The signature to start from.
    b : int
        The signature to end at. Keyword-only.

    Returns
    -------
    list of QPointF
        The points to pass through, from `a` to `b`.

    Examples
    --------
    >>> path_between(2, b=2) == [node_position(2)]
    True
    >>> path_between(1, b=-1)[0] == node_position(1) and path_between(1, b=-1)[-1] == node_position(-1)
    True
    >>> any(abs(p.x() - APEX_X) < 1e-9 for p in path_between(1, b=-1))  # it goes round the U, through its apex
    True
    """
    from_a, to_b = route(a), route(b)
    shared = 0
    while shared < min(len(from_a), len(to_b)) and from_a[shared] == to_b[shared]:
        shared += 1
    return [*reversed(from_a[shared - 1 :]), *to_b[shared:]]


def point_along(points: list[QPointF], *, t: float) -> QPointF:
    """
    Return the point a fraction of the way along a path made of short straight pieces.

    Parameters
    ----------
    points : list of QPointF
        The corners of the path; at least one.
    t : float
        How far along, from 0 (the first point) to 1 (the last). Keyword-only.

    Returns
    -------
    QPointF
        The point that far along.

    Examples
    --------
    >>> point_along([QPointF(0, 0), QPointF(10, 0), QPointF(10, 10)], t=0.75).toTuple()
    (10.0, 5.0)
    >>> point_along([QPointF(0, 0), QPointF(3, 4)], t=0.5).toTuple()  # slanting pieces are measured along their length
    (1.5, 2.0)
    """
    pieces = list(zip(points, points[1:], strict=False))
    lengths = [math.hypot(q.x() - p.x(), q.y() - p.y()) for p, q in pieces]
    remaining = t * sum(lengths)
    for (p, q), length in zip(pieces, lengths, strict=True):
        if remaining <= length and length > 0:
            return p + (q - p) * (remaining / length)
        remaining -= length
    return points[-1]


def nearest_on_fork(point: QPointF) -> QPointF:
    """
    Return the point on the fork's line that is closest to a point.

    Parameters
    ----------
    point : QPointF
        Any position in the widget, such as the mouse while the circle is dragged.

    Returns
    -------
    QPointF
        The closest point on the way from the last sharp, round the U, to the last flat.

    Examples
    --------
    >>> nearest_on_fork(QPointF(node_position(2).x(), 0)) == node_position(2)  # straight above the number
    True
    >>> nearest_on_fork(QPointF(-50, node_position(0).y())) == node_position(0)  # past the end of the stem
    True
    """
    line = [*reversed(route(MAX_ACCIDENTALS)), *route(-MAX_ACCIDENTALS)[1:]]
    best, best_distance = line[0], math.inf
    for a, b in zip(line, line[1:], strict=False):
        edge = b - a
        length_squared = edge.x() ** 2 + edge.y() ** 2
        if length_squared == 0:
            continue
        along = max(0.0, min(1.0, ((point.x() - a.x()) * edge.x() + (point.y() - a.y()) * edge.y()) / length_squared))
        candidate = a + edge * along
        distance = (candidate - point).manhattanLength()
        if distance < best_distance:
            best, best_distance = candidate, distance
    return best


def fork_path() -> QPainterPath:
    """
    Return the outline of the fork: the stem, a half circle for the U, and the two tines.

    Returns
    -------
    QPainterPath
        One smooth line, drawn from the end of the stem.

    Examples
    --------
    >>> outline = fork_path()
    >>> outline.boundingRect().left() == STEM_X and outline.boundingRect().top() == TOP_Y
    True
    """
    last_x = FIRST_X + STEP * (MAX_ACCIDENTALS - 1) + STEP / 2  # the tines run a little past the last number
    path = QPainterPath(QPointF(STEM_X, MID_Y))
    path.lineTo(APEX_X, MID_Y)  # the stem
    path.arcTo(QRectF(JOINT_X - BEND_R, TOP_Y, 2 * BEND_R, 2 * BEND_R), 180.0, -90.0)  # up to the sharp tine
    path.lineTo(last_x, TOP_Y)
    path.moveTo(APEX_X, MID_Y)
    path.arcTo(QRectF(JOINT_X - BEND_R, TOP_Y, 2 * BEND_R, 2 * BEND_R), 180.0, 90.0)  # down to the flat tine
    path.lineTo(last_x, BOTTOM_Y)
    return path


def draw_natural(
    p: QPainter,
    *,
    center: QPointF,
    height: float,
    color: QColor,
) -> None:
    """
    Draw a natural sign: two upright lines joined by two slanting bars.

    Parameters
    ----------
    p : QPainter
        The painter to draw with.
    center : QPointF
        The middle of the sign. Keyword-only.
    height : float
        How tall it is, in pixels. Keyword-only.
    color : QColor
        The colour of the lines. Keyword-only.

    Examples
    --------
    >>> from PySide6.QtGui import QPixmap
    >>> canvas = QPixmap(20, 20)
    >>> painter = QPainter(canvas)
    >>> draw_natural(painter, center=QPointF(10, 10), height=14, color=QColor("black"))
    >>> _ = painter.end()
    """
    p.setPen(QPen(color, max(1.4, height / 9), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    x, y, h, w = center.x(), center.y(), height / 2, height / 5
    p.drawLine(QPointF(x - w, y - h), QPointF(x - w, y + h * 0.55))  # the left line reaches up
    p.drawLine(QPointF(x + w, y - h * 0.55), QPointF(x + w, y + h))  # the right line reaches down
    p.drawLine(QPointF(x - w, y - h * 0.2), QPointF(x + w, y - h * 0.5))  # the upper bar slants up to the right
    p.drawLine(QPointF(x - w, y + h * 0.5), QPointF(x + w, y + h * 0.2))  # the lower bar


class KeyFork(QWidget):
    """
    A tuning fork on its side, for choosing how many sharps or flats a key signature has.

    Attributes
    ----------
    value : int
        The chosen signature: sharps if positive, flats if negative, 0 for none.
    locked : bool
        While True the fork ignores the mouse and the keyboard.
    changed : Signal
        Emitted with the new `value` whenever it changes.

    Examples
    --------
    >>> fork = KeyFork()
    >>> got = []
    >>> _ = fork.changed.connect(got.append)
    >>> fork.set_value(2)
    >>> fork.set_value(2)  # no change, nothing said
    >>> got
    [2]
    """

    changed = Signal(int)

    def __init__(
        self,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the fork, set to no sharps or flats.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the fork. Keyword-only.

        Examples
        --------
        >>> KeyFork().value
        0
        """
        super().__init__(parent)
        self.value = 0
        self.locked = False
        self._wheel = 0  # the part of a wheel notch not yet used
        self._hover: int | None = None  # the number under the mouse, which is lit a little
        self._dragging = False  # True while the circle is held
        self._marker = node_position(0)  # where the circle is drawn, which lags behind `value` while it slides
        self._marker_color: QColor | None = None  # None for the highlight colour
        self._slide = QVariantAnimation(self)
        self._slide.setDuration(SLIDE_MS)
        self._slide.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._slide.setStartValue(0.0)
        self._slide.setEndValue(1.0)
        self._slide.valueChanged.connect(self._move)
        self._path = [self._marker]  # the way the circle is sliding along
        self.setFixedSize(FORK_W, FORK_H)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)  # numbers light up as the mouse passes over them
        self.setToolTip("Click a number, drag the circle or turn the mouse wheel: sharps on top, flats below, none at the left")

    def set_value(
        self,
        value: int,
        *,
        slide: bool = True,
    ) -> None:
        """
        Choose a signature and move the circle to it.

        Parameters
        ----------
        value : int
            The signature, kept between 7 flats and 7 sharps.
        slide : bool, default True
            Move the circle along the fork; if False it jumps. Keyword-only.

        Examples
        --------
        >>> fork = KeyFork()
        >>> fork.set_value(99)
        >>> fork.value
        7
        >>> fork.set_value(0, slide=False)
        >>> fork.value, fork._marker == node_position(0)
        (0, True)
        """
        value = max(-MAX_ACCIDENTALS, min(MAX_ACCIDENTALS, value))
        if value == self.value:
            return
        self._path = [self._marker, *path_between(self.value, b=value)[1:]]
        self.value = value
        self._slide.stop()
        if slide:
            self._slide.start()
        else:
            self._marker = node_position(value)
        self.update()
        self.changed.emit(value)

    def _move(self, t: float) -> None:
        """
        Put the circle a fraction of the way along the path it is sliding on.

        Parameters
        ----------
        t : float
            How far along, from 0 to 1.

        Examples
        --------
        >>> fork = KeyFork()
        >>> fork.set_value(1, slide=False)
        >>> fork._path = [node_position(1), node_position(2)]
        >>> fork._move(1.0)
        >>> fork._marker == node_position(2)
        True
        """
        self._marker = point_along(self._path, t=t)
        self.update()

    def set_marker_color(self, color: QColor | None) -> None:
        """
        Colour the circle, for a right or wrong answer.

        Parameters
        ----------
        color : QColor or None
            The colour to use, or None for the highlight colour.

        Examples
        --------
        >>> fork = KeyFork()
        >>> fork.set_marker_color(QColor("#2e7d32"))
        >>> fork._marker_color == QColor("#2e7d32")
        True
        """
        self._marker_color = color
        self.update()

    @staticmethod
    def value_at(point: QPointF) -> int | None:
        """
        Return the signature whose number is under a point.

        Parameters
        ----------
        point : QPointF
            A position in the widget.

        Returns
        -------
        int or None
            The signature there, or None if the point is not near a number.

        Examples
        --------
        >>> fork = KeyFork()
        >>> fork.value_at(node_position(3)), fork.value_at(node_position(-4)), fork.value_at(node_position(0))
        (3, -4, 0)
        >>> fork.value_at(QPointF(5, 130)) is None
        True
        """
        for value in range(-MAX_ACCIDENTALS, MAX_ACCIDENTALS + 1):
            if (node_position(value) - point).manhattanLength() <= 1.5 * NODE_R + 4:
                return value
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Pick up the circle if it was pressed, or choose the number that was clicked.

        Parameters
        ----------
        event : QMouseEvent
            The press. Only the left button does anything.

        Examples
        --------
        >>> from PySide6.QtCore import QEvent
        >>> fork = KeyFork()
        >>> point = node_position(-2)
        >>> fork.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.MouseButton.LeftButton,
        ...                                  Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
        >>> fork.value
        -2
        """
        if event.button() != Qt.MouseButton.LeftButton or self.locked:
            return
        self.setFocus()
        resting = self._slide.state() != QAbstractAnimation.State.Running  # a circle that is still sliding cannot be caught
        if resting and (event.position() - self._marker).manhattanLength() <= MARKER_R + 4:
            self._dragging = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        value = self.value_at(event.position())
        if value is not None:
            self.set_value(value)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Carry the circle along the fork while it is held, and light the number under the mouse otherwise.

        The signature changes to the nearest number as the circle passes it.

        Parameters
        ----------
        event : QMouseEvent
            The move.

        Examples
        --------
        >>> from PySide6.QtCore import QEvent
        >>> fork = KeyFork()
        >>> here = node_position(0)
        >>> there = node_position(3)
        >>> fork.mousePressEvent(QMouseEvent(QEvent.Type.MouseButtonPress, here, here, Qt.MouseButton.LeftButton,
        ...                                  Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
        >>> fork.mouseMoveEvent(QMouseEvent(QEvent.Type.MouseMove, there, there, Qt.MouseButton.NoButton,
        ...                                 Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
        >>> fork.value
        3
        """
        if self._dragging:
            self._marker = nearest_on_fork(event.position())
            nearest = min(
                range(-MAX_ACCIDENTALS, MAX_ACCIDENTALS + 1),
                key=lambda value: (node_position(value) - self._marker).manhattanLength(),
            )
            if nearest != self.value:
                self.value = nearest
                self.changed.emit(nearest)
            self.update()
            return
        hover = None if self.locked else self.value_at(event.position())
        near_circle = (event.position() - self._marker).manhattanLength() <= MARKER_R + 4
        if not self.locked and (near_circle or hover is not None):
            self.setCursor(Qt.CursorShape.OpenHandCursor if near_circle else Qt.CursorShape.PointingHandCursor)
        else:
            self.unsetCursor()
        if hover != self._hover:
            self._hover = hover
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Let go of the circle, which slides to the number it is nearest.

        Parameters
        ----------
        event : QMouseEvent
            The release.

        Examples
        --------
        >>> from PySide6.QtCore import QEvent
        >>> fork = KeyFork()
        >>> fork._dragging = True
        >>> fork._marker = node_position(0) + QPointF(9, 0)
        >>> fork.mouseReleaseEvent(QMouseEvent(QEvent.Type.MouseButtonRelease, fork._marker, fork._marker,
        ...                                    Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
        ...                                    Qt.KeyboardModifier.NoModifier))
        >>> fork._dragging
        False
        """
        if event.button() != Qt.MouseButton.LeftButton or not self._dragging:
            return
        self._dragging = False
        self.unsetCursor()
        self._path = [self._marker, node_position(self.value)]
        self._slide.start()

    def leaveEvent(self, event: QEvent) -> None:
        """
        Stop lighting a number when the mouse leaves the fork.

        Parameters
        ----------
        event : QEvent
            The leave event.

        Examples
        --------
        >>> fork = KeyFork()
        >>> fork._hover = 3
        >>> fork.leaveEvent(QEvent(QEvent.Type.Leave))
        >>> fork._hover is None
        True
        """
        self._hover = None
        self.update()
        super().leaveEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Move the circle one number along the fork for each notch of the wheel.

        Rolling up goes towards more sharps and down towards more flats, passing through the natural sign.

        Parameters
        ----------
        event : QWheelEvent
            The wheel turn.

        Examples
        --------
        >>> from PySide6.QtCore import QPoint
        >>> fork = KeyFork()
        >>> point = QPointF(100, 50)
        >>> fork.wheelEvent(QWheelEvent(point, point, QPoint(0, 0), QPoint(0, -120), Qt.MouseButton.NoButton,
        ...                             Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False))
        >>> fork.value
        -1
        """
        event.accept()
        if self.locked:
            return
        self._wheel += event.angleDelta().y()
        notches = int(self._wheel / WHEEL_NOTCH)  # whole notches, towards zero
        self._wheel -= notches * WHEEL_NOTCH
        if notches:
            self.set_value(self.value + notches)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Move the circle with the arrow keys: up or right for a sharp, down or left for a flat.

        Parameters
        ----------
        event : QKeyEvent
            The key press.

        Examples
        --------
        >>> from PySide6.QtCore import QEvent
        >>> fork = KeyFork()
        >>> fork.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier))
        >>> fork.value
        1
        """
        step = {Qt.Key.Key_Up: 1, Qt.Key.Key_Right: 1, Qt.Key.Key_Down: -1, Qt.Key.Key_Left: -1}.get(Qt.Key(event.key()))
        if step is None or self.locked:
            super().keyPressEvent(event)
            return
        self.set_value(self.value + step)

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the fork, its numbers and the circle on the chosen one.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request; the whole widget is always redrawn.

        Examples
        --------
        >>> KeyFork().grab().isNull()
        False
        """
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = self.palette()
        ink = palette.color(QPalette.ColorRole.WindowText)
        ground = palette.color(QPalette.ColorRole.Window)
        metal = blend(ground, b=ink, t=0.45)  # soft, like the outlines in the rest of the app
        outline = blend(ground, b=ink, t=0.55)
        accent = self._marker_color or palette.color(QPalette.ColorRole.Highlight)

        p.setPen(QPen(metal, LINE_W, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(fork_path())

        sign_font = QFont(self.font())
        sign_font.setPixelSize(24)
        number_font = QFont(self.font())
        number_font.setPixelSize(12)
        number_font.setWeight(QFont.Weight.DemiBold)
        paper = palette.color(QPalette.ColorRole.Base)
        highlight = palette.color(QPalette.ColorRole.Highlight)
        for value in range(-MAX_ACCIDENTALS, MAX_ACCIDENTALS + 1):
            c = node_position(value)
            lit = value == self._hover and value != self.value
            p.setPen(QPen(blend(outline, b=highlight, t=0.7) if lit else outline, 1.6 if lit else 1.2))
            p.setBrush(blend(paper, b=highlight, t=0.22) if lit else paper)
            p.drawEllipse(c, NODE_R, NODE_R)
            p.setPen(ink)
            if value == 0:
                draw_natural(p, center=c, height=NODE_R * 1.5, color=ink)
            else:
                p.setFont(number_font)
                p.drawText(
                    QRectF(c.x() - NODE_R, c.y() - NODE_R, 2 * NODE_R, 2 * NODE_R),
                    Qt.AlignmentFlag.AlignCenter,
                    str(abs(value)),
                )
        tip = FIRST_X + STEP * (MAX_ACCIDENTALS - 1) + STEP / 2 + 6  # past the end of the tines, to say which is which
        p.setFont(sign_font)
        p.setPen(metal)
        p.drawText(QRectF(tip, TOP_Y - 18, 30, 36), Qt.AlignmentFlag.AlignCenter, "♯")
        p.drawText(QRectF(tip, BOTTOM_Y - 18, 30, 36), Qt.AlignmentFlag.AlignCenter, "♭")

        p.setPen(QPen(accent.darker(115), 1.6))  # the circle on the chosen number
        p.setBrush(accent)
        p.drawEllipse(self._marker, MARKER_R, MARKER_R)
        if self.value:
            p.setFont(number_font)
            p.setPen(QColor("white"))
            p.drawText(
                QRectF(
                    self._marker.x() - MARKER_R,
                    self._marker.y() - MARKER_R,
                    2 * MARKER_R,
                    2 * MARKER_R,
                ),
                Qt.AlignmentFlag.AlignCenter,
                str(abs(self.value)),
            )
        else:
            draw_natural(p, center=self._marker, height=MARKER_R * 1.4, color=QColor("white"))
