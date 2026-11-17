"""
Tests for the reference pane: the circle that can be explored, and the explanation that follows the pick.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QPoint,
    Qt,
)
from PySide6.QtTest import QTest

from alto.theory.fifths import (
    MAJORS,
    SIGNATURES,
    accidentals_of,
    explain,
)
from alto.ui.reference import (
    ExplorableCircle,
    ReferencePanel,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def click(circle: ExplorableCircle, *, ring: str, place: int) -> None:
    """
    Click the middle of a cell.

    Parameters
    ----------
    circle : ExplorableCircle
        The circle to click.
    ring : str
        "outer" or "inner".
    place : int
        The place on the circle.
    """
    from_middle = 0.87 if ring == "outer" else 0.62
    center, radius = circle.geometry_of()
    angle = math.radians(30 * place)
    point = QPoint(
        round(center.x() + from_middle * radius * math.sin(angle)),
        round(center.y() - from_middle * radius * math.cos(angle)),
    )
    QTest.mouseClick(circle, Qt.MouseButton.LeftButton, pos=point)


def test_every_cell_can_be_clicked_and_lights_its_key(app: QApplication) -> None:
    """
    Check that a click on any of the 24 cells picks it, shows its signature and lights its six chords.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = ExplorableCircle()
    circle.resize(500, 500)
    for place in range(12):
        for ring in ("outer", "inner"):
            click(circle, ring=ring, place=place)
            assert circle.cell == (ring, place)
            assert circle.signature == SIGNATURES[place]
            assert len(circle.numerals) == 6 and circle.lit == {(place + step) % 12 for step in (-1, 0, 1)}


def test_a_click_in_the_middle_clears_the_pick(app: QApplication) -> None:
    """
    Check that clicking the disc in the middle goes back to nothing picked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = ExplorableCircle()
    circle.resize(500, 500)
    click(circle, ring="outer", place=3)
    center, _ = circle.geometry_of()
    QTest.mouseClick(circle, Qt.MouseButton.LeftButton, pos=QPoint(round(center.x()), round(center.y())))
    assert circle.cell is None and circle.signature is None and circle.title == "Circle of fifths"


def test_the_arrow_keys_move_the_pick_round_and_between_the_rings(app: QApplication) -> None:
    """
    Check that the arrow keys walk around the circle, switch rings and clear the pick, so no mouse is needed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = ExplorableCircle()
    circle.show()
    QTest.keyClick(circle, Qt.Key.Key_Right)
    assert circle.cell == ("outer", 0)
    QTest.keyClick(circle, Qt.Key.Key_Left)
    assert circle.cell == ("outer", 11)
    QTest.keyClick(circle, Qt.Key.Key_Down)
    assert circle.cell == ("inner", 11)
    QTest.keyClick(circle, Qt.Key.Key_Right)
    assert circle.cell == ("inner", 0)
    QTest.keyClick(circle, Qt.Key.Key_Escape)
    assert circle.cell is None


def test_the_explanation_follows_the_pick(app: QApplication) -> None:
    """
    Check that the text under the circle changes with the key, and says what to do when nothing is picked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    panel = ReferencePanel()
    assert "Pick a key" in panel.explanation.text()
    panel.circle.select("outer", place=3)
    assert "<b>A major</b>" in panel.explanation.text() and "F♯, C♯, G♯" in panel.explanation.text()
    panel.circle.select("inner", place=3)
    assert "<b>F♯ minor</b>" in panel.explanation.text()
    panel.circle.clear()
    assert "Pick a key" in panel.explanation.text()


def test_the_explanation_is_right_for_every_key() -> None:
    """
    Check that every cell's explanation names its key and counts its sharps or flats rightly.
    """
    for place, names in enumerate(MAJORS):
        text = explain("outer", place=place)
        assert f"<b>{names[0]} major</b>" in text
        assert len(accidentals_of(SIGNATURES[place])) == abs(SIGNATURES[place])
        assert (" sharp" in text.split("</p>")[0].replace("no sharps", "")) == (SIGNATURES[place] > 0)
        assert ("also be spelled" in text) == (len(names) == 2)
