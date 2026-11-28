"""A pane that slides open beside an exercise from its toolbar."""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLayout,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto.ui.zoom import px

SLIDE_MS = 220
INNER_MARGIN = 9


class SidePane(QFrame):
    """
    Hold a panel beside the exercise and slide it open or closed.

    The toolbar button that controls the pane stays in step with it:
    checking the button opens the pane, and the pane's collapse button
    unchecks it.

    Attributes
    ----------
    open_width : int
        Width of the open pane at 100% zoom, in pixels.
    collapse_button : QToolButton
        Closes the pane from its top corner.
    animation : QPropertyAnimation
        Slides the pane's maximum width between closed and open.

    Examples
    --------
    >>> from PySide6.QtWidgets import QLabel
    >>> toggle = QToolButton()
    >>> toggle.setCheckable(True)
    >>> pane = SidePane(
    ...     QLabel("Settings"),
    ...     open_width=290,
    ...     toggle=toggle,
    ...     label="Collapse exercise settings",
    ... )
    >>> pane.set_open(True)
    >>> pane.isHidden(), pane.maximumWidth() == px(290)
    (False, True)
    """

    def __init__(
        self,
        content: QWidget,
        *,
        open_width: int,
        toggle: QToolButton,
        label: str,
    ) -> None:
        """
        Place the content below a collapse button and start closed.

        Parameters
        ----------
        content : QWidget
            Panel shown in the pane. It fills the height of the pane, so
            a long page can scroll.
        open_width : int
            Width of the open pane at 100% zoom, in pixels.
        toggle : QToolButton
            Checkable toolbar button that opens and closes the pane.
        label : str
            Tooltip and accessible name of the collapse button.

        Examples
        --------
        The pane starts hidden at zero width, so it takes no space and
        cannot be tabbed into.
        """
        super().__init__()
        self.open_width = open_width
        self.setObjectName("settingsPane")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(0)
        self.setMaximumWidth(0)
        layout = QVBoxLayout(self)
        # Let the pane shrink to zero while it animates.
        layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        header = QHBoxLayout()
        header.addStretch()
        self.collapse_button = QToolButton()
        self.collapse_button.setText("−")
        self.collapse_button.setAutoRaise(True)
        self.collapse_button.setToolTip(label)
        self.collapse_button.setAccessibleName(label)
        self.collapse_button.clicked.connect(lambda: toggle.setChecked(False))
        header.addWidget(self.collapse_button)
        layout.addLayout(header)
        content.setFixedWidth(px(open_width - 2 * INNER_MARGIN))
        layout.addWidget(content, 1)
        self.hide()
        self.animation = QPropertyAnimation(self, b"maximumWidth", self)
        self.animation.setDuration(SLIDE_MS)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self._settled)
        toggle.toggled.connect(self.slide)

    def slide(self, open_: bool) -> None:
        """
        Animate the pane open or closed from its current width.

        Parameters
        ----------
        open_ : bool
            Whether the pane ends open.

        Examples
        --------
        >>> from PySide6.QtWidgets import QLabel
        >>> pane = SidePane(
        ...     QLabel(),
        ...     open_width=290,
        ...     toggle=QToolButton(),
        ...     label="Collapse",
        ... )
        >>> pane.slide(True)
        >>> pane.animation.endValue() == px(290)
        True
        """
        self.animation.stop()
        self.show()
        self.animation.setStartValue(self.maximumWidth())
        self.animation.setEndValue(px(self.open_width) if open_ else 0)
        self.animation.start()

    def set_open(self, open_: bool) -> None:
        """
        Open or close the pane at once, without the slide.

        Parameters
        ----------
        open_ : bool
            Whether the pane is open.

        Examples
        --------
        >>> from PySide6.QtWidgets import QLabel
        >>> pane = SidePane(
        ...     QLabel(),
        ...     open_width=290,
        ...     toggle=QToolButton(),
        ...     label="Collapse",
        ... )
        >>> pane.set_open(False)
        >>> pane.isHidden(), pane.maximumWidth()
        (True, 0)
        """
        self.animation.stop()
        self.setMaximumWidth(px(self.open_width) if open_ else 0)
        self.setVisible(open_)

    def _settled(self) -> None:
        """
        Hide the pane when it finishes closing.

        Examples
        --------
        A closed pane takes no space and cannot be tabbed into.
        """
        if self.maximumWidth() == 0:
            self.hide()
