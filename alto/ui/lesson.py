"""
The lesson pages: a page that walks through one lesson step by step.

A step has some words, sometimes a sound to hear, sometimes the circle of fifths to explore, and sometimes a small task. The
tasks cannot be failed and are not recorded.

Examples
--------
>>> LessonsPage("circle-of-fifths", step=0).view.counter.text()
'Step 1 of 8'
"""

from __future__ import annotations

import random

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from alto.audio import sounds
from alto.lessons import (
    LESSONS,
    Lesson,
    Step,
    Task,
)
from alto.lessons.circle_of_fifths import summary
from alto.theory.pitch import Note
from alto.ui.reference import ExplorableCircle
from alto.ui.store import (
    int_value,
    store,
)
from alto.ui.widgets import SidebarToggle

TEXT_WIDTH = 560  # the widest a paragraph is set, in pixels, so lines stay short enough to read comfortably
CIRCLE_SIZE = 560  # the biggest the circle is in a lesson, in pixels
RIGHT = "#2e7d32"  # the green of a right answer, as everywhere in the app
GENTLE = "#b26a00"  # the amber of a hint, which is not a red mark because nothing here can be failed
GIVE_UP_AFTER = 2  # wrong answers before the answer is shown


def saved_step(lesson: Lesson) -> int:
    """
    Return the step a lesson was left at, from the saved settings.

    Parameters
    ----------
    lesson : Lesson
        The lesson.

    Returns
    -------
    int
        The step number from 0, or 0 if none is saved or it no longer exists.

    Examples
    --------
    >>> saved_step(LESSONS[0]) in range(len(LESSONS[0].steps))
    True
    """
    step = int_value(store(), key=f"lessons/{lesson.key}/step", default=0)
    return step if 0 <= step < len(lesson.steps) else 0


def save_step(
    lesson: Lesson,
    *,
    step: int,
) -> None:
    """
    Remember the step a lesson is at.

    Parameters
    ----------
    lesson : Lesson
        The lesson.
    step : int
        The step number from 0. Keyword-only.

    Examples
    --------
    >>> save_step(LESSONS[0], step=0)
    >>> saved_step(LESSONS[0])
    0
    """
    store().setValue(f"lessons/{lesson.key}/step", step)


class StepView(QWidget):
    """
    One step of a lesson: its words, a sound to hear, the circle, and a task.

    Attributes
    ----------
    step : Step
        The step.
    circle : ExplorableCircle or None
        The circle, for a step that has one.
    left_scroll : QScrollArea
        Holds the words and controls on the left, so they scroll if the window is too short for them.
    task : Task or None
        The task now being asked, for a step that has them.
    feedback : QLabel
        What is said about the last answer.
    info : QLabel
        What is said about the key last picked on the circle.
    again : QPushButton
        Asks another task; it appears once the task has been answered.
    practise : Signal
        Emitted by the Practise button on the last step.

    Examples
    --------
    >>> view = StepView(LESSONS[0].steps[1], rng=random.Random(1))
    >>> view.task is not None and len(view.choice_buttons) == 4
    True
    """

    practise = Signal()

    def __init__(
        self,
        step: Step,
        *,
        rng: random.Random | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the step and ask its first task.

        Parameters
        ----------
        step : Step
            What to show.
        rng : random.Random or None, default None
            Chooses the tasks; None for a new one. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> StepView(LESSONS[0].steps[0]).circle is not None
        True
        """
        super().__init__(parent)
        self.step = step
        self.rng = rng or random.Random()
        self.task: Task | None = None
        self.circle: ExplorableCircle | None = None
        self.choice_buttons: list[QPushButton] = []
        self._wrong = 0  # wrong answers to the task now being asked
        self._setting = False  # True while the program, not the learner, is picking a cell
        lay = QHBoxLayout(self)  # the words and the controls on the left, the circle beside them
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        lay.setSpacing(24)
        column = QWidget()  # the left side scrolls by itself if it is taller than the window, and the circle never does
        left = QVBoxLayout(column)
        left.setContentsMargins(
            0,
            0,
            8,
            0,
        )
        left.setSpacing(12)
        text = QLabel(step.text)
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setWordWrap(True)
        text.setMaximumWidth(TEXT_WIDTH)
        text.setAlignment(Qt.AlignmentFlag.AlignTop)
        text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        left.addWidget(text)
        if step.hear:
            self.hear_button = QPushButton(f"♪  {step.hear_label}")
            self.hear_button.clicked.connect(self.hear)
            row = QHBoxLayout()
            row.addWidget(self.hear_button)
            row.addStretch(1)
            left.addLayout(row)
        side = left
        self.info = QLabel()
        self.info.setTextFormat(Qt.TextFormat.RichText)
        self.info.setWordWrap(True)
        self.feedback = QLabel()
        self.feedback.setTextFormat(Qt.TextFormat.RichText)
        self.feedback.setWordWrap(True)
        self.again = QPushButton("Try another")
        self.again.clicked.connect(self.ask)
        self.again.hide()
        if step.circle != "none":
            circle = ExplorableCircle()
            circle.setMaximumSize(CIRCLE_SIZE, CIRCLE_SIZE)
            circle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            circle.set_interactive(step.circle != "rest")
            circle.picked.connect(lambda ring, place: self._picked(ring, place=place))
            self.circle = circle
        if step.circle == "walk":
            self.walk_row = QHBoxLayout()
            self.down = QPushButton("◀  Down a fifth")
            self.up = QPushButton("Up a fifth  ▶")
            self.down.clicked.connect(lambda: self.walk(-1))
            self.up.clicked.connect(lambda: self.walk(1))
            self.walk_row.addWidget(self.down)
            self.walk_row.addWidget(self.up)
            side.addLayout(self.walk_row)
        side.addWidget(self.info)
        self.task_box = QFrame()
        self.task_box.setObjectName("settingsPane")  # the same soft outline as the panes
        box = QVBoxLayout(self.task_box)
        self.prompt = QLabel()
        self.prompt.setTextFormat(Qt.TextFormat.RichText)
        self.prompt.setWordWrap(True)
        self.choices = QHBoxLayout()
        box.addWidget(self.prompt)
        box.addLayout(self.choices)
        box.addWidget(self.feedback)
        box.addWidget(self.again, alignment=Qt.AlignmentFlag.AlignLeft)
        self.task_box.setVisible(step.make_task is not None)
        side.addWidget(self.task_box)
        if step.closing:
            self.practise_button = QPushButton("Practise this in the exercise  →")
            self.practise_button.setDefault(True)
            self.practise_button.clicked.connect(self.practise)
            side.addWidget(self.practise_button, alignment=Qt.AlignmentFlag.AlignLeft)
        left.addStretch(1)
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(column)
        self.left_scroll = scroll
        lay.addWidget(scroll, 2)
        if self.circle is not None:
            lay.addWidget(self.circle, 3)  # it takes the height that is left, and is drawn as the biggest square that fits
        if step.circle == "walk" and self.circle is not None:
            self._show(self.circle, ring="outer", place=0)
        elif self.circle is not None:
            self.info.setText(self._invitation())
        if step.make_task is not None:
            self.ask()

    def _invitation(self) -> str:
        """
        Say what can be done with this step's circle, before anything is picked.

        Returns
        -------
        str
            A sentence of advice.

        Examples
        --------
        >>> StepView(LESSONS[0].steps[0])._invitation()
        'This is the circle. Each wedge is a key.'
        >>> StepView(LESSONS[0].steps[3])._invitation()
        'Click a key to see its key signature.'
        """
        if self.step.circle == "rest":
            return "This is the circle. Each wedge is a key."
        return "Click a key to see its key signature."

    def hear(self) -> None:
        """
        Play the step's notes.

        Examples
        --------
        >>> StepView(LESSONS[0].steps[1]).hear()  # nothing sounds while muted, and nothing breaks
        """
        columns = [[Note.parse(name) for name in column] for column in self.step.hear]
        sounds.play_notes(columns, gap_ms=330 if len(columns) > 4 else 650)

    def walk(self, step: int) -> None:
        """
        Move the pick one fifth round the outer ring.

        Parameters
        ----------
        step : int
            1 for a fifth up (clockwise), -1 for a fifth down.

        Examples
        --------
        >>> view = StepView(LESSONS[0].steps[2])
        >>> view.walk(1)
        >>> # noinspection PyUnresolvedReferences
        >>> view.circle.cell
        ('outer', 1)
        >>> view.walk(-1)
        >>> view.walk(-1)
        >>> # noinspection PyUnresolvedReferences
        >>> view.circle.cell
        ('outer', 11)
        """
        if self.circle is None:
            return
        now = self.circle.cell[1] if self.circle.cell is not None else 0
        self._show(self.circle, ring="outer", place=(now + step) % 12)

    def _show(
        self,
        circle: ExplorableCircle,
        *,
        ring: str,
        place: int,
    ) -> None:
        """
        Pick a cell from the program, without treating it as an answer.

        Parameters
        ----------
        circle : ExplorableCircle
            The circle.
        ring : str
            "outer" or "inner". Keyword-only.
        place : int
            The place on the circle. Keyword-only.

        Examples
        --------
        >>> view = StepView(LESSONS[0].steps[3], rng=random.Random(1))
        >>> # noinspection PyTypeChecker
        >>> view._show(view.circle, ring="outer", place=4)
        >>> # noinspection PyUnresolvedReferences
        >>> view.circle.cell, view.feedback.text() == ""
        (('outer', 4), True)
        """
        self._setting = True
        try:
            circle.select(ring, place=place)
        finally:
            self._setting = False
        self.info.setText(summary(ring, place=place))

    def ask(self) -> None:
        """
        Ask a new task, with a fresh circle and clean feedback.

        Examples
        --------
        >>> view = StepView(LESSONS[0].steps[3], rng=random.Random(1))
        >>> first = view.task
        >>> view.ask()
        >>> view.task is not None and view.again.isHidden()
        True
        """
        if self.step.make_task is None:
            return
        task = self.task = self.step.make_task(self.rng)
        self._wrong = 0
        self.prompt.setText(task.prompt)
        self.feedback.clear()
        self.again.hide()
        while self.choices.count():
            item = self.choices.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self.choice_buttons = []
        for text in task.choices:
            button = QPushButton(text)
            button.setMinimumWidth(56)
            button.clicked.connect(lambda _=False, answer=text, pressed=button: self._answered(answer, button=pressed))
            self.choices.addWidget(button)
            self.choice_buttons.append(button)
        self.choices.addStretch(1)
        if self.circle is not None:
            self._setting = True
            try:
                self.circle.clear()
            finally:
                self._setting = False
            self.info.setText(self._invitation())

    def _picked(
        self,
        ring: str,
        *,
        place: int,
    ) -> None:
        """
        Handle a cell the learner picked on the circle: answer the task, or just say what the key is.

        Parameters
        ----------
        ring : str
            "outer" or "inner"; "" when the pick was cleared.
        place : int
            The place; -1 when the pick was cleared. Keyword-only.

        Examples
        --------
        >>> view = StepView(LESSONS[0].steps[3], rng=random.Random(2))
        >>> # noinspection PyUnresolvedReferences
        >>> view.circle.select("outer", place=1)
        >>> "sharp" in view.feedback.text() or "step" in view.feedback.text()
        True
        """
        if self._setting:
            return
        if place < 0 or self.circle is None:
            self.info.setText(self._invitation())
            return
        self.info.setText(summary(ring, place=place))
        if self.task is not None and self.task.cells:
            self._answered((ring, place), button=None)

    def _answered(
        self,
        answer: tuple[str, int] | str,
        *,
        button: QPushButton | None,
    ) -> None:
        """
        Respond to an answer: praise and explain a right one, hint at a wrong one, and give the answer after two.

        Parameters
        ----------
        answer : tuple of (str, int) or str
            The cell or button.
        button : QPushButton or None
            The button that was pressed, if it was a button. Keyword-only.

        Examples
        --------
        >>> view = StepView(LESSONS[0].steps[1], rng=random.Random(1))
        >>> # noinspection PyUnresolvedReferences
        >>> view._answered(view.task.correct, button=None)
        >>> view.again.isHidden(), "Right" in view.feedback.text()
        (False, True)
        """
        task = self.task
        if task is None:
            return
        if task.check(answer):
            self.feedback.setText(f'<span style="color:{RIGHT}"><b>Right.</b></span> {task.explanation}')
            self.again.show()
            self._lock()
            if self.circle is not None and task.cells and isinstance(answer, tuple):
                self._show(self.circle, ring=answer[0], place=answer[1])
            return
        self._wrong += 1
        if button is not None:
            button.setEnabled(False)
        if self._wrong >= GIVE_UP_AFTER:
            self.feedback.setText(f'<span style="color:{GENTLE}"><b>Here it is.</b></span> {task.explanation}')
            self.again.show()
            self._lock()
            if self.circle is not None and task.cells:
                ring, place = min(task.cells)
                self._show(self.circle, ring=ring, place=place)
        else:
            self.feedback.setText(f'<span style="color:{GENTLE}"><b>Not quite.</b></span> {task.hint}')

    def _lock(self) -> None:
        """
        Switch off the answer buttons once the task is over.

        Examples
        --------
        >>> view = StepView(LESSONS[0].steps[1], rng=random.Random(1))
        >>> view._lock()
        >>> any(choice.isEnabled() for choice in view.choice_buttons)
        False
        """
        for button in self.choice_buttons:
            button.setEnabled(False)


class LessonView(QWidget):
    """
    One lesson being taken: the step, a progress bar, and Back and Next.

    Attributes
    ----------
    lesson : Lesson
        The lesson.
    current : int
        The step being shown, from 0.
    heading : QLabel
        The step's title.
    counter : QLabel
        "Step 2 of 8".
    progress : QProgressBar
        How far through the lesson.
    back_button : QPushButton
        Goes to the step before, or out to the list from the first step.
    next_button : QPushButton
        Goes to the next step, or finishes on the last one.
    leave : Signal
        Emitted to leave the lesson.
    stepped : Signal
        Emitted with the number of the step each time one is shown.
    practise : Signal
        Emitted when the last step's Practise button is pressed, with the exercise's class name.

    Examples
    --------
    >>> view = LessonView(LESSONS[0])
    >>> view.counter.text()
    'Step 1 of 8'
    >>> view.go(to=1)
    >>> view.heading.text(), view.counter.text()
    ('A fifth', 'Step 2 of 8')
    """

    leave = Signal()
    stepped = Signal(int)
    practise = Signal(str)

    def __init__(
        self,
        lesson: Lesson,
        *,
        start: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the view at a step.

        Parameters
        ----------
        lesson : Lesson
            The lesson to take.
        start : int, default 0
            The step to begin at. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> LessonView(LESSONS[0], start=3).current
        3
        """
        super().__init__(parent)
        self.lesson = lesson
        self.current = -1
        self._views: dict[int, StepView] = {}
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.heading = QLabel()
        self.heading.setStyleSheet("font-size: 18pt; font-weight: bold;")
        self.heading.setAccessibleName("Step title")
        self.counter = QLabel()
        top.addWidget(self.heading, 1)
        top.addWidget(self.counter)
        lay.addLayout(top)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(6)
        self.progress.setRange(0, len(lesson.steps))
        lay.addWidget(self.progress)
        self.pages = QStackedWidget()
        lay.addWidget(self.pages, 1)
        bottom = QHBoxLayout()
        self.back_button = QPushButton("←  Back")
        self.back_button.clicked.connect(lambda: self.go(to=self.current - 1))
        self.next_button = QPushButton("Next  →")
        self.next_button.setDefault(True)
        self.next_button.clicked.connect(lambda: self.go(to=self.current + 1))
        bottom.addWidget(self.back_button)
        bottom.addStretch(1)
        bottom.addWidget(self.next_button)
        lay.addLayout(bottom)
        self.go(to=start)

    def go(self, *, to: int) -> None:
        """
        Show a step. Going before the first leaves to the list, and going past the last finishes the lesson.

        Parameters
        ----------
        to : int
            The step to show, from 0. Keyword-only.

        Examples
        --------
        >>> view = LessonView(LESSONS[0])
        >>> view.go(to=2)
        >>> view.current
        2
        """
        steps = self.lesson.steps
        if to < 0 or to >= len(steps):
            if to >= len(steps):
                save_step(self.lesson, step=0)
            self.leave.emit()
            return
        self.current = to
        if to not in self._views:
            made = StepView(steps[to])
            made.practise.connect(lambda: self.practise.emit(self.lesson.exercise))
            self._views[to] = made
            self.pages.addWidget(made)
        self.pages.setCurrentWidget(self._views[to])
        self.heading.setText(steps[to].title)
        self.counter.setText(f"Step {to + 1} of {len(steps)}")
        self.progress.setValue(to + 1)
        self.back_button.setText("←  Lessons" if to == 0 else "←  Back")
        self.next_button.setText("Finish" if to == len(steps) - 1 else "Next  →")
        save_step(self.lesson, step=to)
        self.stepped.emit(to)


class LessonsPage(QWidget):
    """
    The page of an open lesson, with a button to leave it.

    Attributes
    ----------
    view : LessonView
        The lesson being taken.
    sidebar_button : SidebarToggle
        Shows or hides the list on the left; the main window wires it up.
    back : Signal
        Emitted to leave the lesson, to wherever it was opened from.
    practise_requested : Signal
        Emitted with the class name of an exercise to practise.

    Examples
    --------
    >>> page = LessonsPage("circle-of-fifths")
    >>> page.view.lesson.key
    'circle-of-fifths'
    """

    back = Signal()
    practise_requested = Signal(str)

    def __init__(
        self,
        key: str,
        *,
        step: int | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the page for a lesson, at the step it was left at unless another is asked for.

        Parameters
        ----------
        key : str
            The lesson's key.
        step : int or None, default None
            The step to start at; None for where it was left. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Raises
        ------
        KeyError
            If there is no lesson with that key.

        Examples
        --------
        >>> LessonsPage("circle-of-fifths", step=2).view.current
        2
        """
        super().__init__(parent)
        lesson = next((candidate for candidate in LESSONS if candidate.key == key), None)
        if lesson is None:
            raise KeyError(key)
        outer = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.sidebar_button = SidebarToggle(noun="lesson list")
        bar.addWidget(self.sidebar_button)
        self.back_button = QPushButton("←  Leave lesson")
        self.back_button.setToolTip("Leave the lesson (Esc). Alto remembers where you were.")
        self.back_button.clicked.connect(self.back)
        self.restart_button = QPushButton("Start over")
        self.restart_button.setFlat(True)
        bar.addWidget(self.back_button)
        bar.addStretch(1)
        bar.addWidget(self.restart_button)
        outer.addLayout(bar)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.back.emit)
        self.view = LessonView(lesson, start=saved_step(lesson) if step is None else step)
        self.view.leave.connect(self.back)
        self.view.practise.connect(self.practise_requested)
        self.restart_button.clicked.connect(lambda: self.view.go(to=0))
        outer.addWidget(self.view, 1)
