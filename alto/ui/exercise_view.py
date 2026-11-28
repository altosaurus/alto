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
    QEvent,
    QMetaMethod,
    QObject,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QHideEvent,
    QKeySequence,
    QShortcut,
    QShowEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
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
from alto.ui.colors import (
    CORRECT_ANSWER_COLOR,
)
from alto.ui.control_area import ControlArea
from alto.ui.exercise_toolbar import ExerciseToolbar
from alto.ui.key_fork import (
    KeyFork,
)
from alto.ui.question_view import QuestionView
from alto.ui.reference import (
    REFERENCE_WIDTH,
    reference_panel_for,
)
from alto.ui.settings_panel import (
    ExerciseSettingsPanel,
    settings_panel_for,
)
from alto.ui.side_pane import SidePane
from alto.ui.staff import (
    StaffWidget,
)
from alto.ui.staff_input import (
    ClefInput,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from alto.ui.exercise_controller import AnswerResult


class ExerciseView(QWidget):
    """
    The screen for practicing one exercise.

    Properties
    ----------
    session : PracticeSession
        Read-only progress snapshot for the displayed question.

    Attributes
    ----------
    control_area : ControlArea
        Holds answer choices, placement actions, ratings, and Next.
    settings_pane : SidePane
        Collapsible pane that holds the exercise settings panel.
    settings_panel : ExerciseSettingsPanel
        The exercise's settings, including how to advance after a
        correct answer.
    question_view : QuestionView
        Displays the question and its placement editor.
    toolbar : ExerciseToolbar
        Shows progress and provides the exercise controls.
    reference_panel : ReferencePanel or None
        Exercise reference content, including links to lessons.
    reference_pane : SidePane or None
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
        self.toolbar = ExerciseToolbar(
            instructions=exercise.instructions,
            has_reference=self.reference_panel is not None,
            has_midi=sys.platform.startswith("linux")
            and isinstance(
                exercise,
                (
                    NoteNames,
                    IntervalConstruction,
                    ScaleConstruction,
                ),
            ),
        )
        self.question_view = self._create_question_view(exercise)
        self.control_area = self._create_control_area(exercise)
        self.settings_pane, self.reference_pane = self._create_side_panes()

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
        view.placement_changed.connect(self._show_placement_actions)
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

    def _create_side_panes(self) -> tuple[SidePane, SidePane | None]:
        """
        Build the settings pane and, when there is one, the reference
        pane, each opened by its toolbar button.

        The two panes share the right-hand side, so opening one closes
        the other.

        Returns
        -------
        tuple of SidePane and SidePane or None
            The settings pane, and the reference pane for exercises
            with a reference.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import CircleOfFifths
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(CircleOfFifths(), rng=random.Random(1))
        >>> view.toolbar.gear.setChecked(True)
        >>> view.toolbar.book_btn.setChecked(True)
        >>> view.toolbar.gear.isChecked()
        False
        """
        gear = self.toolbar.gear
        settings = SidePane(
            self.settings_panel,
            open_width=self.settings_panel.PANE_WIDTH,
            toggle=gear,
            label="Collapse exercise settings",
        )
        self.settings_panel.restyled.connect(self.question_view.restyle)
        book = self.toolbar.book_btn
        if self.reference_panel is None or book is None:
            return settings, None
        reference = SidePane(
            self.reference_panel,
            open_width=REFERENCE_WIDTH,
            toggle=book,
            label="Collapse reference",
        )
        gear.toggled.connect(self._closer(book))
        book.toggled.connect(self._closer(gear))
        return settings, reference

    @staticmethod
    def _closer(other: QToolButton) -> Callable[[bool], None]:
        """
        Make a slot that unchecks another pane's button when a pane
        opens.

        Parameters
        ----------
        other : QToolButton
            Toolbar button of the pane to close.

        Returns
        -------
        callable
            Unchecks `other` when called with True.

        Examples
        --------
        >>> button = QToolButton()
        >>> button.setCheckable(True)
        >>> button.setChecked(True)
        >>> ExerciseView._closer(button)(True)
        >>> button.isChecked()
        False
        """

        def close(opened: bool) -> None:
            """
            Close the other pane if this one opened.

            Parameters
            ----------
            opened : bool
                Whether this pane's button was checked.

            Examples
            --------
            Closing a pane leaves the other one as it was.
            """
            if opened:
                other.setChecked(False)

        return close

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
        >>> reports = []
        >>> connection = view.visibility_changed.connect(reports.append)
        >>> view.hide()
        >>> reports
        [False]
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
        >>> reports = []
        >>> connection = view.visibility_changed.connect(reports.append)
        >>> view.show()
        >>> view.hide()
        >>> view.show()
        >>> reports
        [True, False, True]
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

    def settings_state(self) -> tuple[bool, int, int]:
        """
        Remember the exercise settings pane, selected page, and scroll
        position before a theme rebuild.

        Returns
        -------
        tuple of (bool, int, int)
            Whether the pane is open, its page index, and its vertical
            scroll position.

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
        index, position = self.settings_panel.page_state()
        return self.toolbar.gear.isChecked(), index, position

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
        open_, index, position = state
        self.settings_panel.restore_page_state(index=index, position=position)
        self.toolbar.gear.setChecked(open_)
        self.settings_pane.set_open(open_)

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
        self.settings_panel.show_question(
            q,
            empty_sample=empty_sample,
            scheduler_mode=scheduler_mode,
            self_grading=self_grading,
        )
        named_meter = self.question_view.show_question(
            q,
            answer_width=self.control_area.answers.maximumWidth(),
            empty_queue=empty_sample is not None,
        )
        self.question_view.update_placement()
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
        Let a newly mounted staff pass the mouse wheel to the editor.

        Parameters
        ----------
        widget : QWidget
            Display staff or editor created for the current question.

        Examples
        --------
        Scrolling over the written staff turns the key fork.
        """
        if isinstance(widget, StaffWidget):
            widget.installEventFilter(self)

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

    def _show_placement_actions(self) -> None:
        """
        Let Place and Answer work when they can, and switch the editor's
        keys on for the questions that use them.

        Place does the next thing, and Answer takes over from it once
        everything is placed. For a key signature on the fork only
        Answer shows.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import KeySignatureConstruction
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> (
        ...     all(bound.isEnabled() for bound in view._arrow_keys),
        ...     any(bound.isEnabled() for bound in view._letter_keys),
        ... )
        (True, False)
        """
        music = self.question_view
        q = music.displayed_question
        if q is None:
            return
        self.control_area.answers.placement.show_actions(
            q,
            live=music.accepts_input,
            sequence=music.scale_input if q.places_sequence else None,
            beats=music.active_beat_editor,
        )
        for key in self._arrow_keys:
            key.setEnabled(music.editor is not None)
        for key in self._letter_keys:
            key.setEnabled(music.accepts_letters)

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
        if q is not None:
            self.control_area.answers.show_selection(q, parts=parts)

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
            answers = self.control_area.answers
            for button in answers.buttons_for(q, selected=(choice,)):
                button.setEnabled(False)
                self._request_fade(answers.fade(button))
            if self.question_view.circle is not None:
                self.question_view.circle.set_subtitle("and its other name")

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
        answers = self.control_area.answers
        buttons = self.control_area.feedback_buttons(result, q=q)
        self.question_view.show_result(result)
        if result.correct:
            if kind == "choice" and q.required:
                for button in buttons:
                    button.setEnabled(False)
            if mode == "Immediately":
                for button in buttons:
                    answers.mark(button, color=CORRECT_ANSWER_COLOR)
            else:
                if mode == "Wait":
                    answers.disable_choices()
                for button in buttons:
                    self._request_fade(answers.fade(button))
                if self.question_view.circle is not None:
                    self.question_view.circle.reveal()
        else:
            self._show_incorrect(result, buttons=buttons)
        self.question_view.update_placement()
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
        fade = self.question_view.answer_fade(result.kind, target="#c62828")
        if fade is not None:
            self._request_fade(fade)
        elif result.kind == "signature":
            self.question_view.scale_input.set_note_color(QColor("#c62828"))
        elif result.kind == "pair":
            for button in buttons:
                self._request_fade(
                    self.control_area.answers.fade(
                        button,
                        target="#c62828",
                    ),
                )
        elif result.kind == "choice":
            for button in buttons:
                button.clearFocus()
                button.setEnabled(False)
                self._request_fade(
                    self.control_area.answers.fade(
                        button,
                        target="#c62828",
                    ),
                )
        elif result.kind in ("notation", "midi"):
            self.question_view.show_prompt(f"Try again. {q.prompt}")
        if self.session.answered:
            self.control_area.answers.disable_choices()

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
            self.control_area.answers.clear_selection()
        self.question_view.update_placement()

    def show_silent_feedback(self) -> None:
        """
        Animate an answer that has no sounding notes.

        Examples
        --------
        A correct clef placement flashes the clef symbol.
        """
        fade = self.question_view.silent_fade()
        if fade is not None:
            self._request_fade(fade)
