"""
Scale-degree carets are visibly centered above their numbers rather than
beside them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import QRectF
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QPainter,
)

from alto import settings
from alto.ui.degree_text import (
    degree_tooltip,
    draw_degree_text,
)
from alto.ui.pictures import NamePicture
from alto.ui.settings_panel import NoteNameSettingsPanel

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


@pytest.mark.parametrize("digit", list("1234567"))
@pytest.mark.parametrize("family", ["Sans Serif", "Liberation Sans"])
def test_caret_ink_is_centered_above_digit(
    app: QApplication,
    *,
    digit: str,
    family: str,
) -> None:
    """
    Compare the rendered caret and digit bounds in fonts that misplace
    combining accents.

    Parameters
    ----------
    app : QApplication
        The shared application.
    digit : str
        The degree number. Keyword-only.
    family : str
        The text font. Keyword-only.
    """
    image = QImage(100, 90, QImage.Format.Format_RGB32)
    image.fill(QColor("white"))
    painter = QPainter(image)
    font = QFont(family)
    font.setPixelSize(40)
    painter.setFont(font)
    painter.setPen(QColor("black"))
    draw_degree_text(painter, rect=QRectF(0, 0, 100, 90), text=f"{digit}̂")
    painter.end()
    rows = [
        y
        for y in range(image.height())
        if any(
            image.pixelColor(x, y).lightness() < 128
            for x in range(image.width())
        )
    ]
    gaps = [
        index
        for index in range(1, len(rows))
        if rows[index] > rows[index - 1] + 1
    ]
    assert len(gaps) == 1, (
        "the caret must be separated from the digit by clear space"
    )
    caret_rows, digit_rows = rows[: gaps[0]], rows[gaps[0] :]
    caret_x = [
        x
        for y in caret_rows
        for x in range(image.width())
        if image.pixelColor(x, y).lightness() < 128
    ]
    digit_x = [
        x
        for y in digit_rows
        for x in range(image.width())
        if image.pixelColor(x, y).lightness() < 128
    ]
    assert (
        abs(
            (min(caret_x) + max(caret_x)) / 2
            - (min(digit_x) + max(digit_x)) / 2,
        )
        <= 1
    )
    assert max(caret_rows) < min(digit_rows)


def test_caret_tooltips_use_the_explicit_renderer(app: QApplication) -> None:
    """
    Use rendered caret examples for both the option and its summary
    picture.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    panel = NoteNameSettingsPanel(settings.note_names)
    tooltip = panel.naming_radios["degrees"].toolTip()
    assert "data:image/png;base64," in tooltip
    assert 'alt="Caret (1̂ 2̂ 3̂)"' in tooltip
    assert NamePicture("degrees").toolTip() == tooltip
    assert degree_tooltip("Letters (C D E)") == "Letters (C D E)"
    panel.close()
