"""
A responsive, scrollable grid for large banks of answer buttons.

Examples
--------
>>> AnswerBank().maximumHeight()
240
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QAbstractButton,
    QFrame,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
    QWidget,
)


class AnswerBank(QScrollArea):
    """
    Wrap existing answer buttons to fit the available width and scroll long lists.

    Attributes
    ----------
    buttons : list of QAbstractButton
        The answer buttons in their display and keyboard navigation order.
    content : QWidget
        The grid's content widget.

    Examples
    --------
    >>> bank = AnswerBank()
    >>> bank.buttons
    []
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create a bank that shows at most four rows before scrolling.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the bank.

        Examples
        --------
        >>> AnswerBank().horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        True
        """
        super().__init__(parent)
        self.buttons: list[QAbstractButton] = []
        self.content = QWidget()
        self._grid = QGridLayout(self.content)
        self._grid.setContentsMargins(8, 8, 8, 8)
        self._grid.setSpacing(8)
        self.setWidget(self.content)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMaximumWidth(760)
        self.setMaximumHeight(240)
        self.setMinimumWidth(120)
        self.setAccessibleName("Interval answer buttons")

    def set_buttons(self, buttons: list[QAbstractButton]) -> None:
        """
        Display answer buttons in a stable order.

        Parameters
        ----------
        buttons : list of QAbstractButton
            The buttons to arrange. Their caller owns answer handling.

        Examples
        --------
        >>> from PySide6.QtWidgets import QPushButton
        >>> bank = AnswerBank()
        >>> bank.set_buttons([QPushButton("m3"), QPushButton("P5")])
        >>> len(bank.buttons)
        2
        """
        self.buttons = list(buttons)
        self._reflow()

    def _reflow(self) -> None:
        """
        Recompute the columns and bounded height for the current width.

        Examples
        --------
        >>> bank = AnswerBank()
        >>> bank._reflow()
        >>> bank.buttons
        []
        """
        while self._grid.count():
            self._grid.takeAt(0)
        for column in range(self._grid.columnCount()):
            self._grid.setColumnStretch(column, 0)
        if not self.buttons:
            self.content.setMinimumHeight(0)
            return
        width = max(72, *(button.sizeHint().width() for button in self.buttons))
        available = self.width() - self.verticalScrollBar().sizeHint().width() - 16
        columns = max(1, min(6, len(self.buttons), (available + 8) // (width + 8)))
        height = max(max(button.minimumHeight(), button.sizeHint().height()) for button in self.buttons)
        for index, button in enumerate(self.buttons):
            self._grid.addWidget(button, index // columns, index % columns)
        for column in range(columns):
            self._grid.setColumnStretch(column, 1)
        rows = (len(self.buttons) + columns - 1) // columns
        content_height = rows * height + max(0, rows - 1) * 8 + 16
        self.content.setMinimumHeight(content_height)
        visible_height = min(240, min(rows, 4) * height + max(0, min(rows, 4) - 1) * 8 + 16)
        if self.minimumHeight() != visible_height or self.maximumHeight() != visible_height:
            self.setFixedHeight(visible_height)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Rewrap the buttons when the exercise or settings pane changes width.

        Parameters
        ----------
        event : QResizeEvent
            The resize notification.

        Examples
        --------
        >>> bank = AnswerBank()
        >>> bank.resize(300, 200)
        >>> bank.width()
        300
        """
        super().resizeEvent(event)
        self._reflow()
