"""
Shared dropdown fields with rounded popup windows.

Examples
--------
>>> FieldComboBox().property("field")
True
"""

from __future__ import annotations

from PySide6.QtCore import (
    QEvent,
    QObject,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QPainterPath,
    QRegion,
)
from PySide6.QtWidgets import (
    QComboBox,
    QWidget,
)

from alto.ui.style import RADIUS


class FieldComboBox(QComboBox):
    """
    A shared dropdown whose field and popup both use Alto's rounded styling.

    Examples
    --------
    >>> picker = FieldComboBox()
    >>> picker.addItems(["m2", "M2", "m3"])
    >>> picker.currentText()
    'm2'
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create a themed dropdown and prepare to clip its popup corners.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the dropdown.

        Examples
        --------
        >>> FieldComboBox().maxVisibleItems()
        12
        """
        super().__init__(parent)
        self.setProperty("field", True)
        self.setMaxVisibleItems(12)

    def showPopup(self) -> None:
        """
        Open the dropdown with a rounded outer window, including its native container.

        Examples
        --------
        >>> picker = FieldComboBox()
        >>> picker.addItems(["P4", "P5"])
        >>> picker.showPopup()
        >>> picker.view().window().mask().isEmpty()
        False
        >>> picker.hidePopup()
        """
        style_combo_popup(self)
        super().showPopup()


def style_combo_popup(combo: QComboBox) -> None:
    """
    Apply the shared field and popup styling to a dropdown, including one created by Qt.

    Parameters
    ----------
    combo : QComboBox
        Field whose item view and outer popup should follow the application theme.
    """
    if not combo.property("field"):
        combo.setProperty("field", True)
        combo.style().unpolish(combo)
        combo.style().polish(combo)
    view = combo.view()
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    popup = view.window()
    if popup.objectName() != "dropdownPopup":
        popup.setObjectName("dropdownPopup")
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        popup.installEventFilter(_PopupCorners(popup))
        popup.style().unpolish(popup)
        popup.style().polish(popup)


class _PopupCorners(QObject):
    """Keep the outer dropdown window clipped when Qt opens or resizes it."""

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: PLR0917 (Qt passes both arguments positionally)
        """
        Reapply the rounded mask after Qt finishes sizing the popup.

        Returns
        -------
        bool
            Whether the superclass consumes the event.
        """
        if isinstance(watched, QWidget) and event.type() in (QEvent.Type.Show, QEvent.Type.Resize):

            def round_corners() -> None:
                """Clip the popup at its current size."""
                path = QPainterPath()
                path.addRoundedRect(QRectF(watched.rect()), RADIUS, RADIUS)
                watched.setMask(QRegion(path.toFillPolygon().toPolygon()))

            round_corners()
            QTimer.singleShot(0, watched, round_corners)
        return super().eventFilter(watched, event)
