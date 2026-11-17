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
        self._popup: QWidget | None = None

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
        popup = self.view().window()
        if popup is not self._popup:
            self._popup = popup
            popup.setObjectName("dropdownPopup")
            popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            popup.installEventFilter(self)
            popup.style().unpolish(popup)
            popup.style().polish(popup)
        self.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        super().showPopup()
        # Qt's combo popup can reset the list policy while opening it.
        self.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._round_popup()

    def _round_popup(self) -> None:
        """
        Clip the entire popup to the same corner radius used by the shared stylesheet.

        Examples
        --------
        >>> FieldComboBox()._round_popup()
        """
        if self._popup is None:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(self._popup.rect()), RADIUS, RADIUS)
        self._popup.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: PLR0917 (Qt passes both arguments positionally)
        """
        Keep popup clipping synchronized with layout and size changes.

        Parameters
        ----------
        watched : QObject
            The object receiving the event.
        event : QEvent
            The event being filtered.

        Returns
        -------
        bool
            Whether the superclass consumes the event.

        Examples
        --------
        >>> picker = FieldComboBox()
        >>> picker.eventFilter(picker, QEvent(QEvent.Type.None_))
        False
        """
        if watched is self._popup:
            if event.type() == QEvent.Type.Show:
                self._round_popup()
            elif event.type() == QEvent.Type.Resize:
                # Qt resets the popup mask in its resize handler, after event filters run.
                QTimer.singleShot(0, self, self._round_popup)
        return super().eventFilter(watched, event)
