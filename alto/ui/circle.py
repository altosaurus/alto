"""
The circle of fifths: twelve wedges, the major keys on the outside and their relative minors on the inside.

C is at the top and each step clockwise is a fifth up, so the keys gather sharps on the right and flats on the left. The
disc in the middle shows the staff and key signature of the key being talked about. In an exercise one wedge is the question
and its name (or its Roman numeral) is blank until the answer is right.

Examples
--------
>>> circle = FifthsCircle()
>>> circle.show_question("major", place=3, title="F♯ minor")
>>> circle.target
('outer', 3)
"""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QPointF,
    QRectF,
    QSize,
    Qt,
    QVariantAnimation,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
)

from alto import settings
from alto.circle_schemes import (
    Scheme,
)
from alto.theory.fifths import (
    MAJORS,
    MINORS,
    NUMERALS,
    SIGNATURES,
    cells_of_key,
)
from alto.theory.scales import format_key_signature
from alto.ui.colors import blend
from alto.ui.engraving import (
    accidental_width,
    draw_accidental,
)
from alto.ui.notation import current as current_style
from alto.ui.staff import (
    StaffWidget,
    draw_key_signature,
)

OUTER_FROM = 0.746  # where the outer ring starts, as a fraction of the circle's radius
DISC = 0.485  # the radius of the disc in the middle
WEDGE = 30.0  # the angle of one wedge, in degrees
if TYPE_CHECKING:
    from collections.abc import Callable

OUTER_TEXT = (
    0.078  # the height of an outer name's letters, as a fraction of the circle's radius: a little under a third of the ring
)
INNER_TEXT = 0.07  # and of an inner name's, which sits in a ring of about the same width
MAX_BRIGHTNESS = 0.42  # the brightest a wedge looks, so that white names stay easy to read on it whatever its hue
SIGN_GAP = 0.3  # how big the notation font's sharps and flats are drawn beside text, as a fraction of the letters' height
SIGNS = {"♯": 1, "♭": -1, "♮": 0}  # the characters that are drawn as the notation font's own glyphs, and their signs
GLOW_MS = 450  # how long a right answer takes to brighten its wedge
WRONG_COLOR = QColor("#c62828")  # the red that a wrong answer turns its button, used for the cell as well
MAX_RADIUS = 320.0  # the largest the circle is drawn, in pixels: past this the names are bigger than they need to be to read
WRONG_MS = 900  # how long a wrong answer shows its warning color


def wedge_path(
    *,
    center: QPointF,
    inner: float,
    outer: float,
    index: int,
) -> QPainterPath:
    """
    Return the outline of one wedge of a ring.

    Parameters
    ----------
    center : QPointF
        The middle of the circle.
    inner : float
        The radius of the wedge's inner edge, in pixels. Keyword-only.
    outer : float
        The radius of its outer edge. Keyword-only.
    index : int
        Which wedge: 0 is the one at the top and they go clockwise. Keyword-only.

    Returns
    -------
    QPainterPath
        A closed shape, a piece of a ring 30 degrees wide.

    Examples
    --------
    >>> shape = wedge_path(center=QPointF(100, 100), inner=40, outer=90, index=0)
    >>> shape.contains(QPointF(100, 30)), shape.contains(QPointF(100, 170))  # the top of the circle, and the bottom
    (True, False)
    """
    start = 90.0 + WEDGE / 2 - WEDGE * index  # the angle of its counterclockwise edge, in Qt's counterclockwise degrees
    outer_box = QRectF(center.x() - outer, center.y() - outer, 2 * outer, 2 * outer)
    inner_box = QRectF(center.x() - inner, center.y() - inner, 2 * inner, 2 * inner)
    path = QPainterPath()
    path.arcMoveTo(outer_box, start)
    path.arcTo(outer_box, start, -WEDGE)
    path.arcTo(inner_box, start - WEDGE, WEDGE)  # back along the inner edge
    path.closeSubpath()
    return path


def wedge_middle(
    *,
    center: QPointF,
    radius: float,
    index: int,
) -> QPointF:
    """
    Return the point in the middle of a wedge, at a given distance from the center.

    Parameters
    ----------
    center : QPointF
        The middle of the circle.
    radius : float
        How far out, in pixels. Keyword-only.
    index : int
        Which wedge, clockwise from the top. Keyword-only.

    Returns
    -------
    QPointF
        The point.

    Examples
    --------
    >>> wedge_middle(center=QPointF(100, 100), radius=50, index=0).toTuple()  # straight up
    (100.0, 50.0)
    >>> round(wedge_middle(center=QPointF(100, 100), radius=50, index=3).x())  # a quarter of the way around: to the right
    150
    """
    angle = math.radians(-90 + WEDGE * index)  # the screen's y grows downwards, so clockwise is increasing
    return QPointF(center.x() + radius * math.cos(angle), center.y() + radius * math.sin(angle))


def wedge_color(
    index: int,
    *,
    inner: bool,
    lift: float = 0.0,
    scheme: Scheme | None = None,
) -> QColor:
    """
    Return the color of a wedge in a color scheme: quiet when it is not being talked about and bright when it is.

    Parameters
    ----------
    index : int
        Which wedge, clockwise from the top.
    inner : bool
        Whether it is in the inner ring. Keyword-only.
    lift : float, default 0.0
        How bright it is, from 0 (quiet) to 1 (lit). Keyword-only.
    scheme : Scheme or None, default None
        The color scheme; the one chosen in the circle of fifths settings if None. Keyword-only.

    Returns
    -------
    QColor
        The color.

    Examples
    --------
    >>> from alto.circle_schemes import preset
    >>> spectrum = preset("spectrum")
    >>> wedge_color(0, inner=False, lift=1.0, scheme=spectrum).hue(), wedge_color(6, inner=False, scheme=spectrum).hue()
    (0, 180)
    >>> lit, quiet = (wedge_color(0, inner=False, lift=amount, scheme=spectrum) for amount in (1.0, 0.0))
    >>> lit.lightness() > quiet.lightness()
    True
    >>> # no wedge looks too bright for white names
    >>> every = [wedge_color(i, inner=False, lift=1.0, scheme=spectrum) for i in range(12)]
    >>> all(0.299 * c.redF() + 0.587 * c.greenF() + 0.114 * c.blueF() <= 0.44 for c in every)
    True
    """
    chosen = scheme or settings.circle.active_scheme()
    red, green, blue = chosen.color("inner" if inner else "outer", place=index, lift=lift)
    return QColor.fromRgbF(red, green, blue)


def write_text(
    p: QPainter,
    *,
    center: QPointF,
    text: str,
    pixels: float,
    weight: QFont.Weight,
    color: QColor,
    max_width: float | None = None,
) -> None:
    """
    Write a line of text centered on a point, with its sharps and flats drawn as the notation font draws them.

    The letters are in the app's own font. Its ♭ is the shape of a small "b", though, and does not look like a flat sign, so
    the sharps, flats and naturals are the glyphs of the notation style that the staff is drawn in, sized to the letters.

    Parameters
    ----------
    p : QPainter
        The painter to draw with.
    center : QPointF
        The middle of the line. Keyword-only.
    text : str
        What to write, such as "B♭m" or "F♯ major". Keyword-only.
    pixels : float
        The size of the letters. Keyword-only.
    weight : QFont.Weight
        How heavy they are. Keyword-only.
    color : QColor
        The color. Keyword-only.
    max_width : float or None, default None
        The widest the line may be. A longer line is written smaller to fit. Keyword-only.

    Examples
    --------
    >>> from PySide6.QtGui import QImage
    >>> image = QImage(120, 60, QImage.Format.Format_ARGB32)
    >>> image.fill(QColor("black"))
    >>> painter = QPainter(image)
    >>> write_text(painter, center=QPointF(60, 30), text="B♭m", pixels=24, weight=QFont.Weight.Bold, color=QColor("white"))
    >>> painter.end()
    True
    >>> any(image.pixelColor(x, 30).lightness() > 128 for x in range(20, 100))
    True
    """
    notation = current_style().font
    runs = re.findall(r"[♯♭♮]|[^♯♭♮]+", text)
    font = QFont()
    font.setWeight(weight)

    def measure(size: float) -> tuple[QFontMetricsF, float, float, list[float]]:
        """
        Measure the line at a size.

        Parameters
        ----------
        size : float
            The size of the letters.

        Returns
        -------
        tuple of (QFontMetricsF, float, float, list of float)
            The font's metrics, the gap and padding around a sign, and the width of each run.
        """
        font.setPixelSize(max(int(size), 6))
        sign_gap, sign_pad = size * SIGN_GAP, size * 0.05
        signs = {}
        if notation:
            for sign in set(runs) & set(SIGNS):
                signs[sign] = accidental_width(font=notation, sign=SIGNS[sign], gap=sign_gap) + 2 * sign_pad
        font_metrics = QFontMetricsF(font)
        # Only measure what is not a notation sign: the text font has no ♯ or ♭, so Qt searches other fonts for them at every
        # size, about 40 ms each time, for a width that would not be used.
        runs_width = [signs[part] if part in signs else font_metrics.horizontalAdvance(part) for part in runs]
        return font_metrics, sign_gap, sign_pad, runs_width

    metrics, gap, pad, widths = measure(pixels)
    if max_width is not None and sum(widths) > max_width:  # too wide: write it smaller, so that it fits
        pixels *= max_width / sum(widths)
        metrics, gap, pad, widths = measure(pixels)
    left = center.x() - sum(widths) / 2
    baseline = center.y() + metrics.capHeight() / 2
    p.save()
    p.setFont(font)
    p.setPen(color)
    for run, width in zip(runs, widths, strict=True):
        if notation and run in SIGNS:  # a flat's bowl sits on the baseline; a sharp or natural is centered on the capitals
            middle = baseline - 0.55 * gap if SIGNS[run] < 0 else baseline - metrics.capHeight() / 2
            draw_accidental(p, font=notation, sign=SIGNS[run], x=left + pad, y=middle, gap=gap, color=color)
        else:
            p.drawText(QPointF(left, baseline), run)
        left += width
    p.restore()


class FifthsCircle(QWidget):
    """
    The circle of fifths, drawn for an exercise.

    Attributes
    ----------
    kind : str
        What is being asked: "major", "minor" or "numeral", or "" for nothing.
    target : tuple of (str, int) or None
        The cell asked about: its ring ("outer" or "inner") and its place clockwise from the top.
    shown : dict of str to set of int
        For each ring, the places whose key name is written.
    lit : set of int
        The places of the chords of the key, in a Roman numeral question; both rings are lit there.
    numerals : dict of tuple of (str, int) to str
        The Roman numeral written in each cell that has one.
    title : str
        The big text in the middle.
    subtitle : str
        The small text in the middle.
    signature : int or None
        The key signature drawn on the staff in the middle, or None for no staff.

    Examples
    --------
    >>> circle = FifthsCircle()
    >>> circle.show_question("major", place=0, title="A minor")
    >>> circle.reveal(animate=False)
    >>> circle.shown["outer"], circle.signature
    ({0}, 0)
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the circle, with nothing asked.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> FifthsCircle().target is None
        True
        """
        super().__init__(parent)
        self.kind = ""
        self.target: tuple[str, int] | None = None
        self.shown: dict[str, set[int]] = {"outer": set(), "inner": set()}
        self.lit: set[int] = set()
        self.numerals: dict[tuple[str, int], str] = {}
        self.title = ""
        self.subtitle = ""
        self.signature: int | None = None
        self._place = 0  # the place that was asked about, and the key of a numeral question
        self._key = 0
        self._glow = 0.0  # how far the answered cell has brightened, from 0 to 1
        self._warning: tuple[str, int, float] | None = None  # a cell showing its warning, and how strongly
        self._animations: list[QVariantAnimation] = []
        self.setMinimumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAccessibleName("Circle of fifths")

    def sizeHint(self) -> QSize:
        """
        Return the size it would like: a square, big enough to read.

        Returns
        -------
        QSize
            The size.

        Examples
        --------
        >>> FifthsCircle().sizeHint().width()
        460
        """
        return QSize(460, 460)

    def show_question(
        self,
        kind: str,
        *,
        place: int,
        title: str,
        ring: str | None = None,
        key: int | None = None,
    ) -> None:
        """
        Ask about a cell, showing what the question needs and leaving the answer blank.

        A "major" question shows the minor keys and asks for the major of one of them; a "minor" question shows the majors and
        asks for a minor; a "numeral" question shows every name, lights the six chords of a key with its staff in the middle, and
        asks for the Roman numeral of one of them.

        Parameters
        ----------
        kind : str
            "major", "minor" or "numeral".
        place : int
            The place of the cell asked about, clockwise from the top. Keyword-only.
        title : str
            The big text in the middle, such as "F♯ minor". Keyword-only.
        ring : str or None, default None
            The ring of the cell asked about; for "major" the outer one and for "minor" the inner one if None. Keyword-only.
        key : int or None, default None
            For a "numeral" question, the place of the key whose chords they are. Keyword-only.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.show_question("minor", place=3, title="A major")
        >>> circle.target, circle.shown["outer"] == set(range(12)), circle.shown["inner"], circle.signature
        (('inner', 3), True, set(), None)
        >>> circle.show_question("numeral", place=11, ring="outer", key=0, title="C major")
        >>> sorted(circle.lit), circle.signature, circle.numerals
        ([0, 1, 11], 0, {})
        """
        self.reset()
        self.kind, self._place = kind, place
        everyone = set(range(12))
        if kind == "numeral":
            self._key = key if key is not None else place
            self.target = (ring or "outer", place)
            self.shown = {"outer": set(everyone), "inner": set(everyone)}
            self.lit = {(self._key + step) % 12 for step in (-1, 0, 1)}
            self.signature = SIGNATURES[self._key]
            self.subtitle = "Roman numeral?"
        elif kind == "minor":
            self.target = (ring or "inner", place)
            self.shown = {"outer": set(everyone), "inner": set()}
            self.subtitle = "relative minor?"
        else:
            self.target = (ring or "outer", place)
            self.shown = {"outer": set(), "inner": set(everyone)}
            self.subtitle = "relative major?"
        self.title = title
        self.setAccessibleDescription(self._describe(answered=False))
        self.update()

    def _describe(self, *, answered: bool) -> str:
        """
        Describe what the circle shows, in words for a screen reader.

        Parameters
        ----------
        answered : bool
            Whether the question has been answered.

        Returns
        -------
        str
            A description of the question, or of the answer.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.show_question("major", place=3, title="F♯ minor")
        >>> circle.accessibleDescription()
        'Outer ring: the major keys, the one beside F♯m blank. Inner ring: the minor keys. F♯ minor, relative major?'
        >>> circle.reveal(animate=False)
        >>> circle.accessibleDescription()
        'A major, 3 sharps. Its relative minor is F♯m.'
        """
        place = self._place
        if answered and self.kind == "numeral":
            names = ", ".join(f"{numeral} {self._name_of(cell)}" for cell, numeral in self.numerals.items())
            return f"The chords of {self.title}: {names}."
        if answered:
            major, minor = MAJORS[place][0], MINORS[place][0]
            key = format_key_signature(SIGNATURES[place])
            if self.kind == "major":
                return f"{major} major, {key}. Its relative minor is {minor}."
            return f"{minor[:-1]} minor, {key}. Its relative major is {major}."
        if self.kind == "numeral":
            return (
                f"The chords of {self.title} are lit. The one over {self._name_of(self.target)} is the question. Roman numeral?"
            )
        if self.kind == "minor":
            return (
                f"Inner ring: the minor keys, the one beside {MAJORS[place][0]} blank. Outer ring: the major keys. "
                f"{self.title}, relative minor?"
            )
        return (
            f"Outer ring: the major keys, the one beside {MINORS[place][0]} blank. Inner ring: the minor keys. "
            f"{self.title}, relative major?"
        )

    @staticmethod
    def _name_of(cell: tuple[str, int] | None) -> str:
        """
        Return the first name of the key in a cell.

        Parameters
        ----------
        cell : tuple of (str, int) or None
            The ring and place, or None for no cell.

        Returns
        -------
        str
            The name, such as "F♯m" or "B♭"; "" for no cell.

        Examples
        --------
        >>> FifthsCircle._name_of(("inner", 3)), FifthsCircle._name_of(("outer", 10)), FifthsCircle._name_of(None)
        ('F♯m', 'B♭', '')
        """
        if cell is None:
            return ""
        ring, place = cell
        return MINORS[place][0] if ring == "inner" else MAJORS[place][0]

    def reset(self) -> None:
        """
        Clear everything: no question, no names shown, no animation running.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.show_question("major", place=2, title="B minor")
        >>> circle.reset()
        >>> circle.target is None and circle.title == "" and circle.lit == set()
        True
        """
        for animation in self._animations:
            animation.stop()
        self._animations.clear()
        self.kind = ""
        self.target, self.signature = None, None
        self.shown = {"outer": set(), "inner": set()}
        self.lit.clear()
        self.numerals = {}
        self._glow = 0.0
        self._warning = None
        self.title = self.subtitle = ""
        self.update()

    def reveal(self, *, animate: bool = True) -> None:
        """
        Show the answer: the key's name in its cell, brightened, and its staff and key signature in the middle.

        For a Roman numeral question every chord of the key shows its numeral, as the circle in the reference does.

        Parameters
        ----------
        animate : bool, default True
            Brighten the cell gradually; if False it is bright at once. Keyword-only.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.show_question("minor", place=5, title="B major / C♭ major")
        >>> circle.reveal(animate=False)
        >>> circle.shown["inner"], circle.title, circle.subtitle, circle.signature
        ({5}, 'G♯ minor', '5 sharps', 5)
        """
        place = self._place
        self._warning = None
        if self.kind == "numeral":
            self.numerals = cells_of_key(self._key)
            self.subtitle = " ".join(NUMERALS)
        else:
            if self.kind == "minor":
                self.shown["inner"].add(place)
                self.title = f"{MINORS[place][0][:-1]} minor"
            else:
                self.shown["outer"].add(place)
                self.title = f"{MAJORS[place][0]} major"
            self.signature = SIGNATURES[place]
            self.subtitle = format_key_signature(SIGNATURES[place])
        self.setAccessibleDescription(self._describe(answered=True))
        if animate:
            self._animate(GLOW_MS, step=self._set_glow)
        else:
            self._glow = 1.0
            self.update()

    def set_subtitle(self, text: str) -> None:
        """
        Change the small text in the middle, for example to say that a second answer is wanted.

        Parameters
        ----------
        text : str
            The new text.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.set_subtitle("and its other name")
        >>> circle.subtitle
        'and its other name'
        """
        self.subtitle = text
        self.update()

    def flash_wrong(self) -> None:
        """
        Flash the cell asked about in the red of a wrong answer, striped as well so that it still shows on the red wedge.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.show_question("major", place=0, title="A minor")
        >>> circle.flash_wrong()
        >>> circle._warning is not None
        True
        """
        if self.target is None:
            return
        ring, place = self.target
        self._warning = (ring, place, 1.0)

        def fade(t: float) -> None:
            """
            Let the warning fade as the flash goes on.

            Parameters
            ----------
            t : float
                How far through the flash: 0 at the start, 1 at the end, when it is gone.

            Examples
            --------
            >>> fade(1.0)  # doctest: +SKIP
            """
            self._warning = None if t >= 1.0 else (ring, place, 1.0 - t)
            self.update()

        self._animate(WRONG_MS, step=fade)
        self.update()

    def _animate(
        self,
        duration: int,
        *,
        step: Callable[[float], object],
    ) -> None:
        """
        Run an animation from 0 to 1 over a time, calling a function with its progress.

        Parameters
        ----------
        duration : int
            How long it takes, in milliseconds.
        step : callable
            Called with a number from 0 to 1. Keyword-only.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle._animate(10, step=lambda t: None)
        >>> len(circle._animations)
        1
        """
        animation = QVariantAnimation(self)
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.valueChanged.connect(step)
        self._animations.append(animation)
        animation.start()

    def _set_glow(self, level: float) -> None:
        """
        Set how bright the answered cell is, and redraw.

        Parameters
        ----------
        level : float
            From 0 (as it was when asked) to 1 (fully lit).

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle._set_glow(0.5)
        >>> circle._glow
        0.5
        """
        self._glow = level
        self.update()

    def lift_of(
        self,
        ring: str,
        *,
        place: int,
    ) -> float:
        """
        Return how bright a cell is drawn, from 0 (quiet) to 1 (fully lit).

        The cell asked about is half lit, and brightens when it is answered. The cell beside it on the other ring is a little
        lit, to show the pair; in a Roman numeral question the six chords of the key are lit instead.

        Parameters
        ----------
        ring : str
            "outer" or "inner".
        place : int
            The place clockwise from the top. Keyword-only.

        Returns
        -------
        float
            The brightness.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.show_question("major", place=0, title="A minor")
        >>> circle.lift_of("outer", place=0), circle.lift_of("inner", place=0), circle.lift_of("outer", place=5)
        (0.5, 0.3, 0.0)
        >>> circle.reveal(animate=False)
        >>> circle.lift_of("outer", place=0)
        1.0
        """
        if self.target == (ring, place):
            return 0.5 + 0.5 * self._glow
        if self.kind == "numeral":
            return 0.38 if place in self.lit else 0.0
        return 0.3 if self.target is not None and self.target[1] == place else 0.0

    def geometry_of(self) -> tuple[QPointF, float]:
        """
        Return where the circle is drawn: its middle and its radius.

        The circle fits the widget as a square in the middle of it, but no larger than `MAX_RADIUS`.

        Returns
        -------
        tuple of QPointF and float
            The center and the radius, in pixels.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.resize(400, 300)
        >>> middle, radius = circle.geometry_of()
        >>> middle.toTuple(), radius < 150
        ((200.0, 150.0), True)
        >>> circle.resize(2400, 2000)
        >>> circle.geometry_of()[1] == MAX_RADIUS
        True
        """
        center = QPointF(self.width() / 2, self.height() / 2)
        return center, min(max(min(self.width(), self.height()) / 2 - 4.0, 10.0), MAX_RADIUS)

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the two rings, the names, the question and the disc in the middle.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request; the whole circle is always redrawn.

        Examples
        --------
        >>> circle = FifthsCircle()
        >>> circle.resize(400, 400)
        >>> circle.show_question("major", place=0, title="A minor")
        >>> circle.grab().isNull()
        False
        """
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        center, radius = self.geometry_of()
        scheme = settings.circle.active_scheme()
        rings = {"outer": (OUTER_FROM * radius, radius), "inner": (DISC * radius, OUTER_FROM * radius)}
        p.setPen(
            QPen(self.palette().color(QPalette.ColorRole.Window), max(radius / 160, 1.0)),
        )  # the gaps are the app's own background
        for index in range(12):
            for ring, (inner, outer) in rings.items():
                shade = wedge_color(index, inner=ring == "inner", lift=self.lift_of(ring, place=index), scheme=scheme)
                shape = wedge_path(center=center, inner=inner, outer=outer, index=index)
                p.setBrush(shade)
                p.drawPath(shape)
                if self._warning is not None and self._warning[:2] == (ring, index):
                    hot = QColor(WRONG_COLOR)
                    hot.setAlphaF(self._warning[2])
                    p.setBrush(hot)
                    p.drawPath(shape)
                    stripes = QColor("white")
                    stripes.setAlphaF(0.35 * self._warning[2])
                    p.setBrush(QBrush(stripes, Qt.BrushStyle.BDiagPattern))
                    p.drawPath(shape)
        if self.target is not None:  # the cell being asked, outlined as on the circle itself
            ring, place = self.target
            inner, outer = rings[ring]
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(
                QPen(self.palette().color(QPalette.ColorRole.WindowText), max(radius / 100, 2.0)),
            )  # the text color shows in either theme
            p.drawPath(wedge_path(center=center, inner=inner, outer=outer, index=place))
        self._draw_labels(p, center=center, radius=radius, scheme=scheme)
        self._draw_disc(p, center=center, radius=radius)

    def _draw_labels(
        self,
        p: QPainter,
        *,
        center: QPointF,
        radius: float,
        scheme: Scheme,
    ) -> None:
        """
        Write the names of the keys that are shown, with the Roman numeral of any chord that has one.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        center : QPointF
            The middle of the circle. Keyword-only.
        radius : float
            The radius of the circle, in pixels. Keyword-only.
        scheme : Scheme
            The color scheme, which says what color the names are. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(300, 300, QImage.Format.Format_ARGB32)
        >>> painter = QPainter(image)
        >>> from alto.circle_schemes import preset
        >>> FifthsCircle()._draw_labels(painter, center=QPointF(150, 150), radius=140, scheme=preset("midnight"))
        >>> painter.end()
        True
        """
        given = None if self.target is None or self.kind == "numeral" else ("inner" if self.target[0] == "outer" else "outer")
        for ring, names_of, middle, size in (
            ("inner", MINORS, (DISC + OUTER_FROM) / 2, INNER_TEXT),
            ("outer", MAJORS, (OUTER_FROM + 1.0) / 2, OUTER_TEXT),
        ):
            for index in sorted(self.shown[ring]):
                at = wedge_middle(center=center, radius=middle * radius, index=index)
                asked = (ring, index) == self.target or (given == ring and self.target is not None and index == self.target[1])
                self._write(
                    p,
                    at=at,
                    names=names_of[index],
                    numeral=self.numerals.get((ring, index), ""),
                    size=radius * size,
                    weight=QFont.Weight.Bold if ring == "outer" or asked else QFont.Weight.Medium,
                    colors=scheme.names(),
                )

    @staticmethod
    def _write(
        p: QPainter,
        *,
        at: QPointF,
        names: tuple[str, ...],
        numeral: str,
        size: float,
        weight: QFont.Weight,
        colors: dict[str, str],
    ) -> None:
        """
        Write what a cell says, stacked and centered: the key's name, its other name smaller and grayer, and its numeral.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        at : QPointF
            The middle of the text. Keyword-only.
        names : tuple of str
            The key's names; the first is the main one, the second (if any) is the same key spelled another way. Keyword-only.
        numeral : str
            The Roman numeral of the chord, or "" for none. Keyword-only.
        size : float
            The size of the main name's letters, in pixels. Keyword-only.
        weight : QFont.Weight
            How heavy the main name is. Keyword-only.
        colors : dict of str to str
            The colors of the writing, from `Scheme.text`: "ink" for the name, "muted" for the rest. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(100, 100, QImage.Format.Format_ARGB32)
        >>> painter = QPainter(image)
        >>> from alto.circle_schemes import preset
        >>> inks = preset("spectrum").names()
        >>> FifthsCircle._write(
        ...     painter, at=QPointF(50, 50), names=("B", "C♭"), numeral="V", size=14, weight=QFont.Weight.Bold, colors=inks
        ... )
        >>> painter.end()
        True
        """
        lines = [(names[0], size, weight, QColor(colors["ink"]))]
        if len(names) > 1:
            lines.append((f"/{names[1]}", size * 0.78, QFont.Weight.Normal, QColor(colors["muted"])))
        if numeral:
            lines.append((numeral, size * 0.85, QFont.Weight.Normal, QColor(colors["muted"])))
        heights = [pixels * 1.3 for _, pixels, _, _ in lines]
        top = at.y() - sum(heights) / 2
        for (text, pixels, heavy, color), height in zip(lines, heights, strict=True):
            write_text(p, center=QPointF(at.x(), top + height / 2), text=text, pixels=pixels, weight=heavy, color=color)
            top += height

    def _draw_disc(
        self,
        p: QPainter,
        *,
        center: QPointF,
        radius: float,
    ) -> None:
        """
        Draw the disc in the middle: the staff with the key signature once the answer is known, and the words.

        Parameters
        ----------
        p : QPainter
            The painter to draw with.
        center : QPointF
            The middle of the circle. Keyword-only.
        radius : float
            The radius of the circle, in pixels. Keyword-only.

        Examples
        --------
        >>> from PySide6.QtGui import QImage
        >>> image = QImage(300, 300, QImage.Format.Format_ARGB32)
        >>> painter = QPainter(image)
        >>> FifthsCircle()._draw_disc(painter, center=QPointF(150, 150), radius=140)
        >>> painter.end()
        True
        """
        r = DISC * radius
        window, text = self.palette().color(QPalette.ColorRole.Window), self.palette().color(QPalette.ColorRole.WindowText)
        p.setPen(QPen(blend(window, b=text, t=0.2), max(radius / 160, 1.0)))
        p.setBrush(window)  # the disc is the app's own background, light or dark
        p.drawEllipse(center, r, r)
        pale = text
        if self.signature is not None:
            gap = r * 0.115
            bottom = center.y() + gap * 1.0 - r * 0.2
            p.setPen(QPen(blend(window, b=text, t=0.5), 1.2))
            for line in range(5):
                y = bottom - line * gap
                p.drawLine(QPointF(center.x() - r * 0.62, y), QPointF(center.x() + r * 0.62, y))
            font = current_style().font
            left = center.x() - r * 0.55
            # noinspection PyProtectedMember
            StaffWidget._draw_clef(p, clef="treble", x=left, bottom=bottom, gap=gap, color=pale, font=font)
            draw_key_signature(
                p,
                clef="treble",
                key=self.signature,
                x=left + gap * 3.4,
                bottom=bottom,
                gap=gap,
                color=pale,
                step=gap * 1.15,
                font=font,
            )
        top = center.y() + (r * 0.32 if self.signature is not None else -r * 0.06)  # under the staff, or in the middle
        write_text(
            p,
            center=QPointF(center.x(), top),
            text=self.title,
            pixels=r * 0.2,
            weight=QFont.Weight.DemiBold,
            color=pale,
            max_width=r * 1.6,
        )
        write_text(
            p,
            center=QPointF(center.x(), top + r * 0.26),
            text=self.subtitle,
            pixels=r * 0.14,
            weight=QFont.Weight.Normal,
            color=blend(window, b=text, t=0.65),
            max_width=r * 1.45,
        )
