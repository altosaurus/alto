"""
Get ready, while Alto sits idle just after it opens, what a first visit to a page would otherwise pay for.

The music font of the notation style is loaded by drawing a small staff out of sight. And most of what makes a page slow to open
the first time is not the page. Labels such as "F♯" and "B♭" use signs that the interface font does not have, so Qt looks for a
font that does, and it does so again for every size and weight of text, about 40 ms each time on Linux. Pages show such labels in
several sizes, so a first visit could spend a tenth of a second looking for fonts. Laying out a line with those signs once in each
size the interface uses, a little at a time while nothing else is happening, makes the first visit to a page about as quick as the
second.

Examples
--------
>>> warmed = []
>>> owner = QObject()
>>> start(owner, steps=[lambda: warmed.append(1), lambda: warmed.append(2)], delay=0)
>>> import time
>>> deadline = time.monotonic() + 2
>>> while len(warmed) < 2 and time.monotonic() < deadline:
...     app.processEvents()
>>> warmed
[1, 2]
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import (
    QObject,
    QTimer,
)
from PySide6.QtGui import (
    QFont,
    QFontMetricsF,
    QGuiApplication,
)

from alto.theory.pitch import Note
from alto.ui import zoom
from alto.ui.staff import StaffWidget

SIZES = (8, 9, 11, 12, 14, 15, 16, 18, 20, 22)  # the point sizes the interface's style sheets use, at 100%
SIGNS = "C♯ D♭ E♮ Abc 0123"  # the signs labels use that the interface font may not have, with ordinary text
START_DELAY_MS = 400  # after the window first appears, so its own first paint and the person's first click come first


def _text_step(size: float, *, bold: bool) -> Callable[[], None]:
    """
    Make the step that lays out the signs once in one size and weight, so Qt finds its fallback fonts for them now.

    Parameters
    ----------
    size : float
        The point size.
    bold : bool
        Whether the text is bold. Keyword-only.

    Returns
    -------
    callable
        The step.

    Examples
    --------
    >>> _text_step(12.0, bold=False)()
    """

    def step() -> None:
        """
        Lay out the signs in the step's size and weight.

        Examples
        --------
        >>> step()  # doctest: +SKIP
        """
        app = QGuiApplication.instance()
        font = QFont(app.font()) if isinstance(app, QGuiApplication) else QFont()
        font.setPointSizeF(size)
        font.setBold(bold)
        QFontMetricsF(font).horizontalAdvance(SIGNS)

    return step


def _staff_step() -> None:
    """
    Draw a small staff with notes, a clef and a key signature out of sight, which loads the music font of the notation style.

    Examples
    --------
    >>> _staff_step()
    """
    staff = StaffWidget()
    staff.resize(360, 160)
    staff.show_notes([[Note(4, letter=0)], [Note(4, letter=3, accidental=1)]], clef="treble", key=2)
    staff.grab()
    staff.deleteLater()


def warmup_steps() -> list[Callable[[], None]]:
    """
    List the steps of the warm-up: the application's own font size and each style sheet size, plain and bold, at the zoom.

    Returns
    -------
    list of callable
        The steps, each a few tens of milliseconds at most.

    Examples
    --------
    >>> len(warmup_steps())  # a staff, then the application's size and the ten style sheet sizes, in two weights
    23
    """
    app = QGuiApplication.instance()
    own = app.font().pointSizeF() if isinstance(app, QGuiApplication) else 10.0
    sizes = [own, *(size * zoom.factor() for size in SIZES)]
    return [_staff_step, *(_text_step(size, bold=bold) for size in sizes for bold in (False, True))]


def start(
    owner: QObject,
    *,
    steps: list[Callable[[], None]] | None = None,
    delay: int = START_DELAY_MS,
) -> None:
    """
    Run the warm-up's steps one at a time, each when the event loop has nothing else to do, beginning after a short delay.

    Input and painting are handled between the steps, so the window stays as responsive as it is without the warm-up. If the
    owner is deleted first (the window closed), the rest of the steps are dropped.

    Parameters
    ----------
    owner : QObject
        What the warm-up belongs to, usually the main window.
    steps : list of callable or None, default None
        The steps; None for the usual ones (`warmup_steps()`). Keyword-only.
    delay : int, default START_DELAY_MS
        How long to wait first, in milliseconds. Keyword-only.

    Examples
    --------
    >>> start(QObject(), steps=[], delay=0)  # nothing to do
    """
    remaining = list(steps if steps is not None else warmup_steps())
    timer = QTimer(owner)
    timer.setInterval(0)  # a zero timer fires when the event loop is idle

    def next_step() -> None:
        """
        Run the next step, and stop when there are none.

        Examples
        --------
        >>> next_step()  # doctest: +SKIP
        """
        if not remaining:
            timer.stop()
            timer.deleteLater()
            return
        remaining.pop(0)()

    timer.timeout.connect(next_step)
    QTimer.singleShot(delay, timer, timer.start)
