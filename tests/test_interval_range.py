"""
Mouse and keyboard interaction with the two-handle interval slider.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import (
    QPoint,
    Qt,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from alto.ui.interval_range import IntervalRangeSlider


@pytest.mark.parametrize("rtl", [False, True])
def test_dragging_either_handle_changes_only_its_endpoint(
    app: QApplication,
    rtl: bool,
) -> None:
    """
    Drag each handle in both layout directions without crossing
    endpoints or changing on a right click.

    Parameters
    ----------
    app : QApplication
        The shared application.
    rtl : bool
        Whether the slider uses a right-to-left layout.
    """
    slider = IntervalRangeSlider()
    slider.resize(300, 36)
    slider.setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
        if rtl
        else Qt.LayoutDirection.LeftToRight,
    )
    slider.set_range(3, high=12, maximum=24)
    slider.show()
    app.processEvents()
    QTest.mousePress(
        slider,
        Qt.MouseButton.LeftButton,
        pos=QPoint(round(slider._position(3)), 18),
    )
    QTest.mouseMove(slider, QPoint(round(slider._position(7)), 18))
    QTest.mouseRelease(
        slider,
        Qt.MouseButton.LeftButton,
        pos=QPoint(round(slider._position(7)), 18),
    )
    assert (slider.low, slider.high) == (7, 12)
    QTest.mousePress(
        slider,
        Qt.MouseButton.LeftButton,
        pos=QPoint(round(slider._position(12)), 18),
    )
    QTest.mouseMove(slider, QPoint(round(slider._position(24)), 18))
    QTest.mouseRelease(
        slider,
        Qt.MouseButton.LeftButton,
        pos=QPoint(round(slider._position(24)), 18),
    )
    assert (slider.low, slider.high) == (7, 24)
    QTest.mouseClick(
        slider,
        Qt.MouseButton.RightButton,
        pos=QPoint(round(slider._position(1)), 18),
    )
    assert (slider.low, slider.high) == (7, 24)
    assert not slider.grab().isNull()
    slider.close()


def test_keyboard_adjustments_empty_selection_and_single_interval_limits(
    app: QApplication,
) -> None:
    """
    Navigate both handles, recover an empty selection, and clamp
    movement to a single available interval.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    slider = IntervalRangeSlider()
    slider.show()
    app.processEvents()
    QTest.keyClick(slider, Qt.Key.Key_Up)
    QTest.keyClick(slider, Qt.Key.Key_Right)
    assert slider.high == 13
    QTest.keyClick(slider, Qt.Key.Key_End)
    assert slider.high == 24
    QTest.keyClick(slider, Qt.Key.Key_Down)
    QTest.keyClick(slider, Qt.Key.Key_Right)
    assert slider.low == 2
    QTest.keyClick(slider, Qt.Key.Key_Home)
    assert slider.low == 1
    slider.set_range(1, high=1, maximum=1, active=False)
    slider.move_endpoint("high", delta=1)
    assert slider.active and slider.low == slider.high == 1
    QTest.keyClick(slider, Qt.Key.Key_Left)
    QTest.keyClick(slider, Qt.Key.Key_End)
    assert slider.low == slider.high == 1
    slider.close()
