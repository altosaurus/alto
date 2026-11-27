"""
Helpers for tests that press keys: open an exercise with the keyboard on
it, and press a key the way a person does.
"""

from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
)

from alto.exercises.base import Exercise
from alto.ui.exercise_page import ExercisePage


def opened(
    exercise: Exercise,
    *,
    seed: int = 4,
) -> ExercisePage:
    """
    Open an exercise on a window that is shown and active, with the
    keyboard on it, as when it is opened for use.

    Parameters
    ----------
    exercise : Exercise
        The exercise.
    seed : int
        The random seed. Keyword-only.

    Returns
    -------
    ExercisePage
        The screen.
    """
    view = ExercisePage(exercise, rng=random.Random(seed))
    view.resize(1000, 800)
    view.show()
    view.activateWindow()
    view.setFocus()
    assert QTest.qWaitForWindowActive(view, 2000), (
        "the window did not become active, so no key would reach it"
    )
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
MODIFIER_KEYS = {
    "Shift": Qt.KeyboardModifier.ShiftModifier,
    "Ctrl": Qt.KeyboardModifier.ControlModifier,
}


def press(
    view: QWidget,
    text: str,
) -> None:
    """
    Press a key, written as in a tooltip or a shortcut: "Return",
    "PgUp", "Shift+C", "3".

    Parameters
    ----------
    view : QWidget
        The window to press it in.
    text : str
        The key, with any modifiers before it, joined by "+".
    """
    *modifiers, name = text.split("+")
    key = NAMED_KEYS.get(name) or Qt.Key(
        ord(name.upper()),
    )  # a letter, digit or sign is its character
    held = Qt.KeyboardModifier.NoModifier
    for modifier in modifiers:
        held |= MODIFIER_KEYS[modifier]
    # widgets that were just added become visible, and so their keys
    # live, in the event loop
    QApplication.processEvents()
    QTest.keyClick(
        view,
        key,
        held,
        # a button whose key it is clicks at once: tests do not wait for
        # its
        # pressed look
    )
