"""Audio and onset timing for graded exercise answers."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from alto.audio import DEFAULT_NOTE_GAP_MS, MELODIC_INTERVAL_GAP_MS, sounds
from alto.exercises.library import (
    BEAT_METERS,
    BeatConstruction,
    ScaleIdentification,
)
from alto.ui.exercise_controller import AnswerResult, ExerciseController
from alto.ui.staff_playback import StaffPlayback

SCALE_GAP_MS = 280


class ExerciseFeedback(QObject):
    """
    Play answer audio and publish the onset to highlight.

    Examples
    --------
    A melodic interval highlights its two notes at successive onsets.
    """

    highlight = Signal(object)
    silent_feedback = Signal()

    def __init__(
        self,
        owner: QWidget,
        *,
        controller: ExerciseController,
    ) -> None:
        """
        Tie both playback channels to the page lifetime.

        Parameters
        ----------
        owner : QWidget
            Widget whose visibility controls playback.
        controller : ExerciseController
            Practice controller for the displayed exercise.

        Examples
        --------
        Immediate playback can continue as the next question appears.
        """
        super().__init__(owner)
        self.controller = controller
        self.playback = StaffPlayback(owner)
        self.immediate_playback = StaffPlayback(owner)
        self.playback.step.connect(self.step)
        self.generation = -1
        controller.starting.connect(self.cancel)

    def cancel(self) -> None:
        """
        Cancel synchronized feedback when its question is replaced.

        Examples
        --------
        Changing settings stops the synchronized sample for the old
        question.
        """
        self.generation = -1
        self.playback.stop()

    def step(self, index: int | None) -> None:
        """
        Publish onsets and tell the controller when feedback ends.

        Parameters
        ----------
        index : int or None
            Sounding column, or None when playback ends.

        Examples
        --------
        The end of a scale clears its last highlight before advancing.
        """
        controller = self.controller
        q = controller.question
        if (
            self.generation != controller.generation
            or not q
            or not controller.session.answered
        ):
            return
        self.highlight.emit(index)
        if index is None:
            if isinstance(controller.exercise, BeatConstruction):
                delay = 0
            else:
                delay = (
                    400
                    if q.construct_scale is not None
                    or isinstance(controller.exercise, ScaleIdentification)
                    else 150
                )
            controller.feedback_finished(delay)

    def play(
        self,
        result: AnswerResult,
        *,
        mode: str,
        sound_key: str | None = None,
        fingerboard_gap: int | None = None,
    ) -> None:
        """
        Play the graded answer using the exercise instrument and
        tempo.

        Parameters
        ----------
        result : AnswerResult
            Outcome of the submitted answer.
        mode : str
            Selected Next Question behavior.
        sound_key : str or None
            Instrument sample shown in the question.
        fingerboard_gap : int or None
            Spacing between onsets for an instrument diagram.

        Examples
        --------
        A muted rhythm still sends each onset to the display.
        """
        controller = self.controller
        exercise = controller.exercise
        q = controller.question
        if not result.correct or q is None:
            return
        self.generation = controller.generation
        immediate = mode == "Immediately"
        playback = self.immediate_playback if immediate else self.playback
        if isinstance(exercise, BeatConstruction):
            playback.play_rhythm(
                q.rhythm,
                quarter_ms=600 if BEAT_METERS[q.answer][1] == 4 else 400,
            )
            return
        if result.notes and exercise.has_sound:
            scale = q.construct_scale is not None or isinstance(
                exercise,
                ScaleIdentification,
            )
            gap = DEFAULT_NOTE_GAP_MS
            if scale:
                gap = SCALE_GAP_MS
            elif not immediate and fingerboard_gap is not None:
                gap = fingerboard_gap
            elif exercise.interval_voices and len(result.notes) == 2:
                gap = MELODIC_INTERVAL_GAP_MS
            instrument = exercise.sound_instrument(sound_key)
            if immediate and controller.shuffle_answers:
                sounds.play_notes(
                    result.notes,
                    gap_ms=gap,
                    warmup=scale,
                    instrument=instrument,
                )
            else:
                playback.play(
                    result.notes,
                    gap_ms=gap,
                    warmup=scale,
                    instrument=instrument,
                )
            return
        if exercise.has_sound and q.picture is None:
            sounds.play_correct(controller.session.streak)
        if not immediate:
            self.silent_feedback.emit()
            controller.feedback_finished(600)
