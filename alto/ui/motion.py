"""
Animations and feedback delays, run in one place so that tests decide
when they happen.

The interface moves: pages slide, feedback stays on screen for a moment
and the next question follows. Each of those goes
through this module: `play` starts an animation, `later` runs a step
after a delay and `start_timer` starts a timer that
does. In the app they take their real time. A button is given its key
with `set_shortcut`.

Tests switch to instant motion with `set_instant`. Then nothing moves on
by itself: animations hold still and delayed steps
and timers wait in a queue, however long the test takes, until it calls
`settle`. That runs everything waiting, in the order
it was asked for, at once. So a test can look at the state just after an
action (the feedback showing, a page about to
slide), and the motion happens only when the test says so, never during
some other wait. A button's key clicks it at once,
since its pressed look is all there is to see in the meantime.

Examples
--------
>>> set_instant(True)
>>> owner = QObject()
>>> done = []
>>> later(
...     900,
...     owner=owner,
...     step=lambda: done.append("cleared"),
... )
>>> QCoreApplication.processEvents()  # nothing happens by itself
>>> done, busy()
([], True)
>>> settle()
>>> done, busy()
(['cleared'], False)
>>> set_instant(False)
"""

from __future__ import annotations

import time
from collections.abc import Callable

import shiboken6
from PySide6.QtCore import (
    QAbstractAnimation,
    QCoreApplication,
    QEvent,
    QObject,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QKeySequence,
    QShortcutEvent,
)
from PySide6.QtWidgets import QAbstractButton

_instant = False


class _Pending:
    """
    Motion that has been asked for and has not happened yet: a delayed
    step, a timer or an animation.

    Examples
    --------
    >>> done = []
    >>> pending = _Pending(
    ...     alive=lambda: not done,
    ...     run=lambda: done.append(1),
    ... )
    >>> pending.waiting()
    True
    >>> pending.run()
    >>> pending.waiting(), done
    (False, [1])
    """

    def __init__(
        self,
        *,
        alive: Callable[[], bool],
        run: Callable[[], object],
    ) -> None:
        """
        Hold a piece of motion.

        Parameters
        ----------
        alive : callable
            Says whether the motion is still to come. It is not if it
            has happened, or was stopped, or what it belonged to
            was deleted. Keyword-only.
        run : callable
            Makes it happen at once. Keyword-only.

        Examples
        --------
        >>> _Pending(alive=lambda: True, run=print).ran
        False
        """
        self._alive = alive
        self._run = run
        self.ran = False

    def waiting(self) -> bool:
        """
        Say whether the motion is still to come.

        Returns
        -------
        bool
            True if it has not happened and has not been stopped or
            deleted.

        Examples
        --------
        >>> _Pending(
        ...     alive=lambda: False, run=print
        ... ).waiting()
        False
        """
        return not self.ran and self._alive()

    def run(self) -> None:
        """
        Make the motion happen, once, if it is still to come.

        Examples
        --------
        >>> done = []
        >>> pending = _Pending(
        ...     alive=lambda: True,
        ...     run=lambda: done.append(1),
        ... )
        >>> pending.run()
        >>> pending.run()
        >>> done
        [1]
        """
        if self.waiting():
            self.ran = True
            self._run()


_queue: list[
    _Pending
    # every piece of motion asked for, oldest first; finished ones are
    # dropped as it grows
] = []


def _add(pending: _Pending) -> None:
    """
    Remember a piece of motion, dropping the ones that are over so the
    list stays short.

    Parameters
    ----------
    pending : _Pending
        The motion.

    Examples
    --------
    >>> _add(
    ...     _Pending(alive=lambda: False, run=print)
    ... )
    >>> busy()
    False
    >>> for _ in range(
    ...     40
    ... # motion that is over is dropped, so the list does not grow
    ... # without end
    ... ):
    ...     _add(
    ...         _Pending(
    ...             alive=lambda: False, run=print
    ...         )
    ...     )
    >>> len(_queue) <= 33
    True
    """
    if len(_queue) > 32:
        _queue[:] = [other for other in _queue if other.waiting()]
    _queue.append(pending)


def instant() -> bool:
    """
    Say whether motion waits for `settle`, as it does in tests.

    Returns
    -------
    bool
        True if animations and delays hold until a test settles them.

    Examples
    --------
    >>> instant()
    False
    """
    return _instant


def set_instant(on: bool) -> None:
    """
    Make motion wait for `settle`, for tests, or give it back its real
    time.

    Parameters
    ----------
    on : bool
        True for instant motion.

    Examples
    --------
    >>> set_instant(True)
    >>> instant()
    True
    >>> set_instant(False)
    """
    global _instant  # noqa: PLW0603  (one switch for the whole interface)
    _instant = on
    _queue.clear()


def _valid(item: QObject) -> bool:
    """
    Say whether a Qt object still exists.

    Parameters
    ----------
    item : QObject
        The object.

    Returns
    -------
    bool
        False once Qt has deleted it.

    Examples
    --------
    >>> _valid(QObject())
    True
    """
    return shiboken6.isValid(item)


def later(
    delay: int,
    *,
    owner: QObject,
    step: Callable[[], object],
) -> None:
    """
    Run a step after a delay, such as clearing wrong-answer feedback so
    the learner can try again.

    Parameters
    ----------
    delay : int
        How long to wait, in milliseconds. With instant motion the step
        waits for `settle` instead.
    owner : QObject
        The object the step belongs to. If it is deleted first, the step
        does not run. Keyword-only.
    step : callable
        What to run. Keyword-only.

    Examples
    --------
    >>> set_instant(True)
    >>> owner = QObject()
    >>> done = []
    >>> later(
    ...     450,
    ...     owner=owner,
    ...     step=lambda: done.append("retry"),
    ... )
    >>> settle()
    >>> done
    ['retry']
    >>> set_instant(False)
    """
    pending = _Pending(alive=lambda: _valid(owner), run=step)
    _add(pending)
    if not _instant:
        QTimer.singleShot(delay, owner, pending.run)


def start_timer(
    timer: QTimer,
    *,
    delay: int,
) -> None:
    """
    Start a single-shot timer whose timeout is part of the interface's
    motion, such as moving on to the next question.

    The timer can be stopped as usual, and then it does not fire.

    Parameters
    ----------
    timer : QTimer
        The timer, which fires once.
    delay : int
        Its interval, in milliseconds. With instant motion it waits for
        `settle` instead. Keyword-only.

    Examples
    --------
    >>> set_instant(True)
    >>> timer = QTimer()
    >>> timer.setSingleShot(True)
    >>> fired = []
    >>> _ = timer.timeout.connect(
    ...     lambda: fired.append(1)
    ... )
    >>> start_timer(timer, delay=1200)
    >>> timer.isActive(), busy()
    (True, True)
    >>> settle()
    >>> fired, timer.isActive()
    ([1], False)
    >>> start_timer(timer, delay=1200)
    >>> timer.stop()  # a stopped timer does not fire
    >>> settle()
    >>> fired
    [1]
    >>> set_instant(False)
    """

    def fire() -> None:
        """
        Fire the timer now, as if its time were up.

        Examples
        --------
        >>> fire()  # doctest: +SKIP
        """
        timer.stop()
        timer.timeout.emit()

    _add(_Pending(alive=lambda: _valid(timer) and timer.isActive(), run=fire))
    timer.start(_HELD_MS if _instant else delay)


# a timer held for a test is started for a day, so it shows as active
# and can be stopped, but never fires
_HELD_MS = 86_400_000


def play(animation: QAbstractAnimation) -> None:
    """
    Start an animation. With instant motion it holds still at its start
    until `settle` moves it to its end.

    Parameters
    ----------
    animation : QAbstractAnimation
        The animation, or a group of them. It finishes as usual, with
        its `finished` signal.

    Examples
    --------
    >>> from PySide6.QtCore import QVariantAnimation
    >>> set_instant(True)
    >>> animation = QVariantAnimation()
    >>> animation.setDuration(220)
    >>> animation.setStartValue(0.0)
    >>> animation.setEndValue(1.0)
    >>> play(animation)
    >>> (
    ...     animation.state()
    ...     == QAbstractAnimation.State.Stopped,
    ...     busy(),
    ... )
    (False, True)
    >>> settle()
    >>> (
    ...     animation.currentValue(),
    ...     animation.state()
    ...     == QAbstractAnimation.State.Stopped,
    ... )
    (1.0, True)
    >>> set_instant(False)
    """
    stopped = QAbstractAnimation.State.Stopped
    pending = _Pending(
        alive=lambda: _valid(animation) and animation.state() != stopped,
        run=lambda: animation.setCurrentTime(animation.totalDuration()),
    )
    _add(pending)
    animation.start()
    if _instant:
        animation.pause()


def busy() -> bool:
    """
    Say whether any motion is still to come: a delayed step, an active
    timer or a running animation.

    Returns
    -------
    bool
        True if `settle` would run something.

    Examples
    --------
    >>> busy()
    False
    """
    return any(pending.waiting() for pending in _queue)


def settle(*, rounds: int = 1000) -> None:
    """
    Let every piece of motion happen: delayed steps run, timers fire and
    animations reach their end.

    With instant motion they happen at once, in the order they were
    asked for, and motion they start (feedback that leads to
    the next question, which slides in) happens too. In the app's real
    time this waits for them instead.

    Parameters
    ----------
    rounds : int, default 1000
        The most pieces of motion to go through or, in real time, about
        how many milliseconds to wait. Keyword-only.

    Raises
    ------
    RuntimeError
        If motion is still going after that many, such as a step that
        keeps asking for itself again.

    Examples
    --------
    >>> settle()
    >>> busy()
    False

    A step that always asks for itself again never settles:

    >>> set_instant(True)
    >>> owner = QObject()
    >>> def again():
    ...     later(10, owner=owner, step=again)
    >>> later(10, owner=owner, step=again)
    >>> settle(rounds=3)
    Traceback (most recent call last):
        ...
    RuntimeError: Motion is still going after 3 rounds.
    >>> set_instant(False)
    """
    for _ in range(rounds):
        QCoreApplication.processEvents()
        waiting = next(
            (pending for pending in _queue if pending.waiting()),
            None,
        )
        if waiting is None:
            return
        if _instant:
            waiting.run()
        else:
            time.sleep(
                0.001,
            )  # real motion takes its time: a round is about a millisecond
    if busy():
        raise RuntimeError(f"Motion is still going after {rounds} rounds.")


class _KeyPress(QObject):
    """
    With instant motion, click a button at once when its key is pressed.

    Qt shows a button that a key presses as pressed for a moment, then
    clicks it, on a timer of its own that tests cannot hold
    or settle. This filter takes its place, but only in tests: a filter
    runs for every event that reaches the button (paints,
    hovers, layout), and in the app Qt's own handling is what should
    happen anyway.

    Examples
    --------
    >>> from PySide6.QtWidgets import QPushButton
    >>> button = QPushButton("Answer")
    >>> clicks = []
    >>> _ = button.clicked.connect(
    ...     lambda: clicks.append(1)
    ... )
    >>> _KeyPress().eventFilter(
    ...     button,
    ...     QShortcutEvent(
    ...         QKeySequence("Return"), None, False
    ...     ),
    ... )
    True
    >>> clicks
    [1]
    """

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802, PLR0917 (Qt passes both arguments positionally)
        """
        Click the button whose key it is, unless the key is shared and
        Qt only moves the focus.

        Parameters
        ----------
        watched : QObject
            The button.
        event : QEvent
            The event on its way to the button.

        Returns
        -------
        bool
            True when the event was the button's key, which is handled
            here.

        Examples
        --------
        >>> from PySide6.QtWidgets import QPushButton
        >>> button = QPushButton("Answer")
        >>> _KeyPress().eventFilter(
        ...     button, QEvent(QEvent.Type.Enter)
        ... )
        False
        >>> _KeyPress().eventFilter(
        ...     button,
        ...     QShortcutEvent(
        ...         QKeySequence("Return"), None, True
        ...     ),
        ... )  # shared: Qt moves the focus
        False
        >>> button.setEnabled(False)
        >>> _KeyPress().eventFilter(
        ...     button,
        ...     QShortcutEvent(
        ...         QKeySequence("Return"), None, False
        ...     ),
        ... )  # taken, but nothing happens
        True
        """
        if event.type() != QEvent.Type.Shortcut or not isinstance(
            watched,
            QAbstractButton,
        ):
            return False
        if not isinstance(event, QShortcutEvent) or event.isAmbiguous():
            return False
        if watched.isEnabled():
            if (
                watched.isCheckable()
                and watched.focusPolicy() & Qt.FocusPolicy.ClickFocus
            ):
                watched.setFocus(Qt.FocusReason.ShortcutFocusReason)
            watched.click()
        return True


_key_press = _KeyPress()


def set_shortcut(
    button: QAbstractButton,
    *,
    key: QKeySequence | str,
) -> None:
    """
    Give a button a key that presses it. In the app Qt handles the key;
    with instant motion it clicks the button at once.

    Parameters
    ----------
    button : QAbstractButton
        The button.
    key : QKeySequence or str
        The key, such as "Return" or "Shift+C". Keyword-only.

    Examples
    --------
    >>> from PySide6.QtWidgets import QPushButton
    >>> button = QPushButton("Undo")
    >>> set_shortcut(button, key="Backspace")
    >>> button.shortcut().toString()
    'Backspace'
    >>> set_instant(True)
    >>> held = QPushButton("Answer")
    >>> set_shortcut(
    ...     held, key="Return"
    ... )  # in a test: the key clicks it at once
    >>> set_instant(False)
    """
    button.setShortcut(key)
    # only tests need it, and it would cost the app a call for every
    # event the button gets
    if _instant:
        button.installEventFilter(
            _key_press,
        )  # installing it again only moves it to the front
