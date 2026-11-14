"""
A preview of a transition for the settings.

It is a mock of the home page, with the app's own cards, that switches from the exercises to the lessons once.

Examples
--------
>>> preview = TransitionPreview()
>>> preview.show_transition("cascade")
>>> preview.transition.key
'cascade'
"""

from __future__ import annotations

from PySide6.QtCore import (
    QRectF,
    QTimer,
)
from PySide6.QtGui import (
    QPainter,
    QPaintEvent,
    QResizeEvent,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from alto.exercises import REGISTRY
from alto.lessons import LESSONS
from alto.ui import icons
from alto.ui.home import (
    CARD_H,
    CARD_W,
    EXERCISE_ICONS,
    GAP,
    ExerciseCard,
    TileCard,
    lesson_card,
)
from alto.ui.transitions import (
    DEFAULT_TRANSITION,
    Sprite,
    TransitionCanvas,
    paint_sprites,
    transition_named,
)
from alto.ui.widgets import SegmentedControl

PAUSE_MS = 600  # how long the exercises rest before the preview switches to the lessons
COLUMNS = 3  # how many cards are in a row on the preview's page
MARGIN = 14  # the space round the cards, before they are scaled down to fit
EXAMPLES = (
    ("Notation", "Reading the staff", "Where each note lives.", "NoteNames"),
    ("Intervals", "Counting intervals", "From seconds to octaves.", "IntervalNames"),
    ("Chords", "Building triads", "Stack thirds into chords.", "ChordQualities"),
)  # lessons that do not exist yet, to give the lessons side more than one card; they say so


def make_sides() -> tuple[list[TileCard], list[TileCard]]:
    """
    Make the cards for the two sides of the preview: the app's own exercise cards, and its lesson cards.

    The lessons side has the real lesson, and a few examples that are marked as such, so that a transition has more than one
    card to move.

    Returns
    -------
    tuple of (list of TileCard, list of TileCard)
        The cards of the exercises side, and of the lessons side.

    Examples
    --------
    >>> first, second = make_sides()
    >>> len(first), len(second) > len(LESSONS)
    (6, True)
    """
    exercises: list[TileCard] = [ExerciseCard(cls) for cls in REGISTRY[:6]]
    lessons: list[TileCard] = [lesson_card(lesson) for lesson in LESSONS]
    for category, name, about, exercise in EXAMPLES:
        lessons.append(
            TileCard(
                icon=EXERCISE_ICONS.get(exercise, icons.EXERCISE_NOTE_NAMES),
                category=category,
                name=name,
                about=about,
                status="Example",
            ),
        )
    return exercises, lessons


class Stage(QWidget):
    """
    The page of the mock window: it draws the cards that are resting, and the transition plays on a canvas over it.

    Attributes
    ----------
    canvas : TransitionCanvas
        Where a transition is drawn.
    resting : list of Sprite
        The cards that are showing when no transition is playing.

    Examples
    --------
    >>> Stage().resting
    []
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the stage with nothing on it.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> Stage().canvas.running
        False
        """
        super().__init__(parent)
        self.canvas = TransitionCanvas(self)
        self.resting: list[Sprite] = []

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Keep the canvas the size of the stage.

        Parameters
        ----------
        event : QResizeEvent
            The resize.

        Examples
        --------
        >>> stage = Stage()
        >>> stage.show()  # a hidden widget is only told about its size once it is shown
        >>> stage.resize(300, 200)
        >>> stage.canvas.geometry() == stage.rect()
        True
        """
        super().resizeEvent(event)
        self.canvas.setGeometry(self.rect())

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the cards at rest, unless a transition is drawing them.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request.

        Examples
        --------
        >>> stage = Stage()
        >>> stage.resize(100, 100)
        >>> stage.grab().isNull()
        False
        """
        if self.canvas.running:
            return
        painter = QPainter(self)
        paint_sprites(painter, sprites=self.resting)
        painter.end()


class TransitionPreview(QFrame):
    """
    A mock home page that plays a transition between two sets of the app's cards, once.

    It has a bar with the same Exercises and Lessons switch as the real window. It follows the side that is showing, and pressing
    it plays the transition to the other side, so the learner can try it as often as they like.

    Attributes
    ----------
    transition : Transition
        The transition being shown.
    side : int
        Which set of cards is showing: 0 for the exercises, 1 for the lessons.
    stage : Stage
        The page the cards are on.
    switch : SegmentedControl
        The mock switch in the title bar.

    Examples
    --------
    >>> preview = TransitionPreview()
    >>> preview.side
    0
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the preview, showing the default transition.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> TransitionPreview().transition.key
        'cascade'
        """
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAccessibleName("Transition preview")
        self.transition = transition_named(DEFAULT_TRANSITION)
        self.side = 0
        self._sides = make_sides()
        self.switch = SegmentedControl(["Exercises", "Lessons"], icons=[icons.EXERCISES, icons.LESSONS])
        self.switch.chosen.connect(self.go_to)  # it works: pressing a side plays the transition to it
        bar = QHBoxLayout()
        bar.setContentsMargins(
            14,
            8,
            14,
            8,
        )
        bar.addStretch(1)
        bar.addWidget(self.switch)
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setFrameShadow(QFrame.Shadow.Sunken)
        self.stage = Stage()
        self.stage.setMinimumSize(280, 220)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        lay.setSpacing(0)
        lay.addLayout(bar)
        lay.addWidget(rule)
        lay.addWidget(self.stage, 1)
        self.stage.canvas.finished.connect(self._rest)
        self._pause = QTimer(self)
        self._pause.setSingleShot(True)
        self._pause.timeout.connect(self._next)
        self.stage.resting = self._sprites(self.side)

    def _sprites(self, side: int) -> list[Sprite]:
        """
        Photograph the cards of one side, laid out in rows and scaled down to fit the stage.

        Parameters
        ----------
        side : int
            0 for the exercises, 1 for the lessons.

        Returns
        -------
        list of Sprite
            A sprite for each card, as it rests.

        Examples
        --------
        >>> preview = TransitionPreview()
        >>> len(preview._sprites(0)), len(preview._sprites(1)) > 1
        (6, True)
        """
        cards = self._sides[side]
        most = max(len(self._sides[0]), len(self._sides[1]))  # both sides are scaled alike, so they sit on the same grid
        rows = -(-most // COLUMNS)
        wide = COLUMNS * CARD_W + (COLUMNS - 1) * GAP + 2 * MARGIN
        high = rows * CARD_H + (rows - 1) * GAP + 2 * MARGIN
        scale = max(min(self.stage.width() / wide, self.stage.height() / high, 1.0), 0.2)
        top = (self.stage.height() - high * scale) / 2 + MARGIN * scale
        sprites = []
        for number, card in enumerate(cards):
            row, column = divmod(number, COLUMNS)
            in_row = min(COLUMNS, len(cards) - row * COLUMNS)
            row_wide = in_row * CARD_W + (in_row - 1) * GAP
            left = (self.stage.width() - row_wide * scale) / 2 + column * (CARD_W + GAP) * scale
            sprites.append(
                Sprite(
                    pixmap=card.grab(),
                    rect=QRectF(left, top + row * (CARD_H + GAP) * scale, CARD_W * scale, CARD_H * scale),
                ),
            )
        return sprites

    def show_transition(self, key: str) -> None:
        """
        Show a transition: the exercises appear, and after a moment they change to the lessons, once.

        Parameters
        ----------
        key : str
            The transition's key.

        Examples
        --------
        >>> preview = TransitionPreview()
        >>> preview.show_transition("flip")
        >>> preview.transition.key
        'flip'
        """
        self.transition = transition_named(key)
        self._pause.stop()
        self.stage.canvas.stop()
        self.side = 0
        self.switch.set_current(0)
        self.stage.resting = self._sprites(0)
        self.stage.update()
        self._pause.start(PAUSE_MS)

    def replay(self) -> None:
        """
        Play the transition that is showing again, from the exercises.

        Examples
        --------
        >>> preview = TransitionPreview()
        >>> preview.replay()
        >>> preview.transition.key
        'cascade'
        """
        self.show_transition(self.transition.key)

    def _next(self) -> None:
        """
        Switch to the lessons, with the transition, as the preview does by itself after it is shown.

        Examples
        --------
        >>> preview = TransitionPreview()
        >>> preview._next()
        >>> preview.side
        1
        """
        self.go_to(1)

    def go_to(self, side: int) -> None:
        """
        Switch to one side with the transition, as the switch does in the real window.

        A transition that is still playing ends first. Nothing happens if that side is already showing.

        Parameters
        ----------
        side : int
            0 for the exercises, 1 for the lessons.

        Examples
        --------
        >>> preview = TransitionPreview()
        >>> preview.go_to(1)
        >>> preview.side, preview.switch.current()
        (1, 1)
        >>> preview.go_to(0)
        >>> preview.side
        0
        """
        self._pause.stop()  # the preview no longer switches by itself: the learner is in charge
        self.stage.canvas.stop()
        self.switch.set_current(self.side)
        if side == self.side:
            return
        leaving = self._sprites(self.side)
        self.side = side
        self.switch.set_current(side)
        arriving = self._sprites(side)
        self.stage.resting = arriving
        if self.transition.frame is None:
            self.stage.update()
            return
        self.stage.canvas.cover(leaving)
        self.stage.canvas.play(self.transition, new=arriving, direction=1 if side == 1 else -1)

    def _rest(self) -> None:
        """
        Draw the new cards as they rest once the transition has finished. Nothing follows: it plays once.

        Examples
        --------
        >>> preview = TransitionPreview()
        >>> preview._rest()
        """
        self.stage.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Lay the cards out again for the new size, unless a transition is playing.

        Parameters
        ----------
        event : QResizeEvent
            The resize.

        Examples
        --------
        >>> preview = TransitionPreview()
        >>> preview.resize(700, 500)
        >>> preview.stage.resting[0].rect.width() <= CARD_W
        True
        """
        super().resizeEvent(event)
        if not self.stage.canvas.running:
            self.stage.resting = self._sprites(self.side)
