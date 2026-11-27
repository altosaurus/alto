"""Connect an exercise display to its practice controller and audio."""

from __future__ import annotations

import random

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from alto.audio import sounds
from alto.exercises.base import Exercise, Question
from alto.learning import Learner
from alto.ui.exercise_controller import AnswerResult, ExerciseController
from alto.ui.exercise_feedback import ExerciseFeedback
from alto.ui.exercise_view import ExerciseView
from alto.ui.settings_panel import settings_panel_for


class ExercisePage(ExerciseView):
    """
    Assemble the running exercise screen for a window or standalone
    practice.

    Examples
    --------
    The main window creates one page for the selected exercise.
    """

    def __init__(
        self,
        exercise: Exercise,
        *,
        rng: random.Random | None = None,
        learner: Learner | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Connect the components before requesting the first question.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose questions and controls are in use.
        rng : random.Random or None
            Random source for question selection.
        learner : Learner or None
            Active profile and scheduler, if any.
        parent : QWidget or None
            Qt object that owns this instance.

        Examples
        --------
        Opening Note Identification connects its controls before the
        first note.
        """
        controller = ExerciseController(exercise, rng=rng, learner=learner)
        super().__init__(
            controller.exercise,
            settings_panel=settings_panel_for(
                controller.exercise,
                learner=controller.learner,
            ),
            parent=parent,
        )
        controller.setParent(self)
        self.controller = controller
        controller.connect_view(self)
        self.feedback = ExerciseFeedback(self, controller=controller)
        self.toolbar.sound_btn.clicked.connect(self._toggle_sound)
        self.toolbar.set_sound_enabled(sounds.enabled)
        if self.toolbar.midi_input is not None:
            self.toolbar.midi_input.note_pressed.connect(self._place_midi)
        controller.graded.connect(self._play_feedback)
        self.feedback.highlight.connect(self.question_view.light_answer_notes)
        self.feedback.silent_feedback.connect(self.show_silent_feedback)
        app = QGuiApplication.instance()
        if isinstance(app, QGuiApplication):
            app.applicationStateChanged.connect(
                controller.application_state_changed,
            )
        controller.next_question()

    @property
    def question(self) -> Question | None:
        """
        Return the active practice question.

        Returns
        -------
        Question or None
            The controller's question, or None for an empty queue.

        Examples
        --------
        A caller reads the current choices before submitting an answer.
        """
        return self.controller.question

    def _place_midi(self, pitch: int) -> None:
        """
        Use a played pitch to identify a note, place an interval
        endpoint, or enter the next scale note.

        Parameters
        ----------
        pitch : int
            MIDI note number, including its octave.

        Examples
        --------
        Playing MIDI note 67 answers a perfect fifth above C4 with G4.
        """
        if (
            self.isVisible()
            and not QApplication.activeModalWidget()
            and not QApplication.activePopupWidget()
        ):
            self.controller.played_pitch(pitch)

    def _play_feedback(self, result: AnswerResult, mode: str) -> None:  # noqa: PLR0917 (Qt signal arguments)
        """
        Use the instrument sample associated with the displayed
        diagram.

        Parameters
        ----------
        result : AnswerResult
            Outcome of the submitted answer.
        mode : str
            Selected Next Question behavior.

        Examples
        --------
        A pack exercise uses the instrument shown on its fingerboard.
        """
        if result.correct:
            board = self.question_view.fingerboard
            self.feedback.play(
                result,
                mode=mode,
                sound_key=board.sound_key if board else None,
                fingerboard_gap=board.feedback_gap_ms() if board else None,
            )

    def _toggle_sound(self) -> None:
        """
        Apply the shared mute setting and refresh the toolbar.

        Examples
        --------
        Clicking the speaker button toggles the shared playback
        setting.
        """
        sounds.enabled = not sounds.enabled
        self.toolbar.set_sound_enabled(sounds.enabled)

    def next_question(self) -> None:
        """
        Request a fresh question using the current exercise settings.

        Examples
        --------
        Changing clefs starts a new question with the updated
        settings.
        """
        self.controller.next_question()

    def submit(self, choice: str, *, button: QPushButton | None) -> None:
        """
        Submit a choice programmatically through the same path as user
        input.

        Parameters
        ----------
        choice : str
            Submitted answer text.
        button : QPushButton or None
            Choice button or None for a notation answer.

        Examples
        --------
        A caller may submit a notation choice without clicking a
        widget.
        """
        if button is None or button.isEnabled():
            self.controller.submit_choice(
                choice,
                kind="choice" if button is not None else "notation",
            )
