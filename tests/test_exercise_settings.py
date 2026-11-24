"""
Check how saved exercise settings that are odd or out of date are read
back.
"""

from PySide6.QtCore import QByteArray

from alto import settings
from alto.ui.exercise_settings import (
    load_circle,
    load_keyboard_intervals,
)
from alto.ui.store import (
    list_value,
    store,
)


def test_saved_keyboard_intervals_with_nothing_usable_fall_back() -> None:
    """
    Check that a saved interval list with nothing valid in it practices
    the half step, rather than nothing.
    """
    store().setValue("keyboardIntervals/intervals", "0,999,x")
    load_keyboard_intervals()
    assert settings.keyboard_intervals.intervals == {1}


def test_color_scheme_saved_with_old_british_spelling_still() -> None:
    """
    Check that the checker scheme, which older versions saved as
    "chequer", is chosen again.
    """
    store().setValue("circle/scheme", "chequer")
    load_circle()
    assert settings.circle.scheme == "checker"


def test_a_saved_value_that_is_not_text_reads_as_an_empty_list() -> None:
    """
    Check that a list setting holding something other than text or a
    list, such as bytes, is treated as empty.
    """
    saved = store()
    saved.setValue("demo/clefs", QByteArray(b"treble"))
    assert list_value(saved, key="demo/clefs") == []
