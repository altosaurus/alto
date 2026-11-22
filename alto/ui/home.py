"""
The start screen: a card for every exercise, or for every lesson, in rows.

A switch at the top chooses between the exercises and the lessons.

Examples
--------
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> len(page.cards) == len(REGISTRY)
True
"""

from __future__ import annotations

import time
from collections.abc import (
    Iterable,
    Sequence,
)
from functools import partial

from PySide6.QtCore import (
    QAbstractAnimation,
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPoint,
    QRectF,
    QSignalBlocker,
    QSize,
    QSizeF,
    Qt,
    QTimer,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QResizeEvent,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from alto.exercises.base import REGISTRY, Exercise
from alto.learning import Learner
from alto.learning.calendar import CALENDAR_SCHEDULERS, DEFAULT_SCHEDULER
from alto.lessons import (
    LESSONS,
    Lesson,
)
from alto.ui import icons
from alto.ui.lesson import saved_step
from alto.ui.store import (
    store,
    text_value,
)
from alto.ui.style import (
    RADIUS,
    navigation_heading_style,
)
from alto.ui.transitions import (
    SIDEBAR_SLIDE_MS,
    Sprite,
    TransitionCanvas,
    saved_transition,
    transition_named,
)
from alto.ui.widgets import PracticeCounts, SegmentedControl
from alto.ui.zoom import css, px

# Icon for each exercise, keyed by class name.
EXERCISE_ICONS = {
    "NotationIdentification": icons.EXERCISE_NOTATION_IDENTIFICATION,
    "NoteNames": icons.EXERCISE_NOTE_NAMES,
    "KeyboardNotes": icons.EXERCISE_KEYBOARD,
    "NoteConstruction": icons.EXERCISE_CONSTRUCTION,
    "IntervalConstruction": icons.EXERCISE_INTERVAL_CONSTRUCTION,
    "IntervalNames": icons.EXERCISE_INTERVALS,
    "KeyboardIntervals": icons.EXERCISE_KEYBOARD_INTERVALS,
    "OrderOfKeys": icons.EXERCISE_ORDER_OF_KEYS,
    "KeySignatures": icons.EXERCISE_KEY_SIGNATURES,
    "KeySignatureConstruction": icons.EXERCISE_KEY_CONSTRUCTION,
    "ScaleIdentification": icons.EXERCISE_SCALES,
    "ScaleConstruction": icons.EXERCISE_SCALE_CONSTRUCTION,
    "CircleOfFifths": icons.EXERCISE_CIRCLE,
    "ChordQualities": icons.EXERCISE_CHORDS,
    "ArpeggioNames": icons.EXERCISE_ARPEGGIOS,
    "ClefBasics": icons.EXERCISE_CLEFS,
}


CARD_W, CARD_H, GAP = 190, 185, 14
FILTER_INDENT = 16


class _FilterLabelDelegate(QStyledItemDelegate):
    """
    Indent filter checkboxes and labels while Qt draws the tree branches in the trailing column.

    Examples
    --------
    >>> isinstance(_FilterLabelDelegate(), QStyledItemDelegate)
    True
    """

    def initStyleOption(  # noqa: PLR0917 (Qt passes both arguments positionally)
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """
        Inset the label and its checkbox hit area according to the item's depth.

        Parameters
        ----------
        option : QStyleOptionViewItem
            Style settings for this cell.
        index : QModelIndex or QPersistentModelIndex
            Root, category, or individual tile.

        Examples
        --------
        A tile is indented two levels beneath All categories.
        """
        super().initStyleOption(option, index)
        depth = int(index.parent().isValid()) + int(index.parent().parent().isValid())
        option.rect.adjust(depth * FILTER_INDENT, 0, 0, 0)


def category_tree(name: str) -> QTreeWidget:
    """
    Build a navigation tree with themed checkboxes and right-aligned expansion arrows.

    Parameters
    ----------
    name : str
        Accessible name of the tree.

    Returns
    -------
    QTreeWidget
        Empty tree ready for categories and exercises.

    Examples
    --------
    >>> category_tree("Decks").columnCount()
    2
    """
    tree = QTreeWidget()
    tree.setObjectName("tileFilterTree")
    tree.setAccessibleName(name)
    tree.setIconSize(QSize(px(icons.ACTIVITY_ICON_SIZE), px(icons.ACTIVITY_ICON_SIZE)))
    tree.setHeaderHidden(True)
    tree.setColumnCount(2)
    tree.setTreePosition(1)
    tree.header().setStretchLastSection(False)
    tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
    tree.setColumnWidth(1, 2 * FILTER_INDENT)
    tree.setItemDelegateForColumn(0, _FilterLabelDelegate(tree))
    tree.setFrameShape(QFrame.Shape.NoFrame)
    tree.setUniformRowHeights(True)
    tree.setIndentation(FILTER_INDENT)
    return tree


class _ProgressBar(QWidget):
    """
    A flat strip along the bottom edge of a card that fills from the left, in the palette's accent over a faint track.

    The strip is cut to the card's rounded bottom corners, so it lies flush with the edge instead of floating above it.

    Attributes
    ----------
    fraction : float
        How much of the strip is filled, from 0 to 1.

    Examples
    --------
    >>> bar = _ProgressBar(fraction=0.5, card_height=185, radius=9)
    >>> bar.fraction
    0.5
    """

    def __init__(
        self,
        *,
        fraction: float,
        card_height: int,
        radius: int,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build a strip.

        Parameters
        ----------
        fraction : float
            How much of the strip is filled, from 0 to 1. Keyword-only.
        card_height : int
            The height of the card inside its outline, in pixels; the strip is cut to the card's outline over this height.
            Keyword-only.
        radius : int
            The radius of the card's corners inside its outline, in pixels. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the strip. Keyword-only.

        Examples
        --------
        >>> _ProgressBar(fraction=0.25, card_height=185, radius=9).fraction
        0.25
        """
        super().__init__(parent)
        self.fraction = min(max(fraction, 0.0), 1.0)
        self.card_height = card_height
        self.radius = radius
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw the track and the filled part, cut to the card's bottom corners.

        Parameters
        ----------
        event : QPaintEvent
            The paint request from Qt; the whole strip is always redrawn.

        Examples
        --------
        >>> _ProgressBar(fraction=0.5, card_height=185, radius=9).grab().isNull()
        False
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        area = QRectF(self.rect())
        card = QPainterPath()
        card.addRoundedRect(
            QRectF(0.0, area.height() - self.card_height, area.width(), self.card_height),
            self.radius,
            self.radius,
        )
        painter.setClipPath(card)
        palette = self.palette()
        track = QColor(palette.color(QPalette.ColorRole.WindowText))
        track.setAlpha(45)
        painter.fillRect(area, track)
        if self.fraction > 0:
            painter.fillRect(
                QRectF(0.0, 0.0, area.width() * self.fraction, area.height()),
                palette.color(QPalette.ColorRole.Highlight),
            )
        painter.end()


class TileCard(QPushButton):
    """
    A big button: an icon on top, then a category, a name and a short description, and optionally a lesson's progress.

    Progress takes no room in the layout: a strip along the bottom edge shows it, and "Step N/M" sits in the top-right
    corner, both only once the lesson has been begun. A card with or without progress therefore has the same size and the
    same icon.

    Examples
    --------
    >>> card = TileCard(icon=icons.EXERCISE_CIRCLE, category="Scales & Keys", name="Circle of Fifths", about="Find keys.")
    >>> (card.width(), card.height()) == (CARD_W, CARD_H)
    True
    >>> card.accessibleName()
    'Circle of Fifths, Scales & Keys'
    """

    def __init__(
        self,
        *,
        icon: str,
        category: str,
        name: str,
        about: str,
        progress: tuple[int, int] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build a card.

        Parameters
        ----------
        icon : str
            The inside of a 24 by 24 SVG, drawn in the text color. Keyword-only.
        category : str
            The small heading above the name. Keyword-only.
        name : str
            The name. Keyword-only.
        about : str
            A line of description, which is also the tooltip. Keyword-only.
        progress : tuple of int or None, default None
            The step you are on, counting from 0, and how many steps there are. The bar and "Step N/M" appear only once the first
            step has been passed; nothing is drawn if None or at step 0. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the card. Keyword-only.

        Examples
        --------
        >>> card = TileCard(icon=icons.HELP, category="Help", name="Help", about="Get help.", progress=(1, 8))
        >>> card.toolTip(), card.accessibleDescription()
        ('Get help.', 'Get help. Continue at step 2 of 8.')
        """
        super().__init__(parent)
        self.category = category
        self.title = name
        self.icon_svg = icon
        self.setFixedSize(px(CARD_W), px(CARD_H))
        self.setToolTip(about)
        self.setAccessibleName(f"{name}, {category}")  # the card's text is in labels that a screen reader would skip
        where = f" Continue at step {progress[0] + 1} of {progress[1]}." if progress and progress[0] else ""
        self.setAccessibleDescription(f"{about}{where}".strip())
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            12,
            14,
            12,
            12,
        )
        lay.setSpacing(6)
        self.picture = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.picture.setMinimumHeight(px(56))  # the icon is never squeezed by the text under it
        self._refresh_icon()
        heading = QLabel(category.upper(), alignment=Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet(css("color: gray; font-size: 8pt; letter-spacing: 1px;"))
        title = QLabel(f"<b>{name}</b>", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)  # a long name, such as Key Signature Identification, goes on two lines
        text = QLabel(about, alignment=Qt.AlignmentFlag.AlignCenter)
        text.setWordWrap(True)
        text.setStyleSheet(css("color: gray; font-size: 9pt;"))
        labels = [self.picture, heading, title, text]
        lay.addWidget(self.picture)
        lay.addWidget(heading)
        lay.addWidget(title)
        lay.addWidget(text, 1)
        self.progress_bar: _ProgressBar | None = None
        self.step_label: QLabel | None = None
        if progress and progress[0]:
            step, steps = progress
            edge, height = px(1), px(5)  # inside the one-pixel outline, along the bottom of the card
            self.progress_bar = _ProgressBar(
                fraction=step / steps,
                card_height=px(CARD_H) - 2 * edge,
                radius=px(RADIUS) - edge,
                parent=self,
            )
            self.progress_bar.setGeometry(edge, px(CARD_H) - edge - height, px(CARD_W) - 2 * edge, height)
            self.step_label = QLabel(f"Step {step + 1}/{steps}", self)
            self.step_label.setStyleSheet(css("color: palette(highlight); font-size: 8pt; font-weight: bold;"))
            self.step_label.adjustSize()
            self.step_label.move(px(CARD_W) - self.step_label.width() - px(10), px(7))
            labels.append(self.step_label)
        for label in labels:
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _refresh_icon(self) -> None:
        """
        Draw the tile icon in the current text color.

        Examples
        --------
        >>> card = lesson_card(LESSONS[0])
        >>> card._refresh_icon()
        >>> card.picture.pixmap().isNull()
        False
        """
        color = self.palette().color(QPalette.ColorRole.WindowText)
        self.picture.setPixmap(icons.svg_icon(self.icon_svg, color=color, size=56).pixmap(QSize(px(56), px(56))))

    def changeEvent(self, event: QEvent) -> None:
        """
        Recolor the icon when the tile receives a new palette.

        Parameters
        ----------
        event : QEvent
            The widget change delivered by Qt.

        Examples
        --------
        >>> card = lesson_card(LESSONS[0])
        >>> card.changeEvent(QEvent(QEvent.Type.PaletteChange))
        """
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange:
            self._refresh_icon()


def exercise_icon(name: str) -> str:
    """
    Find the icon for an exercise: the one its plugin supplies, or Alto's own.

    Parameters
    ----------
    name : str
        The exercise's class name.

    Returns
    -------
    str
        SVG shapes with COLOR where the theme's ink goes.

    Examples
    --------
    >>> exercise_icon("NoteNames") == icons.EXERCISE_NOTE_NAMES
    True
    >>> exercise_icon("pack.nothing.here") == icons.EXERCISE_NOTE_NAMES
    True
    """
    found = next((cls for cls in REGISTRY if cls.__name__ == name), None)
    return (found.icon if found else "") or EXERCISE_ICONS.get(name, icons.EXERCISE_NOTE_NAMES)


def lesson_icon(lesson: Lesson) -> str:
    """
    Find the icon for a lesson's tile: its own if a plugin gave it one, otherwise its primary exercise's.

    Parameters
    ----------
    lesson : Lesson
        The lesson.

    Returns
    -------
    str
        SVG shapes with COLOR where the theme's ink goes.

    Examples
    --------
    >>> lesson_icon(LESSONS[0]) == exercise_icon(LESSONS[0].exercise)
    True
    """
    return lesson.icon or exercise_icon(lesson.exercise)


class ExerciseCard(TileCard):
    """
    The card of an exercise: its icon on top, then its category, name and a one-line description.

    Examples
    --------
    >>> from alto.exercises.library import NoteNames
    >>> card = ExerciseCard(NoteNames)
    >>> card.toolTip() == NoteNames.description
    True
    >>> (card.width(), card.height()) == (CARD_W, CARD_H)
    True
    """

    def __init__(
        self,
        cls: type[Exercise],
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the card for one exercise.

        Parameters
        ----------
        cls : type of Exercise
            The exercise class; its name, category and description are shown, and its class name picks the icon.
        parent : QWidget or None, default None
            The widget that owns the card. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import IntervalNames
        >>> ExerciseCard(IntervalNames).toolTip()
        'Name the interval between two notes.'
        """
        super().__init__(
            icon=exercise_icon(cls.__name__),
            category=cls.category,
            name=cls.name,
            about=cls.description,
            parent=parent,
        )

        self.exercise_class = cls
        self.counts = PracticeCounts(self)
        self.counts.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.counts.hide()

    def set_counts(self, counts: tuple[int, int] | tuple[int, int, int] | None) -> None:
        """
        Show due reviews, new cards, and outstanding incorrect cards in the upper right corner.

        Parameters
        ----------
        counts : tuple of int or None
            Reviews due, new cards available, and optionally the outstanding incorrect count. None hides the counts.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> card = ExerciseCard(NoteNames)
        >>> card.set_counts((2, 3, 1))
        >>> print(card.counts.toolTip())
        Blue — 3 new cards available
        Red — 1 incorrect card awaiting a correct answer
        Green — 2 reviews due
        """
        if counts is None:
            self.counts.hide()
            self.setAccessibleDescription(self.exercise_class.description)
            return
        reviews, new = counts[:2]
        incorrect = counts[2] if len(counts) == 3 else 0
        self.counts.set_counts((reviews, new, incorrect))
        self.setAccessibleDescription(f"{self.exercise_class.description} {self.counts.accessibleName()}")
        self.counts.adjustSize()
        self.counts.move(self.width() - self.counts.width() - 8, 3)
        self.counts.show()


def lesson_card(
    lesson: Lesson,
    *,
    parent: QWidget | None = None,
) -> TileCard:
    """
    Make the card of a lesson: the icon of the exercise that practices the same topic, and a bar for how far through it you are.

    Parameters
    ----------
    lesson : Lesson
        The lesson.
    parent : QWidget or None, default None
        The widget that owns the card. Keyword-only.

    Returns
    -------
    TileCard
        The card, with a progress bar and "Step N/M" in its corner once the lesson has been begun.

    Examples
    --------
    >>> card = lesson_card(LESSONS[0])
    >>> card.accessibleName()
    'Pitches and Notes, Notation'
    """
    return TileCard(
        icon=lesson_icon(lesson),
        category=lesson.category,
        name=lesson.title,
        about=lesson.summary,
        progress=(saved_step(lesson), len(lesson.steps)),
        parent=parent,
    )


class HomePage(QWidget):
    """
    The start screen: a row of exercise buttons for each category.

    Attributes
    ----------
    exercise_chosen : Signal
        Emitted with the `Exercise` class when a card is clicked.
    lesson_chosen : Signal
        Emitted with a lesson's key when its card is clicked.
    filters_changed : Signal
        Emitted after a change to the search, tile selection or displayed section.
    cards : list of ExerciseCard
        One per exercise, in registry order.
    lesson_cards : list of TileCard
        One per lesson, with how far through it you are.
    canvas : TransitionCanvas
        Where the transition between the exercises and the lessons is drawn.
    mode_control : SegmentedControl
        The switch between the exercises and the lessons. The main window puts it in its top bar.
    resume_button : QPushButton
        Returns to the retained activity. The main window places it beside search and shows it on tiles after an activity begins.
    category_filter : QToolButton
        Shows or hides the filter sidebar from the right end of the search row.
    no_results : QLabel
        Shown when no tiles match the search.
    mode : str
        "exercises" or "lessons": which cards are showing.
    scroll_area : QScrollArea
        Scrolls the rows when the window is shorter than all of them.

    Examples
    --------
    >>> from alto.exercises import REGISTRY
    >>> page = HomePage(REGISTRY)
    >>> chosen = []
    >>> _ = page.exercise_chosen.connect(chosen.append)
    >>> page.cards[0].click()
    >>> chosen == [REGISTRY[0]]
    True
    """

    exercise_chosen = Signal(object)  # the Exercise class
    lesson_chosen = Signal(str)  # a lesson's key
    filters_changed = Signal()

    def __init__(
        self,
        registry: Iterable[type[Exercise]],
        *,
        parent: QWidget | None = None,
        learner: Learner | None = None,
        filter_layout: QHBoxLayout | None = None,
    ) -> None:
        """
        Build the page.

        Parameters
        ----------
        registry : iterable of type of Exercise
            The exercises to show, in the order to show them.
        parent : QWidget or None, default None
            The widget that owns the page. Keyword-only.

        learner : Learner or None
            Profile supplying the exercise tile counts.
        filter_layout : QHBoxLayout or None
            Shared workspace layout for the filter sidebar. A standalone page places it beside its tiles.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> len(HomePage([NoteNames]).cards)
        1
        """
        super().__init__(parent)
        self.learner = learner
        self._count_timer = QTimer(self)
        self._count_timer.setInterval(30000)
        self._count_timer.timeout.connect(self.refresh_counts)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.mode_control = SegmentedControl(["Exercises", "Lessons"], icons=[icons.EXERCISES, icons.LESSONS])
        self.mode_control.chosen.connect(lambda number: self.set_mode("lessons" if number else "exercises"))
        self.resume_button = QPushButton()
        self.resume_button.hide()
        lay.addWidget(self.resume_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.tile_filters: dict[str, frozenset[str]] = {}
        self._filter_leaves: dict[str, QTreeWidgetItem] = {}
        self._filter_groups: list[QTreeWidgetItem] = []
        self.category_filter = QToolButton(self)
        self.category_filter.setAutoRaise(True)
        self.category_filter.setIconSize(QSize(px(20), px(20)))
        self.category_filter.setMinimumSize(px(32), px(32))
        self.category_filter.setCheckable(True)
        self.filter_sidebar = QFrame()
        self.filter_sidebar.setObjectName("settingsPane")
        sidebar_layout = QVBoxLayout(self.filter_sidebar)
        header = QHBoxLayout()
        header.addWidget(QLabel("Filters"), 1)
        collapse = QToolButton()
        collapse.setText("−")
        collapse.setAutoRaise(True)
        collapse.setToolTip("Collapse filters")
        collapse.setAccessibleName("Collapse filters")
        collapse.clicked.connect(lambda: self.category_filter.setChecked(False))
        header.addWidget(collapse)
        sidebar_layout.addLayout(header)
        self.category_tree = category_tree("Filter by category")
        sidebar_layout.addWidget(self.category_tree, 1)
        self.category_tree.itemChanged.connect(self._selection_changed)
        self.category_filter.toggled.connect(self._toggle_filter_sidebar)
        self._filter_slide = QVariantAnimation(self)
        self._filter_slide.setDuration(SIDEBAR_SLIDE_MS)
        self._filter_slide.setStartValue(0.0)
        self._filter_slide.setEndValue(1.0)
        self._filter_slide.valueChanged.connect(self._size_filter)
        self._filter_slide.finished.connect(
            lambda: self.filter_sidebar.setVisible(self.category_filter.isChecked() and not self.category_filter.isHidden()),
        )
        self.filter_sidebar.setFixedWidth(0)
        self.filter_sidebar.hide()
        lay.addWidget(self.category_filter, alignment=Qt.AlignmentFlag.AlignRight)
        self.queue_totals = PracticeCounts()
        self.queue_totals.setContentsMargins(12, 12, 0, 0)
        self.queue_totals.hide()
        self._query = ""
        self.no_results = QLabel()
        self.no_results.hide()
        self.cards = []
        for cls in registry:
            card = ExerciseCard(cls)
            card.clicked.connect(lambda _=False, c=cls: self.exercise_chosen.emit(c))
            self.cards.append(card)
        body = QWidget()  # scrolls when the window is shorter than all the rows
        self.rows = QVBoxLayout(body)  # one centered row of cards at a time
        self.rows.setContentsMargins(
            28,
            12,
            28,
            12,
        )
        self.rows.setSpacing(px(GAP))
        self._columns = 0
        scroll = QScrollArea()
        scroll.setWidget(body)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)
        body.setAutoFillBackground(False)
        self._hidden = QGraphicsOpacityEffect(body)  # hides the real cards while a transition plays over them
        self._hidden.setEnabled(False)
        body.setGraphicsEffect(self._hidden)
        self.canvas = TransitionCanvas(scroll.viewport())  # where the transition is drawn
        self.canvas.finished.connect(lambda: self._hidden.setEnabled(False))
        self._transition_start = QTimer(self)
        self._transition_start.setSingleShot(True)
        self._transition_start.timeout.connect(self._begin)
        self.canvas.finished.connect(self._transition_start.stop)
        self.scroll_area = scroll
        grid = QHBoxLayout()
        grid.setSpacing(0)
        grid.addWidget(self.queue_totals, alignment=Qt.AlignmentFlag.AlignTop)
        tiles = QVBoxLayout()
        tiles.addWidget(self.no_results, alignment=Qt.AlignmentFlag.AlignCenter)
        tiles.addWidget(scroll, 1)
        grid.addLayout(tiles, 1)
        (filter_layout if filter_layout is not None else grid).addWidget(self.filter_sidebar)
        lay.addLayout(grid, 1)
        self.lesson_cards: list[TileCard] = []
        self._make_lesson_cards()
        self.mode = "lessons" if text_value(store(), key="ui/homeMode", default="exercises") == "lessons" else "exercises"
        filter_host = self.filter_sidebar.parentWidget()
        assert filter_host is not None
        self._filter_host = filter_host
        self._update_categories()
        self._filter_host.installEventFilter(self)
        self.mode_control.set_current(1 if self.mode == "lessons" else 0)
        self._reflow()

    def set_search(
        self,
        text: str,
    ) -> None:
        """
        Show only tiles matching a title, description or category search.

        Parameters
        ----------
        text : str
            Case-insensitive search text. Empty text shows every tile in the selected category.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page.set_search("keyboard")
        >>> page._query
        'keyboard'
        """
        self._query = text.strip().casefold()
        self._filter_tiles()

    def _filter_tiles(self) -> None:
        """
        Apply the text and category filters immediately, including during a transition.

        Examples
        --------
        >>> page = HomePage([])
        >>> page._filter_tiles()
        """
        self.canvas.stop()
        self._hidden.setEnabled(False)
        self._reflow(force=True)
        self.filters_changed.emit()

    def matches_filter(self, card: TileCard, *, section: str) -> bool:
        """
        Check whether a tile matches the search text and the selection for its section.

        Parameters
        ----------
        card : TileCard
            Exercise or lesson tile to check.
        section : str
            Section containing the tile, either "exercises" or "lessons".

        Returns
        -------
        bool
            True if both filters include the tile.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> page = HomePage([NoteNames])
        >>> page.matches_filter(page.cards[0], section="exercises")
        True
        """
        selected = self.tile_filters.get(section)
        searchable_text = f"{card.accessibleName()} {card.toolTip()}".casefold()
        return (selected is None or card.title in selected) and self._query in searchable_text

    def _update_categories(self) -> None:
        """
        Build a checkable tree of categories and tiles for the current section.

        Examples
        --------
        >>> page = HomePage([])
        >>> page.category_tree.topLevelItem(0).text(0)
        'All categories'
        """
        tree = self.category_tree
        cards = self.lesson_cards if self.mode == "lessons" else self.cards
        selected = self.tile_filters.get(self.mode)
        heading_font, heading_ink = navigation_heading_style(self.window().palette())
        drawings = []
        with QSignalBlocker(tree):
            self._filter_leaves.clear()
            self._filter_groups.clear()
            tree.clear()
            root = self._filter_root = QTreeWidgetItem(tree, ["All categories"])
            root.setFont(0, heading_font)
            root.setForeground(0, heading_ink)
            root.setFlags(root.flags() | Qt.ItemFlag.ItemIsAutoTristate)
            root.setCheckState(0, Qt.CheckState.Checked)
            for category in dict.fromkeys(card.category for card in cards):
                group = QTreeWidgetItem(root, [category])
                group.setFont(0, heading_font)
                group.setForeground(0, heading_ink)
                self._filter_groups.append(group)
                group.setFlags(group.flags() | Qt.ItemFlag.ItemIsAutoTristate)
                for card in cards:
                    if card.category == category:
                        leaf = QTreeWidgetItem(group, [card.title])
                        drawings.append((card.icon_svg, partial(leaf.setIcon, 0)))
                        leaf.setToolTip(0, card.title)
                        self._filter_leaves[card.title] = leaf
                        checked = selected is None or card.title in selected
                        leaf.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            icons.set_item_icons(tree, drawings)
            tree.expandAll()
            tree.setCurrentItem(root)
        layout = self.filter_sidebar.layout()
        assert layout is not None
        margins = layout.contentsMargins()
        self._filter_width = (
            tree.sizeHintForColumn(0)
            + 2 * FILTER_INDENT
            + tree.columnWidth(1)
            + tree.verticalScrollBar().sizeHint().width()
            + margins.left()
            + margins.right()
            + 2 * self.filter_sidebar.frameWidth()
        )
        self._update_filter_icon()
        self._size_filter()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: PLR0917 (Qt passes both arguments positionally)
        """
        Fit the open filter sidebar when its workspace changes width.

        Parameters
        ----------
        watched : QObject
            Widget containing the activity and sidebar.
        event : QEvent
            Event delivered to the widget.

        Returns
        -------
        bool
            Whether the base widget consumes the event.

        Examples
        --------
        Dragging the navigation divider resizes the space available for the filters.
        """
        if event.type() == QEvent.Type.Resize and watched is self._filter_host:
            self._size_filter()
        return super().eventFilter(watched, event)

    def _size_filter(self) -> None:
        """
        Size the sliding sidebar while leaving room beside it for the activity.

        Examples
        --------
        A narrow window reserves at least one tile's width for the grid.
        """
        available = self._filter_host.width() - px(CARD_W) - px(56) - self.scroll_area.verticalScrollBar().sizeHint().width()
        if not self.queue_totals.isHidden() and self.isVisible():
            available -= self.queue_totals.sizeHint().width()
        width = min(self._filter_width, max(120, available))
        self.filter_sidebar.setFixedWidth(round(width * self._filter_slide.currentValue()))
        if self._filter_host is self:
            self._reflow()

    def set_filter_available(self, available: bool) -> None:
        """
        Show the filter control on browsing and exercise pages, remembering the sidebar's open state.

        Parameters
        ----------
        available : bool
            Whether the current page supports filtering.

        Examples
        --------
        >>> page = HomePage([])
        >>> page.set_filter_available(False)
        >>> page.category_filter.isHidden()
        True
        """
        self.category_filter.setVisible(available)
        open_or_sliding = self.category_filter.isChecked() or self._filter_slide.state() == QAbstractAnimation.State.Running
        self.filter_sidebar.setVisible(available and open_or_sliding)

    def _toggle_filter_sidebar(self, expanded: bool) -> None:
        """
        Show or hide the filter sidebar and fit the tiles into the remaining space.

        Parameters
        ----------
        expanded : bool
            Whether the sidebar should be open.

        Examples
        --------
        >>> page = HomePage([])
        >>> page.category_filter.click()
        >>> page.filter_sidebar.isHidden()
        False
        """
        if expanded:
            self.filter_sidebar.setVisible(not self.category_filter.isHidden())
            self.category_tree.expandAll()
            self.category_tree.setFocus()
        else:
            self.category_filter.setFocus()
        self._update_filter_icon()
        direction = QAbstractAnimation.Direction.Forward if expanded else QAbstractAnimation.Direction.Backward
        self._filter_slide.setDirection(direction)
        if self._filter_slide.state() != QAbstractAnimation.State.Running:
            self._filter_slide.start()

    def _selection_changed(self) -> None:
        """
        Apply the checked leaves when Qt updates the tree.

        Examples
        --------
        Checking a category updates all of its tiles together.
        """
        selected = frozenset(name for name, leaf in self._filter_leaves.items() if leaf.checkState(0) == Qt.CheckState.Checked)
        if self.tile_filters.get(self.mode) == selected:
            return
        self.tile_filters[self.mode] = selected
        self._update_filter_icon()
        self._filter_tiles()

    def _update_filter_icon(self) -> None:
        """
        Show how many tiles are checked and highlight the funnel for a partial or empty selection.

        Examples
        --------
        >>> HomePage([])._update_filter_icon()
        """
        total = len(self._filter_leaves)
        selected = self.tile_filters.get(self.mode)
        count = total if selected is None else len(selected)
        label = "All categories" if count == total else f"{count} of {total} {self.mode} selected"
        verb = "Hide" if self.category_filter.isChecked() else "Show"
        self.category_filter.setToolTip(f"{verb} filters ({label})")
        self.category_filter.setAccessibleName(f"{verb} filters")
        self.category_filter.setAccessibleDescription(label)
        role = QPalette.ColorRole.Highlight if count != total else QPalette.ColorRole.WindowText
        icons.set_svg_icon(self.category_filter, icons.FILTER, role=role)

    def restore_tile_filters(self, selections: dict[str, frozenset[str]], *, expanded: bool | None = None) -> None:
        """
        Restore exercise and lesson checkboxes after a theme change.

        Parameters
        ----------
        selections : dict of str to frozenset of str
            Checked tile titles for each section with a saved filter.
        expanded : bool or None
            Restore the sidebar at its open or closed width immediately. None keeps its current state.

        Examples
        --------
        >>> HomePage([]).restore_tile_filters({})
        """
        self.tile_filters = selections.copy()
        self._update_categories()
        if expanded is not None:
            self.category_filter.setChecked(expanded)
            self._filter_slide.setCurrentTime(self._filter_slide.duration() if expanded else 0)
        self._filter_tiles()

    def set_category(self, category: str | None) -> None:
        """
        Select the tiles of one category, or all tiles when the category is absent.

        Parameters
        ----------
        category : str or None
            Case-folded category name, or None for all tiles.

        Examples
        --------
        >>> HomePage([]).set_category(None)
        """
        cards = self.lesson_cards if self.mode == "lessons" else self.cards
        selected = frozenset(card.title for card in cards if card.category.casefold() == category)
        if selected:
            self.tile_filters[self.mode] = selected
        else:
            self.tile_filters.pop(self.mode, None)
        self._update_categories()
        self._filter_tiles()

    def _make_lesson_cards(self) -> None:
        """
        Make a card for each lesson, saying how far through it you are. Cards from before are thrown away.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> len(page.lesson_cards) == len(LESSONS)
        True
        """
        from_before = self.lesson_cards
        self.lesson_cards = []
        for old in from_before:
            old.hide()
            old.deleteLater()
        for lesson in LESSONS:
            card = lesson_card(lesson, parent=self)
            card.clicked.connect(lambda _=False, key=lesson.key: self.lesson_chosen.emit(key))
            self.lesson_cards.append(card)

    def set_mode(
        self,
        mode: str,
        *,
        animate: bool = True,
    ) -> None:
        """
        Show the exercises or the lessons, and remember which.

        The cards change with the transition that is chosen in the settings. The new cards are in place at once, so nothing
        waits on it.

        Parameters
        ----------
        mode : str
            "exercises" or "lessons".
        animate : bool, default True
            Play the chosen transition; if False the new cards simply appear. Keyword-only.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page.set_mode("lessons")
        >>> page.mode, page.mode_control.current()
        ('lessons', 1)
        >>> page.set_mode("exercises")
        """
        mode = "lessons" if mode == "lessons" else "exercises"
        if animate and mode != self.mode:
            self._prepare_transition(self.lesson_cards if self.mode == "lessons" else self.cards)
        else:
            self.canvas.stop()
        if self.mode != mode:
            if mode not in self.tile_filters and self._filter_root.checkState(0) == Qt.CheckState.PartiallyChecked:
                groups = self._filter_groups
                if all(group.checkState(0) != Qt.CheckState.PartiallyChecked for group in groups):
                    categories = {group.text(0).casefold() for group in groups if group.checkState(0) == Qt.CheckState.Checked}
                    cards = self.lesson_cards if mode == "lessons" else self.cards
                    selected = frozenset(card.title for card in cards if card.category.casefold() in categories)
                    if selected:
                        self.tile_filters[mode] = selected
            self.mode = mode
            self._update_categories()
        self.refresh_counts()
        self.mode_control.set_current(1 if mode == "lessons" else 0)
        store().setValue("ui/homeMode", mode)
        self._reflow(force=True)
        self.filters_changed.emit()

    def page_changed(self) -> None:
        """
        Animate the tiles from an empty grid on return, or stop the animation when leaving.

        Examples
        --------
        >>> page = HomePage([])
        >>> page.page_changed()
        >>> page.canvas.running
        False
        """
        self._prepare_transition(())

    def _prepare_transition(self, leaving: Sequence[TileCard]) -> None:
        """
        Cover the live tiles until Qt has laid out the arriving cards.

        Parameters
        ----------
        leaving : sequence of TileCard
            Tiles to draw in the opening frame. An empty sequence starts with a blank grid.

        Examples
        --------
        >>> page = HomePage([])
        >>> page._prepare_transition(page.cards)
        """
        self.canvas.stop()
        if self.isVisible():
            self._transition = transition_named(saved_transition())
            if self._transition.frame is not None:
                self.canvas.cover(self._sprites(leaving))
                self._hidden.setOpacity(0.0)
                self._hidden.setEnabled(True)
                self._transition_start.start(0)

    def _begin(self) -> None:
        """
        Start the transition, now that the new cards are in place.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page._begin()  # nothing is covered, so nothing plays
        >>> page.canvas.running
        False
        """
        if not self.canvas.running:
            return
        self.rows.activate()
        self.canvas.setGeometry(self.scroll_area.viewport().rect())
        arriving = self._sprites(self.lesson_cards if self.mode == "lessons" else self.cards)
        self.canvas.play(self._transition, new=arriving, direction=1 if self.mode == "lessons" else -1)

    def _sprites(self, cards: Sequence[TileCard]) -> list[Sprite]:
        """
        Photograph the cards that are showing, for a transition.

        Parameters
        ----------
        cards : list of TileCard
            The cards of one side.

        Returns
        -------
        list of Sprite
            A sprite for each card that is visible, in order, placed where the card is on the page.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page._sprites(page.cards)  # nothing is visible until the page is shown
        []
        """
        viewport = self.scroll_area.viewport()
        return [
            Sprite(pixmap=card.grab(), rect=QRectF(card.mapTo(viewport, QPoint(0, 0)), QSizeF(card.size())))
            for card in cards
            if card.isVisible()
        ]

    def refresh_counts(self) -> None:
        """
        Refresh each exercise tile and the totals for the current filters.

        Examples
        --------
        >>> HomePage([]).refresh_counts()
        """
        mode = self.learner.mode if self.learner else DEFAULT_SCHEDULER
        show_totals = self.mode == "exercises" and mode in CALENDAR_SCHEDULERS
        self.queue_totals.setVisible(show_totals)
        if not self.isVisible() or self.mode != "exercises":
            self._count_timer.stop()
            return
        now = time.time()
        for card in self.cards:
            counts = None
            if self.learner and show_totals:
                counts = self.learner.calendar.tile_counts(
                    card.exercise_class(),
                    profile=self.learner.profile.id,
                    mode=mode,
                    now=now,
                )
            card.set_counts(counts)
        if show_totals:
            self._count_timer.start()
        else:
            self._count_timer.stop()
        self._reflow()

    def showEvent(self, event: QShowEvent) -> None:
        """
        Bring the lesson cards up to date each time the page is shown, so they say where each lesson was left.

        Parameters
        ----------
        event : QShowEvent
            The show.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page.show()
        """
        super().showEvent(event)
        self.refresh_counts()
        self._make_lesson_cards()
        self._reflow(force=True)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Lay the cards out again when the page changes size.

        Parameters
        ----------
        event : QResizeEvent
            The resize that happened.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page.show()
        >>> page.resize(1000, 600)
        >>> page._columns >= 1
        True
        """
        super().resizeEvent(event)
        self._reflow()

    def _reflow(self, *, force: bool = False) -> None:
        """
        Arrange the cards in rows of as many as fit across the page.

        Nothing changes if the number of columns is the same as before, unless `force` says the cards have changed.

        Parameters
        ----------
        force : bool, default False
            Lay out again even if the number of columns is the same. Keyword-only.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page.show()  # a hidden widget is only told about its size when it is shown
        >>> page.resize(2000, 600)
        >>> wide = page._columns
        >>> page.resize(500, 600)
        >>> page._columns < wide
        True
        """
        shown = self.lesson_cards if self.mode == "lessons" else self.cards
        shown = [card for card in shown if self.matches_filter(card, section=self.mode)]
        # Use the page's own width: the scroll area's viewport isn't resized yet when this runs.
        usable = self.width() - 56 - self.scroll_area.verticalScrollBar().sizeHint().width()
        if not self.queue_totals.isHidden():
            due = new = learn = 0
            for card in shown:
                if isinstance(card, ExerciseCard):
                    reviews, unseen, incorrect = card.counts.values
                    due += reviews
                    new += unseen
                    learn += incorrect
            self.queue_totals.set_counts((due, new, learn), totals=True)
            usable -= self.queue_totals.sizeHint().width()
        if self.filter_sidebar.parentWidget() is self and not self.filter_sidebar.isHidden():
            usable -= self.filter_sidebar.width()
        columns = max(1, (usable + px(GAP)) // (px(CARD_W) + px(GAP)))
        if columns == self._columns and not force:
            return
        self._columns = columns
        while self.rows.count():  # take the old rows apart, keeping the cards
            item = self.rows.takeAt(0)
            old_row = item.layout() if item is not None else None
            if old_row is not None:
                while old_row.count():
                    old_row.takeAt(0)
                old_row.deleteLater()
        section = "lessons" if self.mode == "lessons" else "exercises"
        self.no_results.setText(f"No {section} found.")
        self.no_results.setVisible(not shown)
        for card in (*self.cards, *self.lesson_cards):
            card.setVisible(False)
        for start in range(0, len(shown), columns):
            row = QHBoxLayout()
            row.setSpacing(px(GAP))
            row.addStretch(1)
            for card in shown[start : start + columns]:
                row.addWidget(card)
            row.addStretch(1)
            self.rows.addLayout(row)
            for card in shown[start : start + columns]:  # shown only now: putting a card in the page's layout hides it first
                card.setVisible(True)
        self.rows.addStretch(1)
