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

from collections.abc import (
    Iterable,
    Sequence,
)

from PySide6.QtCore import (
    QPoint,
    QRectF,
    QSize,
    QSizeF,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QPalette,
    QResizeEvent,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from alto.exercises.base import Exercise
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
from alto.ui.transitions import (
    Sprite,
    Transition,
    TransitionCanvas,
    saved_transition,
    transition_named,
)
from alto.ui.widgets import SegmentedControl

# Icon for each exercise, keyed by class name.
EXERCISE_ICONS = {
    "NoteNames": icons.EXERCISE_NOTE_NAMES,
    "KeyboardNotes": icons.EXERCISE_KEYBOARD,
    "NoteConstruction": icons.EXERCISE_CONSTRUCTION,
    "IntervalNames": icons.EXERCISE_INTERVALS,
    "KeySignatures": icons.EXERCISE_KEY_SIGNATURES,
    "KeySignatureConstruction": icons.EXERCISE_KEY_CONSTRUCTION,
    "ScaleDegrees": icons.EXERCISE_SCALES,
    "ScaleConstruction": icons.EXERCISE_SCALE_CONSTRUCTION,
    "CircleOfFifths": icons.EXERCISE_CIRCLE,
    "ChordQualities": icons.EXERCISE_CHORDS,
    "ArpeggioNames": icons.EXERCISE_ARPEGGIOS,
    "ClefBasics": icons.EXERCISE_CLEFS,
}


CARD_W, CARD_H, GAP = 190, 185, 14


class TileCard(QPushButton):
    """
    A big button: an icon on top, then a category, a name and a one-line description, and optionally a line of status.

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
        status: str = "",
        parent: QWidget | None = None,
    ) -> None:
        """
        Build a card.

        Parameters
        ----------
        icon : str
            The inside of a 24 by 24 SVG, drawn in the text colour. Keyword-only.
        category : str
            The small heading above the name. Keyword-only.
        name : str
            The name. Keyword-only.
        about : str
            A line of description, which is also the tooltip. Keyword-only.
        status : str, default ""
            A line under the description, such as how far through a lesson you are; nothing if empty. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the card. Keyword-only.

        Examples
        --------
        >>> TileCard(icon=icons.HELP, category="Help", name="Help", about="Get help.", status="Step 2 of 8").toolTip()
        'Get help.'
        """
        super().__init__(parent)
        self.setFixedSize(CARD_W, CARD_H)
        self.setToolTip(about)
        self.setAccessibleName(f"{name}, {category}")  # the card's text is in labels that a screen reader would skip
        self.setAccessibleDescription(f"{about} {status}".strip())
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            12,
            14,
            12,
            12,
        )
        lay.setSpacing(6)
        picture = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        color = self.palette().color(QPalette.ColorRole.WindowText)
        picture.setPixmap(icons.svg_icon(icon, color=color, size=56).pixmap(QSize(56, 56)))
        heading = QLabel(category.upper(), alignment=Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("color: gray; font-size: 8pt; letter-spacing: 1px;")
        title = QLabel(f"<b>{name}</b>", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)  # a long name, such as Key Signature Identification, goes on two lines
        text = QLabel(about, alignment=Qt.AlignmentFlag.AlignCenter)
        text.setWordWrap(True)
        text.setStyleSheet("color: gray; font-size: 9pt;")
        labels = [picture, heading, title, text]
        lay.addWidget(picture)
        lay.addWidget(heading)
        lay.addWidget(title)
        lay.addWidget(text, 1)
        if status:
            line = QLabel(status, alignment=Qt.AlignmentFlag.AlignCenter)
            line.setStyleSheet("font-size: 9pt; font-weight: bold;")
            lay.addWidget(line)
            labels.append(line)
        for label in labels:
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


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
        'Name the interval between two notes (up to an octave).'
        """
        super().__init__(
            icon=EXERCISE_ICONS.get(cls.__name__, icons.EXERCISE_NOTE_NAMES),
            category=cls.category,
            name=cls.name,
            about=cls.description,
            parent=parent,
        )


def lesson_card(
    lesson: Lesson,
    *,
    parent: QWidget | None = None,
) -> TileCard:
    """
    Make the card of a lesson: the icon of the exercise that practises the same topic, and how far through it you are.

    Parameters
    ----------
    lesson : Lesson
        The lesson.
    parent : QWidget or None, default None
        The widget that owns the card. Keyword-only.

    Returns
    -------
    TileCard
        The card, which says "Start" or "Continue at step N".

    Examples
    --------
    >>> card = lesson_card(LESSONS[0])
    >>> card.accessibleName()
    'The Circle of Fifths, Scales & Keys'
    """
    where = saved_step(lesson)
    return TileCard(
        icon=EXERCISE_ICONS.get(lesson.exercise, icons.EXERCISE_NOTE_NAMES),
        category=lesson.category,
        name=lesson.title,
        about=lesson.summary,
        status=f"Continue at step {where + 1}" if where else "Start",
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
    cards : list of ExerciseCard
        One per exercise, in registry order.
    lesson_cards : list of TileCard
        One per lesson, with how far through it you are.
    canvas : TransitionCanvas
        Where the transition between the exercises and the lessons is drawn.
    mode_control : SegmentedControl
        The switch between the exercises and the lessons. The main window puts it in its top bar.
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

    def __init__(
        self,
        registry: Iterable[type[Exercise]],
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the page.

        Parameters
        ----------
        registry : iterable of type of Exercise
            The exercises to show, in the order to show them.
        parent : QWidget or None, default None
            The widget that owns the page. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> len(HomePage([NoteNames]).cards)
        1
        """
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.mode_control = SegmentedControl(["Exercises", "Lessons"], icons=[icons.EXERCISES, icons.LESSONS])
        self.mode_control.chosen.connect(lambda number: self.set_mode("lessons" if number else "exercises"))
        self.cards = []
        for cls in registry:
            card = ExerciseCard(cls)
            card.clicked.connect(lambda _=False, c=cls: self.exercise_chosen.emit(c))
            self.cards.append(card)
        body = QWidget()  # scrolls when the window is shorter than all the rows
        self.rows = QVBoxLayout(body)  # one centred row of cards at a time
        self.rows.setContentsMargins(
            28,
            12,
            28,
            12,
        )
        self.rows.setSpacing(GAP)
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
        self.scroll_area = scroll
        lay.addWidget(scroll, 1)
        self.lesson_cards: list[TileCard] = []
        self._make_lesson_cards()
        self.mode = "lessons" if text_value(store(), key="ui/homeMode", default="exercises") == "lessons" else "exercises"
        self.mode_control.set_current(1 if self.mode == "lessons" else 0)
        self._reflow()

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
        changed = mode != self.mode
        transition = transition_named(saved_transition())
        self.canvas.stop()  # a transition that is still playing ends where it was going
        leaving = self._sprites(self.lesson_cards if self.mode == "lessons" else self.cards)
        self.mode = mode
        self.mode_control.set_current(1 if mode == "lessons" else 0)
        store().setValue("ui/homeMode", mode)
        playing = animate and changed and self.isVisible() and transition.frame is not None
        if playing:
            self.canvas.cover(leaving)  # the old cards stay in view while the new ones are put in place
            self._hidden.setEnabled(True)
            self._hidden.setOpacity(0.0)
        self._reflow(force=True)
        if playing:
            QTimer.singleShot(0, self, lambda: self._begin(transition, direction=1 if mode == "lessons" else -1))

    def _begin(
        self,
        transition: Transition,
        *,
        direction: int,
    ) -> None:
        """
        Start the transition, now that the new cards are in place.

        Parameters
        ----------
        transition : Transition
            Which one to play.
        direction : int
            1 when going towards the lessons, -1 when coming back. Keyword-only.

        Examples
        --------
        >>> from alto.exercises import REGISTRY
        >>> page = HomePage(REGISTRY)
        >>> page._begin(transition_named("fade"), direction=1)  # nothing is covered, so nothing plays
        >>> page.canvas.running
        False
        """
        if not self.canvas.running:
            return
        self.rows.activate()
        arriving = self._sprites(self.lesson_cards if self.mode == "lessons" else self.cards)
        self.canvas.play(transition, new=arriving, direction=direction)

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
        # Use the page's own width: the scroll area's viewport isn't resized yet when this runs.
        usable = self.width() - 56 - self.scroll_area.verticalScrollBar().sizeHint().width()
        columns = max(1, (usable + GAP) // (CARD_W + GAP))
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
        shown = self.lesson_cards if self.mode == "lessons" else self.cards
        for card in (*self.cards, *self.lesson_cards):
            card.setVisible(False)
        for start in range(0, len(shown), columns):
            row = QHBoxLayout()
            row.setSpacing(GAP)
            row.addStretch(1)
            for card in shown[start : start + columns]:
                row.addWidget(card)
            row.addStretch(1)
            self.rows.addLayout(row)
            for card in shown[start : start + columns]:  # shown only now: putting a card in the page's layout hides it first
                card.setVisible(True)
        self.rows.addStretch(1)
