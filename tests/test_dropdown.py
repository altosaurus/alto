"""
Rounded popup windows for shared dropdown fields.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import (
    QColor,
    QPalette,
)
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
)

from alto.ui.dropdown import FieldComboBox
from alto.ui.style import app_style


@pytest.mark.parametrize("dark", [False, True])
def test_popup_corners_are_clipped_after_opening_resizing_and_scrolling(
    app: QApplication,
    dark: bool,
) -> None:
    """
    Round the outer popup window in light and dark palettes while
    preserving scrolling and the field value.

    Parameters
    ----------
    app : QApplication
        The shared application.
    dark : bool
        Whether to use a dark palette.
    """
    host = QWidget()
    palette = host.palette()
    palette.setColor(
        QPalette.ColorRole.Base,
        QColor("#202124" if dark else "#ffffff"),
    )
    palette.setColor(
        QPalette.ColorRole.Text,
        QColor("#f5f5f5" if dark else "#202124"),
    )
    host.setPalette(palette)
    host.setStyleSheet(app_style(palette))
    picker = FieldComboBox()
    picker.setMaxVisibleItems(12)
    picker.addItems([str(number) for number in range(87)])
    layout = QVBoxLayout(host)
    layout.addWidget(picker)
    host.show()
    app.processEvents()
    picker.showPopup()
    app.processEvents()
    popup = picker.view().window()
    assert popup.isVisible() and popup.objectName() == "dropdownPopup"
    assert picker.view().verticalScrollBar().isVisible()
    assert picker.view().verticalScrollBar().maximum() > 0
    assert picker.property("field")
    assert not popup.mask().isEmpty()
    assert not popup.mask().contains(QPoint(0, 0))
    assert not popup.mask().contains(
        QPoint(popup.width() - 1, popup.height() - 1),
    )
    assert popup.mask().contains(popup.rect().center())
    popup.resize(popup.width() + 10, popup.height() + 10)
    app.processEvents()
    assert popup.mask().boundingRect() == popup.rect()
    assert not popup.mask().contains(
        QPoint(popup.width() - 1, popup.height() - 1),
    )
    picker.view().scrollToBottom()
    assert picker.view().verticalScrollBar().value() > 0
    assert picker.currentText() == "0"
    picker.hidePopup()
    picker.clear()
    picker.addItems(["m2", "M2"])
    picker.showPopup()
    app.processEvents()
    assert not picker.view().verticalScrollBar().isVisible()
    picker.hidePopup()
    host.close()
