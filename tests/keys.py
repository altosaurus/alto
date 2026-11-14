"""
Helpers for tests that press keys: open an exercise with the keyboard on it, and press a key the way a person does.
"""

from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QWidget,
)

from alto.exercises.base import Exercise
from alto.ui.exercise_view import ExerciseView


def opened(
    exercise: Exercise,
    *,
    seed: int = 4,
) -> ExerciseView:
    """
    Open an exercise on a window that is shown and active, with the keyboard on it, as when it is opened for use.

    Parameters
    ----------
    exercise : Exercise
        The exercise.
    seed : int
        The random seed. Keyword-only.

    Returns
    -------
    ExerciseView
        The screen.
    """
    view = ExerciseView(exercise, rng=random.Random(seed))
    view.resize(1000, 800)
    view.show()
    view.activateWindow()
    view.setFocus()
    assert QTest.qWaitForWindowActive(view, 2000), "the window did not become active, so no key would reach it"
    return view


NAMED_KEYS = {
    "Return": Qt.Key.Key_Return,
    "Backspace": Qt.Key.Key_Backspace,
    "Up": Qt.Key.Key_Up,
    "Down": Qt.Key.Key_Down,
    "Left": Qt.Key.Key_Left,
    "Right": Qt.Key.Key_Right,
    "PgUp": Qt.Key.Key_PageUp,
    "PgDown": Qt.Key.Key_PageDown,
    "Home": Qt.Key.Key_Home,
}
BUTTON_CLICK_MS = 130  # a button that a key presses is let go after 100 ms, and only then is it clicked
MODIFIER_KEYS = {
    "Shift": Qt.KeyboardModifier.ShiftModifier,
    "Ctrl": Qt.KeyboardModifier.ControlModifier,
}


def press(
    view: QWidget,
    text: str,
) -> None:
    """
    Press a key, written as in a tooltip or a shortcut: "Return", "PgUp", "Shift+C", "3".

    Parameters
    ----------
    view : QWidget
        The window to press it in.
    text : str
        The key, with any modifiers before it, joined by "+".
    """
    *modifiers, name = text.split("+")
    key = NAMED_KEYS.get(name) or Qt.Key(ord(name.upper()))  # a letter, digit or sign is its character
    held = Qt.KeyboardModifier.NoModifier
    for modifier in modifiers:
        held |= MODIFIER_KEYS[modifier]
    QApplication.processEvents()  # widgets that were just added become visible, and so their keys live, in the event loop
    QTest.keyClick(view, key, held)
    wanted = QKeySequence(text)
    if any(b.shortcut() == wanted and b.isEnabled() and b.isVisible() for b in view.findChildren(QAbstractButton)):
        QTest.qWait(BUTTON_CLICK_MS)  # a button's shortcut presses it, and it is let go, and clicked, a moment later
