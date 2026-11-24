"""
Small widgets shared by several screens: the sidebar toggle, the help
button and a segmented control.

Examples
--------
>>> SidebarToggle().toolTip()
'Hide exercise list'
"""

from __future__ import annotations

from collections.abc import (
    Callable,
    Sequence,
)

from PySide6.QtCore import (
    QPoint,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto.ui.colors import blend
from alto.ui.icons import (
    HELP,
    SIDEBAR_CLOSED,
    SIDEBAR_OPEN,
    set_svg_icon,
)
from alto.ui.zoom import px


def vertical_scroll_area(body: QWidget) -> QScrollArea:
    """
    Put a resizable widget in a frameless vertical scroll area.

    Parameters
    ----------
    body : QWidget
        Contents of the viewport.

    Returns
    -------
    QScrollArea
        The scroll area containing the body.

    Examples
    --------
    >>> body = QWidget()
    >>> scroll = vertical_scroll_area(body)
    >>> scroll.widget() is body
    True
    """
    scroll = QScrollArea()
    scroll.setWidget(body)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return scroll


def busy_progress_bar() -> QProgressBar:
    """
    Create the indeterminate progress indicator used during updates.

    Returns
    -------
    QProgressBar
        A progress bar with no percentage label.

    Examples
    --------
    >>> bar = busy_progress_bar()
    >>> (
    ...     bar.minimum(),
    ...     bar.maximum(),
    ...     bar.isTextVisible(),
    ... )
    (0, 0, False)
    """
    bar = QProgressBar()
    bar.setRange(0, 0)
    bar.setTextVisible(False)
    return bar


class PracticeCounts(QLabel):
    """
    Colored counts for calendar practice on tiles and in the exercise
    screen.

    Examples
    --------
    >>> label = PracticeCounts()
    >>> label.set_counts(
    ...     (2, 3, 1),
    ...     studying=True,
    ...     current="incorrect",
    ... )
    >>> "1 incorrect card" in label.toolTip()
    True
    """

    values: tuple[int, int, int] = (0, 0, 0)

    def set_counts(
        self,
        counts: tuple[int, int, int],
        *,
        studying: bool = False,
        current: str | None = None,
        totals: bool = False,
    ) -> None:
        """
        Show the counts in blue, red, green order and underline the
        active queue.

        Parameters
        ----------
        counts : tuple of int
            Due reviews, new cards, and outstanding incorrect cards.
        studying : bool
            Separate the exercise screen's counts with slashes.
        current : str or None
            The queue of the unanswered card, or None between cards.
        totals : bool
            Label the grid totals and show one queue per line.

        Examples
        --------
        >>> label = PracticeCounts()
        >>> label.set_counts((1, 2, 0))
        >>> label.toolTip().startswith(
        ...     "Blue — 2 new cards available"
        ... )
        True
        """
        self.values = counts
        reviews, new, incorrect = counts
        dark = (
            self.palette().color(QPalette.ColorRole.Button).lightness() < 128
        )
        green, blue, red = (
            ("#82cd93", "#89bbff", "#ff9999")
            if dark
            else ("#226939", "#215fa7", "#aa3030")
        )
        values = (
            (
                "new",
                new,
                blue,
                f"{new} new card{'' if new == 1 else 's'} available",
            ),
            (
                "incorrect",
                incorrect,
                red,
                (
                    f"{incorrect}"
                    " incorrect card"
                    f"{('' if incorrect == 1 else 's')}"
                    " awaiting a correct answer"
                ),
            ),
            (
                "review",
                reviews,
                green,
                f"{reviews} review{'' if reviews == 1 else 's'} due",
            ),
        )
        numbers, descriptions = [], []
        for (key, count, color, description), label in zip(
            values,
            ("New", "Learn", "Due"),
            strict=True,
        ):
            value = f"<u>{count}</u>" if key == current else str(count)
            if totals:
                value = f"{value} {label}"
            numbers.append(f'<b style="color:{color}">{value}</b>')
            descriptions.append(
                description + (" (current card)" if key == current else ""),
            )
        separator = " / " if studying else " &nbsp; "
        self.setText(("<br>" if totals else separator).join(numbers))
        self.setAccessibleName(
            ("Matching exercises, " if totals else "")
            + ", ".join(descriptions),
        )
        if studying:
            self.setToolTip(self.accessibleName())
        else:
            legend = zip(("Blue", "Red", "Green"), descriptions, strict=True)
            self.setToolTip(
                "\n".join(f"{color} — {text}" for color, text in legend),
            )


class SidebarToggle(QToolButton):
    """
    A button that shows or hides the exercise list.

    Connect to `clicked`; the main window decides what to show and calls
    `set_open` to match.

    Examples
    --------
    >>> button = SidebarToggle()
    >>> button.toolTip()
    'Hide exercise list'
    >>> button.set_open(False)
    >>> button.toolTip()
    'Show exercise list'
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        noun: str = "exercise list",
    ) -> None:
        """
        Create the toggle, showing the list as open.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the button.
        noun : str, default "exercise list"
            What the list is called in the tooltip: "Hide exercise
            list". Keyword-only.

        Examples
        --------
        >>> SidebarToggle().autoRaise()
        True
        >>> SidebarToggle(noun="lesson list").toolTip()
        'Hide lesson list'
        """
        super().__init__(parent)
        self.noun = noun
        self.setAutoRaise(True)
        self.setIconSize(
            QSize(px(24), px(24)),
        )  # same size as the sound and settings buttons
        self.set_open(True)

    def set_open(self, is_open: bool) -> None:
        """
        Show the icon and tooltip for the list being open or closed.

        Parameters
        ----------
        is_open : bool
            True if the exercise list is showing.

        Examples
        --------
        >>> button = SidebarToggle()
        >>> button.set_open(False)
        >>> button.toolTip()
        'Show exercise list'
        """
        set_svg_icon(self, SIDEBAR_OPEN if is_open else SIDEBAR_CLOSED)
        self.setToolTip(
            f"Hide {self.noun}" if is_open else f"Show {self.noun}",
        )
        self.setAccessibleName(
            f"Hide {self.noun}" if is_open else f"Show {self.noun}",
        )


class HelpButton(QToolButton):
    """
    A "?" button that opens a small popover with help text.

    Click anywhere else to close it.

    Examples
    --------
    >>> HelpButton(
    ...     lambda: "<b>Press the right note.</b>"
    ... ).toolTip()
    'How this exercise works'
    """

    def __init__(
        self,
        text_provider: Callable[[], str],
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Create the button.

        Parameters
        ----------
        text_provider : callable
            Called with no arguments each time the help is shown, so the
            text can follow the current settings. It returns simple
            HTML.
        parent : QWidget or None, default None
            The widget that owns the button. Keyword-only.

        Examples
        --------
        >>> calls = []
        >>> button = HelpButton(
        ...     lambda: calls.append(1) or "help"
        ... )
        >>> # the text is not asked for until the button is clicked
        >>> calls
        []
        """
        super().__init__(parent)
        # called each time, so the text can follow the current settings
        self._text = text_provider
        self.setAutoRaise(True)
        set_svg_icon(self, HELP)
        self.setIconSize(QSize(px(24), px(24)))
        self.setToolTip("How this exercise works")
        self.setAccessibleName("How this exercise works")
        self.clicked.connect(self.show_help)
        self._popup: QWidget | None = None

    def show_help(self) -> None:
        """
        Open the popover under the button, right-aligned with it.

        Examples
        --------
        >>> HelpButton(
        ...     lambda: "<b>Help</b>"
        ... ).show_help()  # doctest: +SKIP
        """
        popup = QWidget(
            self,
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint,
        )
        popup.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
        )  # lets the card's rounded corners show
        card = QFrame(popup)
        card.setObjectName("helpCard")
        label = QLabel(self._text())
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setFixedWidth(px(340))
        inner = QVBoxLayout(card)
        inner.setContentsMargins(
            16,
            14,
            16,
            14,
        )
        inner.addWidget(label)
        outer = QVBoxLayout(popup)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)
        popup.adjustSize()
        # right-aligned under the button
        below = self.mapToGlobal(
            QPoint(self.width() - popup.width(), self.height() + 4),
        )
        popup.move(max(below.x(), 8), below.y())
        popup.show()
        self._popup = popup


class SegmentedControl(QFrame):
    """
    A pill-shaped row of choices of which exactly one is chosen, like
    the switch between two views.

    Attributes
    ----------
    buttons : list of QPushButton
        One per choice, in order.
    chosen : Signal
        Emitted with the number of the choice when the learner picks
        one.

    Examples
    --------
    >>> control = SegmentedControl(
    ...     ["Exercises", "Lessons"]
    ... )
    >>> control.current()
    0
    >>> control.set_current(1)
    >>> (
    ...     control.current(),
    ...     control.buttons[1].isChecked(),
    ... )
    (1, True)
    """

    chosen = Signal(int)

    def __init__(
        self,
        labels: Sequence[str],
        *,
        icons: Sequence[str] = (),
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the control with the first choice chosen.

        Parameters
        ----------
        labels : sequence of str
            The text of each choice.
        icons : sequence of str, default ()
            The icon of each choice, as the inside of a 24 by 24 SVG;
            fewer than the labels, or none, leaves the rest without.
            Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> len(
        ...     SegmentedControl(
        ...         ["A", "B", "C"]
        ...     ).buttons
        ... )
        3
        >>> SegmentedControl(
        ...     ["A"], icons=[HELP]
        ... ).buttons[0].icon().isNull()
        False
        """
        super().__init__(parent)
        self.setObjectName("segments")
        row = QHBoxLayout(self)
        row.setContentsMargins(
            3,
            3,
            3,
            3,
        )
        row.setSpacing(2)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self.buttons: list[QPushButton] = []
        self._labels = list(labels)
        for number, label in enumerate(labels):
            button = QPushButton(label)
            button.setToolTip(label)  # still said when the text is hidden
            button.setAccessibleName(label)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setChecked(number == 0)
            if number < len(icons):
                set_svg_icon(button, icons[number], size=18)
                button.setIconSize(QSize(px(18), px(18)))
            self._group.addButton(button, number)
            button.clicked.connect(
                lambda _=False, n=number: self.chosen.emit(n),
            )
            row.addWidget(button)
            self.buttons.append(button)
        self.restyle()

    def set_compact(self, compact: bool) -> None:
        """
        Show only the icons, or the icons and the text.

        The text is still the tooltip and the name a screen reader says.

        Parameters
        ----------
        compact : bool
            True to hide the text.

        Examples
        --------
        >>> control = SegmentedControl(
        ...     ["Exercises", "Lessons"],
        ...     icons=[HELP, HELP],
        ... )
        >>> control.set_compact(True)
        >>> (
        ...     control.buttons[0].text(),
        ...     control.buttons[0].toolTip(),
        ... )
        ('', 'Exercises')
        >>> control.set_compact(False)
        >>> control.buttons[0].text()
        'Exercises'
        """
        for button, label in zip(self.buttons, self._labels, strict=True):
            button.setText("" if compact else label)

    def current(self) -> int:
        """
        Return the number of the chosen choice.

        Returns
        -------
        int
            The choice, from 0.

        Examples
        --------
        >>> SegmentedControl(["A", "B"]).current()
        0
        """
        return max(self._group.checkedId(), 0)

    def set_current(self, number: int) -> None:
        """
        Choose one, without announcing it.

        Parameters
        ----------
        number : int
            The choice, from 0.

        Examples
        --------
        >>> control = SegmentedControl(["A", "B"])
        >>> control.set_current(1)
        >>> control.current()
        1
        """
        self.buttons[number].setChecked(True)

    def restyle(self) -> None:
        """
        Style the control from the palette now in use: a rounded track
        with the chosen choice raised and tinted.

        A change of theme rebuilds the main window, so the control there
        is drawn afresh in the new colors. One that stays, as in
        the settings, is restyled by calling this.

        Examples
        --------
        >>> "segments" in SegmentedControl(
        ...     ["A", "B"]
        ... ).styleSheet()
        True
        """
        pal = self.palette()
        window, text, base, accent = (
            pal.color(role)
            for role in (
                QPalette.ColorRole.Window,
                QPalette.ColorRole.Text,
                QPalette.ColorRole.Base,
                QPalette.ColorRole.Highlight,
            )
        )
        track = blend(window, b=text, t=0.07)
        sheet = (
            "QFrame#segments { background: "
            f"{track.name()}"
            "; border-radius: 12px; }"
            "QFrame#segments QPushButton { border: 0; border-radius: 9px; "
            "padding: 6px 18px; background: transparent; }"
            "QFrame#segments QPushButton:checked { background: "
            f"{base.name()}"
            "; color: "
            f"{accent.name()}"
            "; "
            f"border: 1px solid {pal.color(QPalette.ColorRole.Mid).name()}; }}"
        )
        self.setStyleSheet(sheet)
