"""
The exercise screen: a question, its answer buttons, the score, and a
pane of settings that slides in from the right.

The view displays a supplied question and emits the learner's input.
ExerciseController connects practice inputs and updates. ExercisePage
connects playback.

Examples
--------
>>> import random
>>> from alto.exercises.library import NoteNames
>>> from alto.ui.exercise_page import ExercisePage
>>> view = ExercisePage(
...     NoteNames(), rng=random.Random(1)
... )
>>> # noinspection PyUnresolvedReferences
>>> view.question.answer in [
...     button.text() for button in view.control_area.answers.buttons
... ]
True
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QMetaMethod,
    QObject,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QHideEvent,
    QKeySequence,
    QPalette,
    QShortcut,
    QShowEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLayout,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto.exercises.base import (
    Exercise,
    Question,
)
from alto.exercises.library import (
    IntervalConstruction,
    NoteNames,
    OrderOfKeys,
    ScaleConstruction,
)
from alto.learning.calendar import DEFAULT_SCHEDULER
from alto.learning.practice_session import PracticeSession
from alto.ui.circle import FifthsCircle
from alto.ui.colors import (
    CORRECT_ANSWER_COLOR,
    blend,
)
from alto.ui.control_area import ControlArea
from alto.ui.exercise_toolbar import ExerciseToolbar
from alto.ui.key_fork import (
    KeyFork,
)
from alto.ui.question_view import QuestionView
from alto.ui.reference import (
    ReferencePane,
    reference_panel_for,
)
from alto.ui.settings_panel import (
    ExerciseSettingsPanel,
    settings_panel_for,
)
from alto.ui.staff import (
    StaffWidget,
)
from alto.ui.staff_input import (
    ClefInput,
    ScaleInput,
)
from alto.ui.zoom import px

if TYPE_CHECKING:
    from collections.abc import Callable

    from alto.ui.exercise_controller import AnswerResult


class ExerciseView(QWidget):
    """
    The screen for practicing one exercise.

    Attributes
    ----------
    session : PracticeSession
        Last progress snapshot rendered by the view.
    control_area : ControlArea
        Holds answer choices, placement actions, ratings, and Next.
    settings_pane : QFrame
        Collapsible frame that holds the exercise settings panel.
    settings_panel : ExerciseSettingsPanel
        The exercise's settings, including how to advance after a
        correct answer.
    question_view : QuestionView
        Displays the question and its placement editor.
    toolbar : ExerciseToolbar
        Shows progress and provides the exercise controls.
    reference_panel : ReferencePanel or None
        Exercise reference content, including links to lessons.
    reference_pane : ReferencePane or None
        The pane that holds the reference.

    Examples
    --------
    >>> import random
    >>> from alto.exercises.library import NoteNames
    >>> from alto.ui.exercise_page import ExercisePage
    >>> view = ExercisePage(
    ...     NoteNames(), rng=random.Random(1)
    ... )
    >>> view.toolbar.score.text()
    '0/0 (–)   streak 0'
    """

    visibility_changed = Signal(bool)
    fade_requested = Signal(object)
    replacing_question = Signal()

    def __init__(
        self,
        exercise: Exercise,
        *,
        settings_panel: ExerciseSettingsPanel | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the display and its input controls.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose questions and controls are in use.
        settings_panel : ExerciseSettingsPanel or None
            Settings widget for this exercise and learner.
        parent : QWidget or None
            Qt object that owns this instance.

        Examples
        --------
        A preview can display a supplied question before any practice
        begins.
        """
        super().__init__(parent)

        self.reference_panel = reference_panel_for(exercise)
        self.settings_panel = settings_panel or settings_panel_for(exercise)
        self.toolbar = self._create_toolbar(exercise)
        self.question_view = self._create_question_view(exercise)
        self.control_area = self._create_control_area(exercise)
        self.settings_pane = self._create_settings_pane()
        self.reference_pane = self._create_reference_pane()

        outer = QHBoxLayout(self)
        outer.addWidget(self._create_main_area(), 1)
        outer.addWidget(self.settings_pane)
        if self.reference_pane is not None:
            outer.addWidget(self.reference_pane)
        self._bind_placement_shortcuts()
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    @property
    def session(self) -> PracticeSession:
        """
        Read the progress snapshot used to render the current question.

        Returns
        -------
        PracticeSession
            The latest progress published to the view.

        Examples
        --------
        Placement actions check whether the question is answered.
        """
        return self.question_view.progress

    def _create_toolbar(self, exercise: Exercise) -> ExerciseToolbar:
        """
        Build the toolbar for the active exercise.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose controls are being built.

        Returns
        -------
        ExerciseToolbar
            Toolbar with the tools available for this exercise.

        Examples
        --------
        Exercises with a reference show a book button.
        """
        return ExerciseToolbar(
            exercise.instructions,
            has_reference=self.reference_panel is not None,
            has_midi=sys.platform.startswith("linux")
            and isinstance(
                exercise,
                (NoteNames, IntervalConstruction, ScaleConstruction),
            ),
        )

    def _create_question_view(self, exercise: Exercise) -> QuestionView:
        """
        Build the question view and connect its signals.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose controls are being built.

        Returns
        -------
        QuestionView
            The question view for the current exercise.

        Examples
        --------
        Marking a beat updates the placement controls.
        """
        view = QuestionView(
            exercise,
            center_controls=isinstance(exercise, OrderOfKeys),
        )
        view.widget_created.connect(self._connect_music_widget)
        view.beats_changed.connect(self._show_placement_rows)
        return view

    def _create_control_area(self, exercise: Exercise) -> ControlArea:
        """
        Build the control area and connect its placement buttons.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose controls are being built.

        Returns
        -------
        ControlArea
            Controls for answering and rating the current question.

        Examples
        --------
        Pressing Answer submits the question view’s current placement.
        """
        area = ControlArea(exercise)
        placement = area.answers.placement
        placement.undo_button.clicked.connect(
            self.question_view.undo_scale_note,
        )
        placement.place_button.clicked.connect(
            self.question_view.place_here,
        )
        placement.answer_button.clicked.connect(
            self.question_view.submit_placement,
        )
        placement.answer_button.installEventFilter(self)
        return area

    def _create_main_area(self) -> QWidget:
        """
        Arrange the exercise components in the main column.

        Returns
        -------
        QWidget
            Practice area to the left of the collapsible panes.

        Examples
        --------
        The answer controls appear directly below the question.
        """
        main = QWidget()
        lay = QVBoxLayout(main)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toolbar)
        lay.addWidget(self.question_view)
        lay.addWidget(self.control_area)
        lay.addStretch()
        return main

    def _create_settings_pane(self) -> QFrame:
        """
        Build the collapsible pane for exercise settings.

        Returns
        -------
        QFrame
            Settings frame connected to the toolbar toggle.

        Examples
        --------
        The sliders button opens the pane.
        """
        pane = QFrame()
        pane.setObjectName("settingsPane")
        pane.setFrameShape(QFrame.Shape.StyledPanel)
        pane.setMinimumWidth(0)
        pane.setMaximumWidth(0)
        pane_lay = QVBoxLayout(pane)
        pane_lay.setSizeConstraint(
            QLayout.SizeConstraint.SetNoConstraint,
        )  # let the pane shrink to zero while animating
        settings_header = QHBoxLayout()
        settings_header.addStretch()
        self.settings_collapse = QToolButton()
        self.settings_collapse.setText("−")
        self.settings_collapse.setAutoRaise(True)
        self.settings_collapse.setToolTip("Collapse exercise settings")
        self.settings_collapse.setAccessibleName(
            "Collapse exercise settings",
        )
        self.settings_collapse.clicked.connect(
            lambda: self.toolbar.gear.setChecked(False),
        )
        settings_header.addWidget(self.settings_collapse)
        pane_lay.addLayout(settings_header)
        self.settings_panel.setFixedWidth(
            px(self.settings_panel.PANE_WIDTH - 2 * 9),
        )
        pane_lay.addWidget(
            self.settings_panel,
            1,
        )  # fill the pane so long pages (Range) can scroll
        pane.hide()
        self._pane_anim = QPropertyAnimation(
            pane,
            b"maximumWidth",
            self,
        )
        self._pane_anim.setDuration(220)
        self._pane_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._pane_anim.finished.connect(self._pane_settled)
        self.toolbar.gear.toggled.connect(self._toggle_pane)
        self.settings_panel.restyled.connect(
            self.question_view.redraw_keyboards,
        )
        return pane

    def _create_reference_pane(self) -> ReferencePane | None:
        """
        Build the collapsible reference pane when one is available.

        Returns
        -------
        ReferencePane or None
            Reference frame for exercises with a reference panel.

        Examples
        --------
        The book button opens the pane.
        """
        reference = self.reference_panel
        book = self.toolbar.book_btn
        if reference is None or book is None:
            return None
        book.toggled.connect(self._toggle_reference)
        ref_pane = ReferencePane()
        book_lay = QVBoxLayout(ref_pane)
        book_lay.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        reference_header = QHBoxLayout()
        reference_header.addStretch()
        self.reference_collapse = QToolButton()
        self.reference_collapse.setText("−")
        self.reference_collapse.setAutoRaise(True)
        self.reference_collapse.setToolTip("Collapse reference")
        self.reference_collapse.setAccessibleName("Collapse reference")
        self.reference_collapse.clicked.connect(
            lambda: book.setChecked(False),
        )
        reference_header.addWidget(self.reference_collapse)
        book_lay.addLayout(reference_header)
        reference.setFixedWidth(px(ref_pane.REFERENCE_WIDTH - 2 * 9))
        book_lay.addWidget(reference, 1)
        ref_pane.hide()
        self._reference_anim = QPropertyAnimation(
            ref_pane,
            b"maximumWidth",
            self,
        )
        self._reference_anim.setDuration(220)
        self._reference_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._reference_anim.finished.connect(self._reference_settled)
        return ref_pane

    def _bind_placement_shortcuts(self) -> None:
        """
        Bind navigation and note-letter keys to the placement editor.

        Examples
        --------
        Pressing G moves the staff caret to the letter G.
        """
        self._arrow_keys = [
            self._bind(
                sequence,
                action=lambda action_name=name: self.question_view.key_action(
                    action_name,
                ),
            )
            for sequence, name in (
                ("Up", "up"),
                ("Down", "down"),
                ("Left", "left"),
                ("Right", "right"),
                ("PgUp", "pageup"),
                ("PgDown", "pagedown"),
                ("Home", "home"),
            )
        ]
        self._letter_keys = [
            self._bind(
                name,
                action=lambda letter=letter: self.question_view.jump_to_letter(
                    letter,
                ),
            )
            for letter, name in enumerate(
                "CDEFGAB",
            )  # C is 0, D is 1 ... B is 6, as a note's letter counts
        ]

    def hideEvent(self, event: QHideEvent) -> None:
        """
        Report that the learner has left the exercise display.

        Parameters
        ----------
        event : QHideEvent
            The notification that the exercise is being hidden.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(NoteNames())
        >>> view.show()
        >>> view.hide()
        >>> view.controller._advance.isActive()
        False
        """
        self.visibility_changed.emit(False)
        super().hideEvent(event)

    def showEvent(self, event: QShowEvent) -> None:
        """
        Report that the exercise display is visible again.

        Parameters
        ----------
        event : QShowEvent
            The notification that the exercise is visible again.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(NoteNames())
        >>> view.show()
        >>> view.hide()
        >>> view.show()
        >>> view.controller._hidden_at is None
        True
        """
        self.visibility_changed.emit(True)
        super().showEvent(event)

    def _bind(
        self,
        sequence: str,
        *,
        action: Callable[[], object],
    ) -> QShortcut:
        """
        Bind a key to something to do, for as long as the keyboard is
        anywhere on this screen.

        The key is off until it is switched on, so that it only works
        for the questions that use it. It does not work while
        the keyboard is in the exercise list or elsewhere outside the
        screen, where the same keys do other things.

        Parameters
        ----------
        sequence : str
            The key, such as "Up" or "C".
        action : callable
            What to do when it is pressed. Keyword-only.

        Returns
        -------
        QShortcut
            The binding, which starts off.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> bound = view._bind(
        ...     "Up", action=lambda: None
        ... )
        >>> bound.isEnabled(), bound.key().toString()
        (False, 'Up')
        """
        binding = QShortcut(QKeySequence(sequence), self)
        binding.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        binding.setEnabled(False)
        binding.activated.connect(action)
        return binding

    def settings_state(self) -> tuple[bool, int, int] | None:
        """
        Remember the exercise settings pane, selected page, and scroll
        position before a theme rebuild.

        Returns
        -------
        tuple of (bool, int, int) or None
            Whether the pane is open, its page index, and its vertical
            scroll position; None without settings.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> ExercisePage(
        ...     NoteNames(), rng=random.Random(1)
        ... ).settings_state()
        (False, 0, 0)
        """
        panel = self.settings_panel
        if panel is None or self.toolbar.gear is None:
            return None
        stack = panel.findChild(QStackedWidget)
        page = stack.currentWidget() if stack is not None else panel
        scroll = page.findChild(QScrollArea) if page is not None else None
        return (
            self.toolbar.gear.isChecked(),
            stack.currentIndex() if stack is not None else 0,
            (scroll.verticalScrollBar().value() if scroll is not None else 0),
        )

    def restore_settings_state(self, state: tuple[bool, int, int]) -> None:
        """
        Restore exercise settings navigation immediately after
        rebuilding the view.

        Parameters
        ----------
        state : tuple of (bool, int, int)
            Whether the pane was open, the selected page, and its
            vertical scroll position.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view.restore_settings_state((True, 0, 0))
        >>> view.settings_state()
        (True, 0, 0)
        """
        panel = self.settings_panel
        if panel is None or self.toolbar.gear is None:
            return
        open_, index, position = state
        stack = panel.findChild(QStackedWidget)
        if stack is not None and 0 <= index < stack.count():
            stack.setCurrentIndex(index)
        self.toolbar.gear.setChecked(open_)
        self._pane_anim.stop()
        self.settings_pane.setMaximumWidth(
            px(panel.PANE_WIDTH) if open_ else 0,
        )
        self.settings_pane.setVisible(open_)
        page = stack.currentWidget() if stack is not None else panel
        scroll = page.findChild(QScrollArea) if page is not None else None
        if scroll is not None:
            bar = scroll.verticalScrollBar()
            QTimer.singleShot(0, scroll, lambda: bar.setValue(position))

    def _toggle_pane(self, open_: bool) -> None:
        """
        Slide the settings pane open or closed.

        Parameters
        ----------
        open_ : bool
            True to open it, False to close it.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._toggle_pane(True)
        >>> view._pane_anim.endValue()
        290
        """
        if open_ and self.toolbar.book_btn is not None:
            self.toolbar.book_btn.setChecked(
                False,
            )  # the two panes share the right-hand side
        self._pane_anim.stop()
        self.settings_pane.show()
        self._pane_anim.setStartValue(self.settings_pane.maximumWidth())
        self._pane_anim.setEndValue(
            px(self.settings_panel.PANE_WIDTH) if open_ else 0,
        )
        self._pane_anim.start()

    def _pane_settled(self) -> None:
        """
        Hide the pane once it has finished sliding shut.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._pane_settled()  # the pane starts closed
        >>> view.settings_pane.isVisible()
        False
        """
        if self.settings_pane.maximumWidth() == 0:
            self.settings_pane.hide()

    def _toggle_reference(self, open_: bool) -> None:
        """
        Slide the reference pane open or closed.

        Opening it closes the settings pane, as they share the
        right-hand side.

        Parameters
        ----------
        open_ : bool
            True to open it, False to close it.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     CircleOfFifths,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     CircleOfFifths(), rng=random.Random(1)
        ... )
        >>> view._toggle_reference(True)
        >>> view._reference_anim.endValue()
        400
        """
        if open_ and self.settings_panel:
            self.toolbar.gear.setChecked(False)
        pane = self.reference_pane
        if pane is None:
            return
        self._reference_anim.stop()
        pane.show()
        self._reference_anim.setStartValue(pane.maximumWidth())
        self._reference_anim.setEndValue(
            px(pane.REFERENCE_WIDTH) if open_ else 0,
        )
        self._reference_anim.start()

    def _reference_settled(self) -> None:
        """
        Hide the reference pane once it has finished sliding shut.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     CircleOfFifths,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     CircleOfFifths(), rng=random.Random(1)
        ... )
        >>> view._reference_settled()  # the pane starts closed
        >>> (
        ...     view.reference_pane is not None
        ...     and view.reference_pane.isVisible()
        ... )
        False
        """
        if (
            self.reference_pane is not None
            and self.reference_pane.maximumWidth() == 0
        ):
            self.reference_pane.hide()

    def show_question(  # noqa: PLR0917 (Qt signal arguments)
        self,
        q: Question,
        empty_sample: Question | None = None,
        scheduler_mode: str = DEFAULT_SCHEDULER,
        self_grading: bool = False,
    ) -> None:
        """
        Draw the supplied question or empty-queue message.

        Parameters
        ----------
        q : Question
            Question to draw.
        empty_sample : Question or None
            Example used to lay out an empty review queue.
        scheduler_mode : str
            Scheduler selected for this practice session.
        self_grading : bool
            Whether the learner chooses a passing grade.

        Examples
        --------
        A scale construction question mounts a scale editor.
        """
        self.replacing_question.emit()
        self.settings_panel.refresh_limits(
            scheduler_mode,
            self_grading=self_grading,
        )
        if (
            self.settings_panel is not None
            and self.settings_panel.choice_buttons_row is not None
        ):
            self.settings_panel.choice_buttons_row.setVisible(
                bool(q.choices)
                or (empty_sample is not None and bool(empty_sample.choices)),
            )
        named_meter = self.question_view.show_question(
            q,
            answer_width=self.control_area.answers.maximumWidth(),
            empty_queue=empty_sample is not None,
        )
        self._show_placement_rows()
        self.control_area.show_question(
            q,
            named_meter=named_meter,
            empty_queue=empty_sample is not None,
            locate_notation=bool(
                self.question_view.staff
                and self.question_view.staff.locate_notation,
            ),
        )

    def _connect_music_widget(self, widget: QWidget) -> None:
        """
        Connect a newly mounted music widget to the exercise controls.

        Parameters
        ----------
        widget : QWidget
            Display staff or editor created for the current question.

        Examples
        --------
        Placing a note on the input staff submits it to this view.
        """
        if isinstance(widget, ScaleInput):
            widget.notes_changed.connect(self._scale_changed)
        elif isinstance(widget, ClefInput):
            widget.changed.connect(self._show_placement_rows)
        elif isinstance(widget, FifthsCircle):
            self.settings_panel.restyled.connect(widget.update)
        elif isinstance(widget, StaffWidget):
            widget.installEventFilter(self)

    @staticmethod
    def _style(color: QColor) -> str:
        """
        Return the style sheet that colors an answer button.

        Parameters
        ----------
        color : QColor
            The background color, with white text on it.

        Returns
        -------
        str
            Qt style sheet text.

        Examples
        --------
        >>> ExerciseView._style(
        ...     QColor(CORRECT_ANSWER_COLOR)
        ... )
        'QPushButton, QPushButton:disabled { background: #2e7d32; color:
        white; }'
        """
        return (
            "QPushButton, QPushButton:disabled { background: "
            f"{color.name()}"
            "; color: white; }"
        )

    def _request_fade(self, step: Callable[[float], None]) -> None:
        """
        Request a timed fade or paint its final color in a preview.

        Parameters
        ----------
        step : callable
            Paints the widget at the supplied fraction of the fade.

        Examples
        --------
        An attached controller drives the fade for a graded answer.
        """
        if self.isSignalConnected(QMetaMethod.fromSignal(self.fade_requested)):
            self.fade_requested.emit(step)
        else:
            step(1.0)

    def _flash(
        self,
        button: QPushButton | None,
        *,
        target: str = CORRECT_ANSWER_COLOR,
        staff: bool = False,
    ) -> None:
        """
        Fade a button (and optionally the notes) from the staff's ink to
        a color over a short time.

        Parameters
        ----------
        button : QPushButton or None
            The button to color, if the learner used one.
        target : str
            The feedback color. Defaults to the correct-answer green.
            Keyword-only.
        staff : bool, default False
            Also color the notes on the staff, or the highlighted key.
            Keyword-only.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._flash(view.control_area.answers.buttons[0])
        >>> len(view.controller.animations.tracked)
        1
        """
        end, start = QColor(target), QColor("black")

        def step(t: float) -> None:
            """
            Set the colors for one moment of the fade.

            Parameters
            ----------
            t : float
                How far through the fade: 0 at the start, 1 at the end.

            Examples
            --------
            >>> step(0.5)  # doctest: +SKIP
            """
            c = blend(start, b=end, t=t)
            if button is not None:
                button.setStyleSheet(self._style(c))
            if staff:
                if self.question_view.staff is not None:
                    self.question_view.staff.set_note_color(
                        c if t > 0 else None,
                    )
                if self.question_view.keyboard is not None:
                    self.question_view.keyboard.set_highlight_color(
                        c
                        if t > 0
                        else self.palette().color(
                            QPalette.ColorRole.Highlight,
                        ),
                    )

        self._request_fade(step)

    def _flash_note(self, target: str = CORRECT_ANSWER_COLOR) -> None:
        """
        Fade the placed note from the staff's ink to a color.

        Parameters
        ----------
        target : str
            The feedback color. Defaults to the correct-answer green.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view._flash_note("#c62828")
        >>> len(view.controller.animations.tracked)
        1
        """
        end, start = QColor(target), QColor("black")
        self._request_fade(
            lambda t: self.question_view.note_input.set_note_color(
                blend(start, b=end, t=t),
            ),
        )

    def _scale_changed(self) -> None:
        """
        Get ready for what comes next on the scale staff: the sign is
        used up, and the right buttons are shown.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view.question_view.set_accidental(1)
        >>> view._scale_changed()
        >>> actions = view.control_area.answers.placement
        >>> (
        ...     view.question_view.scale_input.accidental is None,
        ...     actions.answer_button.isEnabled(),
        ... )
        (True, False)
        """
        q = self.question_view.interactive_question
        if q and q.place_signature:
            self.question_view.scale_input.set_note_color(None)
        elif self.question_view.scale_input.accidental is not None:
            self.question_view.set_accidental(None)
        self._show_placement_rows()

    def _show_placement_rows(self) -> None:
        """
        Show the buttons for what the question is waiting for, and let
        Place and Answer work when they can.

        For a note or a scale on the staff the pitch and sign buttons
        show while notes are being placed, the whole and half
        step buttons while steps are, and neither once everything is
        down. Place does the next thing, and Answer takes over
        from it once everything is placed. For a key signature on the
        fork only Answer shows.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view._show_placement_rows()
        >>> actions = view.control_area.answers.placement
        >>> (
        ...     view.question_view.step_row.isHidden(),
        ...     actions.answer_button.isEnabled(),
        ...     actions.place_button.isEnabled(),
        ... )
        (True, False, True)
        """
        q = self.question_view.displayed_question
        if q is None:
            return
        note, sequence, fork = (
            q.construct is not None,
            q.places_sequence,
            q.build_key,
        )
        clef = bool(q.place_clef)
        beat_editor = self.question_view.active_beat_editor
        placing_notes = note or (
            sequence and not self.question_view.scale_input.complete
        )
        steps_turn = sequence and self.question_view.scale_input.placing_steps
        live = (
            self.question_view.interactive_question is not None
            and not self.session.answered
            and not self.question_view.busy
        )
        for (
            symbol,
            button,
        ) in (
            self.question_view.symbol_buttons.items()
        ):  # one for each symbol that can be chosen, the chosen one pressed
            button.setVisible(
                clef and symbol in self.question_view.clef_input.options,
            )
            button.setChecked(
                clef and symbol == self.question_view.clef_input.selected,
            )
            button.setEnabled(live)
        self.control_area.answers.placement.show_actions(
            q,
            live=live,
            sequence=self.question_view.scale_input if sequence else None,
            beats=beat_editor,
        )
        self.question_view.place_status.setVisible(
            note or sequence or beat_editor is not None,
        )
        self.question_view.pitch_row.setVisible(
            placing_notes and not q.place_signature,
        )
        self.question_view.accidental_buttons[0].setVisible(
            not q.place_signature,
        )
        self.question_view.accidental_row.setEnabled(live and placing_notes)
        self.question_view.accidental_row.setVisible(
            q.place_signature or (q.accidentals and placing_notes),
        )
        self.question_view.step_row.setVisible(steps_turn)
        if beat_editor is not None:
            beat_editor.setEnabled(live)
            count = len(beat_editor.marks)
            if beat_editor.feedback is False:
                self.question_view.place_status.setText(
                    "Check where each beat begins.",
                )
            elif beat_editor.feedback is True:
                self.question_view.place_status.setText("Correct.")
            elif count:
                self.question_view.place_status.setText(
                    f"Beats marked: {count}",
                )
            else:
                self.question_view.place_status.setText(
                    "Mark each beat, including the start of each measure.",
                )
        for key in self._arrow_keys:
            key.setEnabled(self.question_view.editor is not None)
        for key in self._letter_keys:
            key.setEnabled(placing_notes and not fork)
        if note or sequence:
            action = "place the scale" if sequence else "place the note"
            self.question_view.note_input.setAccessibleName(
                "Staff: write the key signature"
                if q.place_signature
                else f"Staff: {action}",
            )
            self.question_view.update_placement_status()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: PLR0917  (Qt calls it with both)
        """
        Forward wheel turns from the staff or Answer button.

        Parameters
        ----------
        watched : QObject
            The staff or the Answer button.
        event : QEvent
            The incoming pointer or widget event.

        Returns
        -------
        bool
            True when the exercise handles the event.

        Examples
        --------
        >>> import random
        >>> from PySide6.QtCore import QPoint, QPointF
        >>> from PySide6.QtGui import QWheelEvent
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(1),
        ... )
        >>> view.show()
        >>> here = QPointF(5, 5)
        >>> turn = QWheelEvent(
        ...     here,
        ...     here,
        ...     QPoint(0, 0),
        ...     QPoint(0, 120),
        ...     Qt.MouseButton.NoButton,
        ...     Qt.KeyboardModifier.NoModifier,
        ...     Qt.ScrollPhase.NoScrollPhase,
        ...     False,
        ... )
        >>> answer = view.control_area.answers.placement.answer_button
        >>> view.eventFilter(answer, turn)
        True
        >>> assert isinstance(view.question_view.editor, KeyFork)
        >>> view.question_view.editor.value
        1
        """
        if isinstance(event, QWheelEvent) and watched in (
            self.question_view.staff,
            self.control_area.answers.placement.answer_button,
        ):
            editor = self.question_view.editor
            if isinstance(editor, (KeyFork, ClefInput)) and editor.isVisible():
                editor.wheelEvent(event)
                return True
        return super().eventFilter(watched, event)

    def _flash_clef(self, target: str = CORRECT_ANSWER_COLOR) -> None:
        """
        Fade the placed clef from black to a color.

        Parameters
        ----------
        target : str
            The feedback color. Defaults to the correct-answer green.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     ClefBasics,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ClefBasics(), rng=random.Random(2)
        ... )
        >>> view._flash_clef("#c62828")
        >>> len(view.controller.animations.tracked)
        1
        """
        end, start = QColor(target), QColor("black")
        self._request_fade(
            lambda t: self.question_view.clef_input.set_clef_color(
                blend(start, b=end, t=t),
            ),
        )

    def show_progress(self, session: PracticeSession, busy: bool) -> None:  # noqa: PLR0917 (Qt signal arguments)
        """
        Display the score and remember whether input is available.

        Parameters
        ----------
        session : PracticeSession
            Immutable progress snapshot from the controller.
        busy : bool
            Whether feedback temporarily blocks further input.

        Examples
        --------
        An incorrect first attempt updates the total and streak.
        """
        self.question_view.progress = session
        self.question_view.busy = busy
        self.toolbar.show_score(session)

    def show_counts(  # noqa: PLR0917 (Qt signal arguments)
        self,
        counts: tuple[int, int, int] | None,
        current: str | None,
    ) -> None:
        """
        Display the calendar queue counts for this exercise.

        Parameters
        ----------
        counts : tuple[int, int, int] or None
            Review, new, and incorrect card counts.
        current : str or None
            Queue containing the current card.

        Examples
        --------
        A calendar review shows the three queue counts in the toolbar.
        """
        if counts is None:
            self.toolbar.queue_counts.hide()
        else:
            self.toolbar.queue_counts.set_counts(
                counts,
                studying=True,
                current=current,
            )
            self.toolbar.queue_counts.show()

    def show_selection(self, parts: dict[str, str]) -> None:
        """
        Check the selected name and octave or other second answer
        part.

        Parameters
        ----------
        parts : dict[str, str]
            Selected values keyed by answer part.

        Examples
        --------
        Choosing the octave first keeps it checked while the name is
        pending.
        """
        q = self.question_view.interactive_question
        if q is None:
            return
        labels = [*q.choices, *(q.octaves or ())]
        for i, (button, label) in enumerate(
            zip(self.control_area.answers.buttons, labels, strict=True),
        ):
            button.setChecked(
                parts.get("name" if i < len(q.choices) else "octave") == label,
            )

    def show_partial(self, choice: str) -> None:
        """
        Highlight a correct choice while another required choice is
        pending.

        Parameters
        ----------
        choice : str
            Submitted answer text.

        Examples
        --------
        An enharmonic key can require two names before practice
        advances.
        """
        q = self.question_view.interactive_question
        if q:
            button = self.control_area.answers.buttons[q.choices.index(choice)]
            button.setEnabled(False)
            self._flash(button)
            if self.question_view.circle is not None:
                self.question_view.circle.set_subtitle("and its other name")

    def _feedback_buttons(
        self,
        result: AnswerResult,
        *,
        q: Question,
    ) -> list[QPushButton]:
        """
        Find the visible controls identified by a graded answer.

        Parameters
        ----------
        result : AnswerResult
            Outcome of the submitted answer.
        q : Question
            Displayed question with its choices in presentation order.

        Returns
        -------
        list of QPushButton
            Buttons corresponding to the submitted values.

        Examples
        --------
        A two-part answer marks one button in each row.
        """
        if result.kind == "note":
            return [self.control_area.answers.placement.place_button]
        if result.kind in ("fork", "clef", "beats", "scale", "signature"):
            return [self.control_area.answers.placement.answer_button]
        if result.selected:
            buttons = self.control_area.answers.buttons
            first = buttons[q.choices.index(result.selected[0])]
            if q.octaves and len(result.selected) == 2:
                return [
                    first,
                    buttons[
                        len(q.choices) + q.octaves.index(result.selected[1])
                    ],
                ]
            return [first]
        return []

    def show_result(self, result: AnswerResult, mode: str) -> None:  # noqa: PLR0917 (Qt signal arguments)
        """
        Present a graded answer without evaluating it or advancing
        practice.

        Parameters
        ----------
        result : AnswerResult
            Outcome of the submitted answer.
        mode : str
            Selected Next Question behavior.

        Examples
        --------
        An incorrect clef placement flashes the clef on the input
        staff.
        """
        q = self.question_view.interactive_question
        if q is None:
            return
        kind = result.kind
        buttons = self._feedback_buttons(result, q=q)
        self.question_view.show_result(result)
        if result.correct:
            if kind == "choice" and q.required:
                for button in buttons:
                    button.setEnabled(False)
            if mode == "Immediately":
                for button in buttons:
                    button.setStyleSheet(
                        self._style(QColor(CORRECT_ANSWER_COLOR)),
                    )
            else:
                if mode == "Wait":
                    for button in self.control_area.answers.buttons:
                        button.setEnabled(False)
                for button in buttons:
                    self._flash(button)
                if self.question_view.circle is not None:
                    self.question_view.circle.reveal()
        else:
            self._show_incorrect(result, buttons=buttons)
        self._show_placement_rows()
        if (
            kind == "signature"
            and not result.correct
            and not self.session.answered
        ):
            self.control_area.answers.placement.answer_button.setEnabled(False)
            self.question_view.place_status.setText(
                "Try again. Use Undo to change the signature, "
                "or add another sign.",
            )

    def _show_incorrect(
        self,
        result: AnswerResult,
        *,
        buttons: list[QPushButton],
    ) -> None:
        """
        Mark the submitted controls and show the appropriate retry
        message.

        Parameters
        ----------
        result : AnswerResult
            Outcome of the submitted answer.
        buttons : list[QPushButton]
            Controls for the submitted answer.

        Examples
        --------
        In ordinary practice, an incorrect choice becomes unavailable.
        """
        q = self.question_view.interactive_question
        assert q is not None
        if self.question_view.circle:
            self.question_view.circle.flash_wrong()
        if result.kind in ("note", "scale"):
            self._flash_note("#c62828")
        elif result.kind == "fork" and isinstance(
            self.question_view.editor,
            KeyFork,
        ):
            self._request_fade(
                self.question_view.editor.marker_fade("#c62828"),
            )
        elif result.kind == "clef":
            self._flash_clef("#c62828")
        elif result.kind == "signature":
            self.question_view.scale_input.set_note_color(QColor("#c62828"))
        elif result.kind == "pair":
            for button in buttons:
                self._flash(button, target="#c62828")
        elif result.kind == "choice":
            for button in buttons:
                button.clearFocus()
                button.setEnabled(False)
                self._flash(button, target="#c62828")
        elif result.kind in ("notation", "midi"):
            self.question_view.show_prompt(f"Try again. {q.prompt}")
        if self.session.answered:
            for button in self.control_area.answers.buttons:
                button.setEnabled(False)

    def show_retry(self, kind: str) -> None:
        """
        Reset the editor or selected buttons for another attempt.

        Parameters
        ----------
        kind : str
            Input that produced this answer.

        Examples
        --------
        After an incorrect pair, both rows accept a new selection.
        """
        q = self.question_view.interactive_question
        if q is None:
            return
        self.question_view.reset_placement(kind)
        if kind == "pair":
            for button in self.control_area.answers.buttons:
                if button.isChecked():
                    button.setStyleSheet("")
                    button.setChecked(False)
        self._show_placement_rows()

    def show_silent_feedback(self) -> None:
        """
        Animate an answer that has no sounding notes.

        Examples
        --------
        A correct clef placement flashes the clef symbol.
        """
        q = self.question_view.interactive_question
        if q is None:
            return
        if (
            q.picture is not None
            and self.question_view.fingerboard is not None
        ):
            self.question_view.fingerboard.animate_silent_answer(600)
        elif q.place_clef:
            self._flash_clef()
        elif isinstance(self.question_view.editor, KeyFork):
            self._request_fade(self.question_view.editor.marker_fade())
        elif q.construct is not None or q.places_sequence:
            self._flash_note()
        else:
            self._flash(None, staff=True)
