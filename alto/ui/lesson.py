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
    QResizeEvent,
    QShortcut,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
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
from alto.exercises import REGISTRY
from alto.lessons import (
    LESSONS,
    Lesson,
    Staff,
    Step,
    Task,
)
from alto.lessons.circle_of_fifths import summary
from alto.theory.pitch import Note
from alto.ui.keyboard import KeyboardWidget
from alto.ui.reference import ExplorableCircle
from alto.ui.scale_explorer import ScaleExplorer
from alto.ui.staff import StaffWidget
from alto.ui.staff_playback import StaffPlayback
from alto.ui.store import (
    int_value,
    store,
)

TEXT_WIDTH = 560  # the widest a paragraph is set, in pixels, so lines stay short enough to read comfortably
CIRCLE_SIZE = 560  # the biggest the circle is in a lesson, in pixels
LESSON_SPREAD_WIDTH = 760  # minimum lesson pane width for side-by-side reading and music
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


class _IllustratedStep(QWidget):
    """An explanation with its captioned examples and playback, arranged for the available lesson width."""

    def __init__(
        self,
        text: QLabel,
        *,
        staves: list[StaffWidget],
        keyboard: KeyboardWidget | None,
        playback: QPushButton | None,
    ) -> None:
        """
        Group the illustrations and their playback button in one framed panel.

        Parameters
        ----------
        text : QLabel
            Lesson prose, with each paragraph marked in HTML.
        staves : list of StaffWidget
            Captioned staff illustrations in reading order.
        keyboard : KeyboardWidget or None
            Keyboard to show for a pitch example.
        playback : QPushButton or None
            Play the pitches shown in this example.
        """
        super().__init__()
        self.setMinimumWidth(1)
        self.setMaximumWidth(980)
        self.prose = text
        self.full_text = text.text()
        opening, end, rest = self.full_text.partition("</p>")
        self.opening = opening + end
        self.rest = QLabel(rest)
        self.rest.setTextFormat(Qt.TextFormat.RichText)
        self.rest.setWordWrap(True)
        self.rest.setMaximumWidth(TEXT_WIDTH)
        self.rest.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(24)
        self.grid.setVerticalSpacing(12)
        self.grid.addWidget(self.prose, 0, 0, Qt.AlignmentFlag.AlignTop)
        self.grid.addWidget(self.rest, 2, 0, Qt.AlignmentFlag.AlignTop)

        self.panel = QFrame()
        self.panel.setObjectName("lessonExample")
        self.panel.setProperty("staffPaper", bool(staves))
        group = QVBoxLayout(self.panel)
        group.setContentsMargins(12, 9, 12, 9)
        group.setSpacing(8)
        self.staves = staves
        self.gallery = QGridLayout()
        self.gallery.setContentsMargins(0, 0, 0, 0)
        self.gallery.setHorizontalSpacing(6)
        self.gallery.setVerticalSpacing(8)
        self.dividers = []
        if staves:
            group.addLayout(self.gallery)
            for _ in staves[1:]:
                divider = QFrame(self.panel)
                divider.setObjectName("lessonExampleDivider")
                divider.setFixedWidth(1)
                self.dividers.append(divider)
        if keyboard is not None:
            keyboard.setMaximumWidth(300)
            group.addWidget(keyboard)
        if playback is not None:
            group.addWidget(playback, alignment=Qt.AlignmentFlag.AlignLeft)
        self.keyboard = keyboard
        self.wide: bool | None = None
        self.columns = 0
        self.arrange()

    def arrange(self) -> None:
        """Fit the examples in reading order and place the panel beside or within the text."""
        wide = self.width() >= LESSON_SPREAD_WIDTH
        budget = (self.width() - 24) * 10 // 21 if wide else self.width()
        if wide != self.wide:
            self.wide = wide
            self.prose.setText(self.full_text if wide else self.opening)
            self.rest.setVisible(bool(self.rest.text()) and not wide)
            self.grid.setAlignment(Qt.AlignmentFlag.AlignTop if wide else Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.grid.setColumnStretch(0, 11 if wide else 1)
            self.grid.setColumnStretch(1, 10 if wide else 0)
            self.grid.addWidget(
                self.panel,
                0 if wide else 1,
                1 if wide else 0,
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            )

        widths = [staff.maximumWidth() for staff in self.staves]
        gutter = 2 * self.gallery.horizontalSpacing() + 1
        columns = len(widths)
        while columns:
            content_width = sum(max(widths[i::columns]) for i in range(columns)) + (columns - 1) * gutter
            if columns == 1 or content_width + 26 <= budget:
                break
            columns -= 1
        if columns != self.columns:
            self.columns = columns
            for index, staff in enumerate(self.staves):
                row, col = divmod(index, columns)
                self.gallery.addWidget(staff, row, 2 * col, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                if index:
                    divider = self.dividers[index - 1]
                    if col:
                        self.gallery.addWidget(divider, row, 2 * col - 1)
                    else:
                        self.gallery.removeWidget(divider)
                    divider.setVisible(bool(col))
        if self.keyboard is not None:
            self.panel.setFixedWidth(min(326, max(1, budget)))
        else:
            self.panel.setMaximumWidth(max(1, budget))
        self.grid.invalidate()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Reflow the existing controls without interrupting playback or clearing answers.

        Parameters
        ----------
        event : QResizeEvent
            New and previous widget sizes.
        """
        super().resizeEvent(event)
        if event.size().width() != event.oldSize().width():
            self.arrange()


class _LessonChoices(QWidget):
    """Keep the callout's answers in reading order as its width changes."""

    def __init__(self) -> None:
        """Start with an empty, left-aligned answer row."""
        super().__init__()
        self.setMinimumWidth(1)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(7)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.buttons: list[QPushButton] = []

    def set_buttons(self, buttons: list[QPushButton]) -> None:
        """
        Replace the previous question's answers.

        Parameters
        ----------
        buttons : list of QPushButton
            Buttons in reading and keyboard focus order.
        """
        for old in self.buttons:
            self.grid.removeWidget(old)
            old.hide()
            old.deleteLater()
        self.buttons = buttons
        self.setVisible(bool(buttons))
        self.arrange()

    def arrange(self) -> None:
        """Wrap buttons into as many columns as fit without truncating a label."""
        if self.buttons:
            spacing = self.grid.spacing()
            widest = max(max(button.minimumWidth(), button.sizeHint().width()) for button in self.buttons)
            columns = max(1, (self.width() + spacing) // (widest + spacing))
            for index, button in enumerate(self.buttons):
                row, col = divmod(index, columns)
                self.grid.addWidget(button, row, col, Qt.AlignmentFlag.AlignLeft)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Reflow the current answers without changing feedback or focus.

        Parameters
        ----------
        event : QResizeEvent
            New and previous widget sizes.
        """
        super().resizeEvent(event)
        if event.size().width() != event.oldSize().width():
            self.arrange()


class StepView(QWidget):
    """
    One step of a lesson: its words, a sound to hear, the circle, and a task.

    Attributes
    ----------
    step : Step
        The step.
    circle : ExplorableCircle or None
        The circle, for a step that has one.
    staves : list of StaffWidget
        The staves beside the words, for a step that has them: one for each of its `staves`, or the one that follows the task.
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
    practice : Signal
        Emitted by the Practice button on the last step.

    Examples
    --------
    >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
    >>> view = StepView(CIRCLE_OF_FIFTHS.steps[1], rng=random.Random(1))
    >>> view.task is not None and len(view.choice_buttons) == 4
    True
    """

    practice = Signal()

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
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> StepView(CIRCLE_OF_FIFTHS.steps[0]).circle is not None
        True
        """
        super().__init__(parent)
        self.step = step
        self.rng = rng or random.Random()
        self.task: Task | None = None
        self.circle: ExplorableCircle | None = None
        self.staves: list[StaffWidget] = []
        self.playback = StaffPlayback(self, highlight=self._highlight_sample)
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
        self.hear_button: QPushButton | None = None
        if step.hear:
            self.hear_button = QPushButton(f"▶  {step.hear_label}")
            self.hear_button.setObjectName("lessonPlayback")
            self.hear_button.clicked.connect(self.hear)
        if step.staves or step.task_staff:
            self.staves = [self._make_staff(staff) for staff in (step.staves or (Staff(clef="treble"),))]
        if step.hear_display == "staff":
            staff = StaffWidget(gap=8.0, side=8.0, lesson_layout=True)
            staff.show_notes([[Note.parse(name) for name in chord] for chord in step.hear], clef="treble")
            self.staves.append(staff)
        keyboard = None
        if step.keyboard_note or step.hear_display == "keyboard":
            keyboard = KeyboardWidget()
            keys = [step.keyboard_note] if step.keyboard_note else [name for chord in step.hear for name in chord]
            keyboard.show_keys([Note.parse(name).midi for name in keys], span=(60, 72))
            keyboard.setAccessibleName(f"Keyboard with {' and '.join(keys)} highlighted")
        self.illustration: _IllustratedStep | None = None
        if self.staves or keyboard is not None or (step.hear and step.circle == "none" and not step.scale):
            comparisons = [staff for staff in self.staves if len(staff.columns) == 1]
            for staff in comparisons:
                staff.lesson_peers.update(peer for peer in comparisons if peer is not staff)
                staff._fit_width()
            self.illustration = _IllustratedStep(text, staves=self.staves, keyboard=keyboard, playback=self.hear_button)
            left.addWidget(self.illustration)
        else:
            left.addWidget(text)
            if self.hear_button is not None:
                left.addWidget(self.hear_button, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self.info.setVisible(self.circle is not None)
        side.addWidget(self.info)
        self.task_box = QFrame()
        self.task_box.setObjectName("lessonKnowledgeCheck")
        self.task_box.setMaximumWidth(TEXT_WIDTH)
        heading = QLabel("Knowledge check")
        heading.setObjectName("knowledgeCheckHeading")
        self.task_box.setAccessibleName(heading.text())
        box = QVBoxLayout(self.task_box)
        box.setContentsMargins(15, 12, 15, 12)
        box.setSpacing(7)
        box.addWidget(heading)
        self.prompt = QLabel()
        self.prompt.setTextFormat(Qt.TextFormat.RichText)
        self.prompt.setWordWrap(True)
        self.choices = _LessonChoices()
        box.addWidget(self.prompt)
        box.addWidget(self.choices)
        box.addWidget(self.feedback)
        box.addWidget(self.again, alignment=Qt.AlignmentFlag.AlignLeft)
        self.task_box.setVisible(step.make_task is not None)
        side.addWidget(self.task_box)
        if step.closing:
            self.practice_button = QPushButton("Practice this in the exercise  →")
            self.practice_button.setDefault(True)
            self.practice_button.clicked.connect(self.practice)
            self.practice_layout = QVBoxLayout()
            self.practice_layout.addWidget(self.practice_button, alignment=Qt.AlignmentFlag.AlignLeft)
            side.addLayout(self.practice_layout)
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
        self.scale_explorer: ScaleExplorer | None = None
        if step.scale:
            explorer = ScaleExplorer(scale=step.scale, tonic=step.scale_tonic, editable=step.scale_explore, lesson_layout=True)
            self.scale_explorer = explorer
            scale_scroll = QScrollArea()
            scale_scroll.setWidgetResizable(True)
            scale_scroll.setFrameShape(QFrame.Shape.NoFrame)
            scale_scroll.setWidget(explorer)
            lay.addWidget(scale_scroll, 3)
        if step.circle == "walk" and self.circle is not None:
            self._show(self.circle, ring="outer", place=0)
        elif self.circle is not None:
            self.info.setText(self._invitation())
        if step.make_task is not None:
            self.ask()

    @staticmethod
    def _make_staff(staff: Staff) -> StaffWidget:
        """
        Make the picture of a staff for a step: a clef, perhaps a note, and the words under it.

        Parameters
        ----------
        staff : Staff
            What to show.

        Returns
        -------
        StaffWidget
            A small staff.

        Examples
        --------
        >>> StepView._make_staff(Staff(clef="alto", note="C4", caption="Alto")).caption
        'Alto'
        """
        widget = StaffWidget(gap=8.0, side=8.0, lesson_layout=True)
        widget.show_notes([[Note.parse(staff.note)]] if staff.note else [], clef=staff.clef, key=staff.key, caption=staff.caption)
        return widget

    def _invitation(self) -> str:
        """
        Say what can be done with this step's circle, before anything is picked.

        Returns
        -------
        str
            A sentence of advice.

        Examples
        --------
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> StepView(CIRCLE_OF_FIFTHS.steps[0])._invitation()
        'This is the circle. Each wedge is a key.'
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> StepView(CIRCLE_OF_FIFTHS.steps[3])._invitation()
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
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> from unittest.mock import patch
        >>> with patch.object(sounds, "enabled", False):
        ...     StepView(CIRCLE_OF_FIFTHS.steps[1]).hear()
        """
        if self.scale_explorer is not None:
            self.scale_explorer.hear(force=False)
            return
        columns = [[Note.parse(name) for name in column] for column in self.step.hear]
        gap_ms = 330 if len(columns) > 4 else 650
        if self.staves:
            self.playback.play(columns, gap_ms=gap_ms)
        else:
            sounds.play_notes(columns, gap_ms=gap_ms)

    def _highlight_sample(self, index: int | None) -> None:
        """
        Follow the phrase on its staff and light matching notes in comparison diagrams.

        Parameters
        ----------
        index : int or None
            Playback onset, or None when the sample ends.
        """
        sounding = {Note.parse(name).midi for name in self.step.hear[index]} if index is not None else set()
        for staff in self.staves:
            if self.step.hear_display == "staff" and staff is self.staves[-1]:
                staff.highlight_column(index)
            else:
                # Each comparison diagram shows a single written note, sometimes in two equivalent spellings.
                matches = bool(staff.columns and staff.columns[0][0].midi in sounding)
                staff.highlight_column(0 if matches else None)

    def walk(self, step: int) -> None:
        """
        Move the pick one fifth around the outer ring.

        Parameters
        ----------
        step : int
            1 for a fifth up (clockwise), -1 for a fifth down.

        Examples
        --------
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> view = StepView(CIRCLE_OF_FIFTHS.steps[2])
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
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> view = StepView(CIRCLE_OF_FIFTHS.steps[3], rng=random.Random(1))
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
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> view = StepView(CIRCLE_OF_FIFTHS.steps[3], rng=random.Random(1))
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
        self.feedback.hide()
        self.choice_buttons = []
        if (
            self.staves and self.step.task_staff
        ):  # the staff beside the words follows the task: its clef, or none to count lines on
            self.staves[0].clef_hidden = not task.clef
            self.staves[0].show_notes([], clef=task.clef or "treble", key=task.key)
            if self.illustration is not None:
                self.illustration.arrange()
        for text in task.choices:
            button = QPushButton(text)
            button.setMinimumWidth(56)
            button.clicked.connect(lambda _=False, answer=text, pressed=button: self._answered(answer, button=pressed))
            self.choice_buttons.append(button)
        self.choices.set_buttons(self.choice_buttons)
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
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> view = StepView(CIRCLE_OF_FIFTHS.steps[3], rng=random.Random(2))
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
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> view = StepView(CIRCLE_OF_FIFTHS.steps[1], rng=random.Random(1))
        >>> # noinspection PyUnresolvedReferences
        >>> view._answered(view.task.correct, button=None)
        >>> view.again.isHidden(), "Right" in view.feedback.text()
        (False, True)
        """
        task = self.task
        if task is None:
            return
        self.feedback.show()
        if task.check(answer):
            self.feedback.setText(f"<b>Right.</b> {task.explanation}")
            self.again.show()
            self._lock()
            if self.circle is not None and task.cells and isinstance(answer, tuple):
                self._show(self.circle, ring=answer[0], place=answer[1])
            return
        self._wrong += 1
        if button is not None:
            button.setEnabled(False)
        if self._wrong >= GIVE_UP_AFTER:
            self.feedback.setText(f"<b>Here it is.</b> {task.explanation}")
            self.again.show()
            self._lock()
            if self.circle is not None and task.cells:
                ring, place = min(task.cells)
                self._show(self.circle, ring=ring, place=place)
        else:
            self.feedback.setText(f"<b>Not quite.</b> {task.hint}")

    def _lock(self) -> None:
        """
        Switch off the answer buttons once the task is over.

        Examples
        --------
        >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
        >>> view = StepView(CIRCLE_OF_FIFTHS.steps[1], rng=random.Random(1))
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
    practice : Signal
        Emitted when the last step's Practice button is pressed, with the exercise's class name.

    Examples
    --------
    >>> from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
    >>> view = LessonView(CIRCLE_OF_FIFTHS)
    >>> view.counter.text()
    'Step 1 of 8'
    >>> view.go(to=1)
    >>> view.heading.text(), view.counter.text()
    ('A fifth', 'Step 2 of 8')
    """

    leave = Signal()
    stepped = Signal(int)
    practice = Signal(str)

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
            made.practice.connect(lambda: self.practice.emit(self.lesson.exercise))
            if steps[to].closing and self.lesson.related_exercises:
                names = {exercise.__name__: exercise.name for exercise in REGISTRY}
                made.practice_button.setText(names[self.lesson.exercise])
                for key in self.lesson.related_exercises:
                    button = QPushButton(names[key])
                    button.clicked.connect(lambda _checked=False, target=key: self.practice.emit(target))
                    made.practice_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
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
    back : Signal
        Emitted to leave the lesson, to wherever it was opened from.
    practice_requested : Signal
        Emitted with the class name of an exercise to practice.

    Examples
    --------
    >>> page = LessonsPage("circle-of-fifths")
    >>> page.view.lesson.key
    'circle-of-fifths'
    """

    back = Signal()
    practice_requested = Signal(str)

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
        self.view.practice.connect(self.practice_requested)
        self.restart_button.clicked.connect(lambda: self.view.go(to=0))
        outer.addWidget(self.view, 1)
