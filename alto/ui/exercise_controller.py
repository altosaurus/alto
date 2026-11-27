"""Exercise selection, answer evaluation, and practice timing."""

from __future__ import annotations

import math
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from fsrs import Rating
from PySide6.QtCore import QObject, Qt, QTimer, QVariantAnimation, Signal

from alto import settings
from alto.exercises.base import Exercise, PicturePosition, Question
from alto.exercises.library import (
    BEAT_METERS,
    INTERVAL_INVERSION_PROMPTS,
    BeatConstruction,
    IntervalConstruction,
    IntervalNames,
    NoteNames,
    beat_positions,
)
from alto.learning import Learner
from alto.learning.calendar import (
    CALENDAR_SCHEDULERS,
    DEFAULT_SCHEDULER,
    ReviewInterval,
)
from alto.learning.learner import PracticeComplete
from alto.learning.practice_session import PracticeSession
from alto.theory.beat_placement import grade_beat_marks
from alto.theory.note_naming import note_name
from alto.theory.pitch import Interval, Note
from alto.theory.scales import format_key_signature
from alto.ui import motion
from alto.ui.staff import clef_targets

if TYPE_CHECKING:
    from alto.ui.exercise_view import ExerciseView


@dataclass(frozen=True)
class AnswerResult:
    """
    The judged input and the music to present as feedback.

    Examples
    --------
    A paired answer carries both selected labels for the display.
    """

    kind: str
    correct: bool
    choice: str
    selected: tuple[str, ...] = ()
    notes: list[list[Note]] | None = None
    note: Note | None = None
    reveal_interval: bool = False
    hint: str = ""


class FeedbackAnimations(QObject):
    """
    Manage the feedback fades for one question.

    Examples
    --------
    A new question stops the old fade before reusing a button.
    """

    def __init__(self, parent: QObject) -> None:
        """
        Tie the animations to their practice controller.

        Parameters
        ----------
        parent : QObject
            Owner of the animation lifetime.

        Examples
        --------
        Closing the page releases its feedback animations.
        """
        super().__init__(parent)
        self.tracked: list[QVariantAnimation] = []

    def fade(self, step: Callable[[float], None]) -> None:
        """
        Run a feedback fade from zero to one over 180 milliseconds.

        Parameters
        ----------
        step : callable
            Updates the displayed color at each step.

        Examples
        --------
        A note placement fades from black to its feedback color.
        """
        animation = QVariantAnimation(self)
        animation.setDuration(180)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.valueChanged.connect(step)
        self.tracked.append(animation)
        animation.start()

    def cancel(self) -> None:
        """
        Stop and dispose of all fades for the previous question.

        Examples
        --------
        The next question starts with its normal button colors.
        """
        for animation in self.tracked:
            animation.stop()
            animation.deleteLater()
        self.tracked.clear()


class ExerciseController(QObject):
    """
    Run an exercise independently of its widgets and playback device.

    Attributes
    ----------
    exercise : Exercise
        Active exercise used to generate questions and grade answers.

    Examples
    --------
    A controller can grade a pair of choices without a display.
    """

    question_started = Signal(object, object, str, bool)
    starting = Signal()
    progress_changed = Signal(object, bool)
    queue_changed = Signal(object, object)
    intervals_changed = Signal(object)
    selection_changed = Signal(object)
    partial_answer = Signal(str)
    graded = Signal(object, str)
    retry_ready = Signal(str)
    next_visible = Signal(bool)
    ratings_changed = Signal(object)
    shuffle_requested = Signal()
    midi_note = Signal(object)
    prompt_changed = Signal(str)

    def __init__(
        self,
        exercise: Exercise,
        *,
        rng: random.Random | None = None,
        learner: Learner | None = None,
        parent: QObject | None = None,
    ) -> None:
        """
        Prepare one independent run of an exercise.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose questions and controls are in use.
        rng : random.Random or None
            Random source for question selection.
        learner : Learner or None
            Active profile and scheduler, if any.
        parent : QObject or None
            Qt object that owns this instance.

        Examples
        --------
        A controller with a learner uses that profile’s practice
        queue.
        """
        super().__init__(parent)
        self.animations = FeedbackAnimations(self)
        self.exercise = exercise
        self.rng = rng or random.Random()
        self.learner = learner
        self.session = PracticeSession()
        self.question: Question | None = None
        self.shuffle_answers = False
        self.next_question_mode = "After Animation"
        self._advance = QTimer(self)
        self._advance.setSingleShot(True)
        self._advance.setTimerType(Qt.TimerType.PreciseTimer)
        self._advance.timeout.connect(self.advance)
        self._count_timer = QTimer(self)
        self._count_timer.setInterval(30_000)
        self._count_timer.timeout.connect(self.refresh_counts)
        self._scheduler_mode = DEFAULT_SCHEDULER
        self._self_grading = False
        self._clock = time.monotonic()
        self._timing_valid = True
        self._visible = False
        self._hidden_at: float | None = None
        self._advance_remaining = -1
        self._review_preview: ReviewInterval | None = None
        self._speed_previews: dict[Rating, ReviewInterval] | None = None
        self._rating_previews: dict[Rating, ReviewInterval] = {}
        self.pending: dict[str, str] = {}
        self._found: set[str] = set()
        self._disabled_choices: set[str] = set()
        self.busy = False
        self._waiting = False
        self.generation = 0

    def connect_view(self, view: ExerciseView) -> None:
        """
        Connect learner input and practice updates to the screen.

        Parameters
        ----------
        view : ExerciseView
            Screen built for this controller's exercise.

        Examples
        --------
        A choice goes to the controller for grading. A retry reopens
        the editor on the screen.
        """
        self.set_next_question_mode(
            view.settings_panel.next_question_mode,
        )
        view.settings_panel.next_question_mode_changed.connect(
            self.set_next_question_mode,
        )
        view.settings_panel.changed.connect(self.next_question)
        view.control_area.next_button.clicked.connect(self.advance)
        view.control_area.ratings.rating_requested.connect(
            self.apply_rating,
        )
        view.fade_requested.connect(self.animations.fade)
        view.replacing_question.connect(self.animations.cancel)
        view.destroyed.connect(self.animations.cancel)
        view.visibility_changed.connect(self.set_visible)
        view.control_area.answers.choice_selected.connect(
            self.submit_choice,
        )
        view.control_area.answers.part_selected.connect(self.select_part)
        view.question_view.note_submitted.connect(self.place_note)
        view.question_view.scale_submitted.connect(self.submit_scale)
        view.question_view.clef_submitted.connect(self.submit_clef)
        view.question_view.fork_submitted.connect(self.submit_fork)
        view.question_view.signature_submitted.connect(
            self.submit_signature,
        )
        view.question_view.beats_submitted.connect(self.submit_beats)
        view.question_view.location_selected.connect(self.locate)
        self.progress_changed.connect(view.show_progress)
        self.question_started.connect(view.show_question)
        self.queue_changed.connect(view.show_counts)
        self.intervals_changed.connect(view.question_view.show_intervals)
        self.ratings_changed.connect(
            view.control_area.ratings.show_ratings,
        )
        self.selection_changed.connect(view.show_selection)
        self.partial_answer.connect(view.show_partial)
        self.prompt_changed.connect(view.question_view.show_prompt)
        self.next_visible.connect(
            view.control_area.next_button.setVisible,
        )
        self.midi_note.connect(view.question_view.enter_midi_note)
        self.retry_ready.connect(view.show_retry)
        self.graded.connect(view.show_result)

    def _pick_question(self) -> Question:
        """
        Select the next eligible question for this exercise.

        Returns
        -------
        Question
            Question selected for this presentation.

        Examples
        --------
        A profile can schedule a previously missed card for review.
        """
        if self.learner is None:
            return self.exercise.generate(self.rng)
        avoid = self.question.item_key() if self.question else None
        if (
            self._scheduler_mode in CALENDAR_SCHEDULERS
            and not self.session.missed
        ):
            avoid = None
        return self.learner.pick(self.exercise, rng=self.rng, avoid=avoid)

    def next_question(self) -> None:
        """
        End the previous presentation and publish a question or queue
        notice.

        Examples
        --------
        Changing clefs starts a new question with the updated
        settings.
        """
        self.animations.cancel()
        self.generation += 1
        self.starting.emit()
        self._advance.stop()
        self._advance_remaining = -1
        self._waiting = False
        self._scheduler_mode = (
            self.learner.mode if self.learner else DEFAULT_SCHEDULER
        )
        self._self_grading = bool(
            self.learner
            and self._scheduler_mode in CALENDAR_SCHEDULERS
            and self.learner.self_grading,
        )
        self._rating_previews.clear()
        empty_sample = None
        try:
            q = self._pick_question()
        except PracticeComplete as empty:
            empty_sample = self.exercise.generate(self.rng)
            message = "You’re caught up for now."
            if empty.retry_at is not None:
                clock = time.strftime(
                    "%H:%M:%S",
                    time.localtime(empty.retry_at),
                )
                timed = (
                    self.learner
                    and self.learner.response_times(
                        type(self.exercise).__name__,
                    ).ready
                )
                message = (
                    f"Next review at {clock}."
                    if self._self_grading or timed
                    else "Waiting for a missed card. "
                    f"Practice resumes at {clock}."
                )
                self._advance.start(
                    max(1, math.ceil((empty.retry_at - time.time()) * 1000)),
                )
            q = (
                Question(message, choices=[], answer="")
                if empty_sample.answer
                else empty_sample
            )
        self.question = q if empty_sample is None else None
        self.session = self.session.new_question(
            available=empty_sample is None,
        )
        self._clock = time.monotonic()
        self._timing_valid = True
        self.pending.clear()
        self._found.clear()
        self._disabled_choices.clear()
        self.busy = False
        self.progress_changed.emit(self.session, self.busy)
        self.question_started.emit(
            q,
            empty_sample,
            self._scheduler_mode,
            self._self_grading,
        )
        self.review_intervals()
        self.refresh_counts()

    def advance(self) -> None:
        """
        Advance locally or request the next shuffled exercise.

        Examples
        --------
        In shuffle practice, the window selects the next exercise.
        """
        if self._rating_previews:
            return
        if (
            self.shuffle_answers
            and self.session.answered
            and self.question is not None
        ):
            self.shuffle_requested.emit()
        else:
            self.next_question()

    def set_next_question_mode(self, mode: str) -> None:
        """
        Apply the selected pacing on the next submission.

        Parameters
        ----------
        mode : str
            Selected Next Question option.

        Examples
        --------
        Selecting Wait keeps the current question on screen.
        """
        self.next_question_mode = mode

    def scheduling_changed(self) -> None:
        """
        Recheck availability when the open page can present it.

        Examples
        --------
        A hidden page refreshes its scheduler when it becomes visible.
        """
        if self._visible:
            self.next_question()
        else:
            self._scheduler_mode = ""

    def set_visible(self, visible: bool) -> None:
        """
        Pause or resume an interrupted presentation.

        Parameters
        ----------
        visible : bool
            Whether the learner can see the exercise.

        Examples
        --------
        Returning from a lesson resumes a pending advance timer.
        """
        self._visible = visible
        if not visible:
            self._count_timer.stop()
            if self._hidden_at is None:
                self._timing_valid = False
                self._hidden_at = time.monotonic()
                self._advance_remaining = self._advance.remainingTime()
                self._advance.stop()
            return
        if self._hidden_at is not None:
            self._clock += time.monotonic() - self._hidden_at
            self._hidden_at = None
            if self._advance_remaining >= 0:
                motion.start_timer(
                    self._advance,
                    delay=max(1, self._advance_remaining),
                )
            self._advance_remaining = -1
        if self.learner and (
            self._scheduler_mode != self.learner.mode or self.question is None
        ):
            self.next_question()
        else:
            self.refresh_counts()

    def application_state_changed(self, state: Qt.ApplicationState) -> None:
        """
        Exclude interrupted attempts from speed grading.

        Parameters
        ----------
        state : Qt.ApplicationState
            Application focus state reported by Qt.

        Examples
        --------
        Switching applications excludes the attempt from speed
        grading.
        """
        if state != Qt.ApplicationState.ApplicationActive:
            self._timing_valid = False

    def review_intervals(self) -> None:
        """
        Publish previews and retain the exact intervals offered for
        grading.

        Examples
        --------
        A new card can show the duration of its next review.
        """
        self._review_preview = None
        self._speed_previews = None
        self.intervals_changed.emit(())
        if (
            self._self_grading
            or self.question is None
            or self.learner is None
            or self._scheduler_mode not in CALENDAR_SCHEDULERS
        ):
            return
        exercise = type(self.exercise).__name__
        if self.learner.response_times(exercise).ready:
            self._speed_previews = self.learner.calendar.passing_intervals(
                exercise,
                profile=self.learner.profile.id,
                key=self.question.item_key(),
                mode=self._scheduler_mode,
                now=time.time(),
            )
            self.intervals_changed.emit(
                tuple(
                    f"{grade.name}: {preview.duration}"
                    for grade, preview in self._speed_previews.items()
                ),
            )
        else:
            self._review_preview = self.learner.calendar.correct_interval(
                exercise,
                profile=self.learner.profile.id,
                key=self.question.item_key(),
                mode=self._scheduler_mode,
                now=time.time(),
            )
            self.intervals_changed.emit((self._review_preview.duration,))

    def refresh_counts(self) -> None:
        """
        Publish current calendar queue counts while the page is
        visible.

        Examples
        --------
        Starting a calendar review displays the remaining new cards.
        """
        if (
            self.learner is None
            or self._scheduler_mode not in CALENDAR_SCHEDULERS
        ):
            self.queue_changed.emit(None, None)
            self._count_timer.stop()
        elif self._visible:
            key = (
                self.question.item_key()
                if self.question and self.session.attempts == 0
                else None
            )
            counts, current = self.learner.calendar.study_counts(
                self.exercise,
                profile=self.learner.profile.id,
                mode=self._scheduler_mode,
                now=time.time(),
                current_key=key,
            )
            self.queue_changed.emit(counts, current)
            self._count_timer.start()

    def record(self, ok: bool, *, choice: str = "") -> None:
        """
        Record a graded attempt once with its elapsed active time.

        Parameters
        ----------
        ok : bool
            Whether the submitted answer is correct.
        choice : str
            Submitted answer text.

        Examples
        --------
        A correct retry records a second attempt at the same question.
        """
        progress = self.session.after_attempt(
            ok,
            calendar_review=self._scheduler_mode in CALENDAR_SCHEDULERS,
            shuffle=self.shuffle_answers,
        )
        if progress is self.session:
            return
        now = time.monotonic()
        if self.learner and self.question:
            assigned = self.learner.record(
                self.exercise,
                question=self.question,
                answer=choice,
                correct=ok,
                attempt_no=progress.attempts,
                seconds=now - self._clock,
                preview=self._review_preview,
                passing_previews=self._speed_previews,
                self_grading=self._self_grading,
                timing_valid=self._timing_valid,
            )
            if assigned is not None:
                self.intervals_changed.emit(
                    (f"{assigned.rating.name} · {assigned.duration}",),
                )
            if not ok:
                self.intervals_changed.emit(())
        self.session = progress
        self._clock = now

    def apply_rating(self, rating: Rating) -> None:
        """
        Apply the offered manual review rating and advance.

        Parameters
        ----------
        rating : Rating
            Passing grade chosen by the learner.

        Examples
        --------
        Selecting Easy saves the interval offered for that grade.
        """
        preview = self._rating_previews.get(rating)
        if preview is None or self.learner is None or self.question is None:
            return
        self.learner.calendar.grade(
            type(self.exercise).__name__,
            profile=self.learner.profile.id,
            key=self.question.item_key(),
            mode=self._scheduler_mode,
            correct=True,
            manual_rating=rating,
            now=time.time(),
            preview=preview,
        )
        self._rating_previews.clear()
        self.ratings_changed.emit({})
        self.advance()

    def feedback_finished(self, delay: int) -> None:
        """
        Advance after feedback unless waiting for the learner.

        Parameters
        ----------
        delay : int
            Time in milliseconds after the last feedback onset.

        Examples
        --------
        Wait leaves the completed question visible until the learner
        advances.
        """
        if self._waiting or self._rating_previews or not self.session.answered:
            return
        if self._hidden_at is not None:
            self._advance_remaining = delay
        else:
            motion.start_timer(self._advance, delay=delay)

    def _finish(self, result: AnswerResult) -> None:
        """
        Commit an outcome, publish its feedback, and arrange the next
        action.

        Parameters
        ----------
        result : AnswerResult
            Outcome of the submitted answer.

        Examples
        --------
        A wrong pair in ordinary practice becomes available for a
        retry.
        """
        mode = self.next_question_mode
        self.record(result.correct, choice=result.choice)
        retry = not result.correct and result.kind in (
            "pair",
            "note",
            "scale",
            "clef",
            "fork",
        )
        self.busy = retry
        self.progress_changed.emit(self.session, self.busy)
        self.refresh_counts()
        if result.correct and self._self_grading:
            assert self.learner and self.question
            self._rating_previews = self.learner.calendar.passing_intervals(
                type(self.exercise).__name__,
                profile=self.learner.profile.id,
                key=self.question.item_key(),
                mode=self._scheduler_mode,
                now=time.time(),
            )
            self.ratings_changed.emit(self._rating_previews)
            mode = "Wait"
        self._waiting = (
            self.session.answered and mode == "Wait" and not self._self_grading
        )
        self.next_visible.emit(self._waiting)
        self.graded.emit(result, mode)
        retry_delay = 400 if result.kind == "pair" else 450
        if result.correct:
            if mode == "Immediately":
                self.feedback_finished(
                    90
                    if result.selected
                    or result.kind not in ("notation", "midi")
                    else 0,
                )
        elif self.session.answered:
            self.prompt_changed.emit(
                "Incorrect. This card will return for review."
                if self._scheduler_mode in CALENDAR_SCHEDULERS
                else "Incorrect.",
            )
            immediate = self._self_grading or mode == "Immediately"
            self.feedback_finished(90 if immediate else retry_delay)
        elif retry:
            generation = self.generation

            def reset() -> None:
                """
                Reopen this editor only while its original question is
                active.

                Examples
                --------
                Replacing the question cancels the pending retry for
                the old one.
                """
                if generation != self.generation:
                    return
                self.busy = False
                self.pending.clear()
                self.progress_changed.emit(self.session, False)
                self.retry_ready.emit(result.kind)

            motion.later(
                retry_delay,
                owner=self,
                step=reset,
            )

    def select_part(self, part: str, text: str) -> None:  # noqa: PLR0917 (Qt signal arguments)
        """
        Collect a named choice and its second part in either order.

        Parameters
        ----------
        part : str
            Name of the answer row that produced the selection.
        text : str
            Text to display or the value selected for this part.

        Examples
        --------
        The learner may choose octave 4 before naming a middle C.
        """
        if self.session.answered or self.busy or self.question is None:
            return
        choices = {
            "name": self.question.choices,
            "octave": self.question.octaves,
        }
        if text not in (choices.get(part) or ()):
            return
        self.pending[part] = text
        self.selection_changed.emit(dict(self.pending))
        if "name" in self.pending and "octave" in self.pending:
            selected = (self.pending["name"], self.pending["octave"])
            self.submit_choice(
                self.question.joiner.join(selected),
                kind="pair",
                selected=selected,
            )

    def submit_choice(
        self,
        choice: str,
        *,
        kind: str = "choice",
        selected: tuple[str, ...] = (),
    ) -> None:
        """
        Evaluate a choice or a location submitted by any input device.

        Parameters
        ----------
        choice : str
            Submitted answer text.
        kind : str
            Input that produced this answer.
        selected : tuple[str, ...]
            Choice labels to mark when rendering this result.

        Examples
        --------
        An enharmonic key can require both accepted names.
        """
        q = self.question
        if (
            self.session.answered
            or self.busy
            or q is None
            or (
                kind == "choice"
                and (
                    choice not in q.choices or choice in self._disabled_choices
                )
            )
        ):
            return
        ok = q.check(choice)
        if kind == "choice":
            selected = (choice,)
            if not ok or q.required:
                self._disabled_choices.add(choice)
            if ok and q.required:
                self._found.add(choice)
                if not q.complete(self._found):
                    self.partial_answer.emit(choice)
                    return
                choice = " ".join(q.required)
        notes = q.sounding_columns() if ok else None
        reveal = (
            ok
            and isinstance(self.exercise, IntervalNames)
            and q.prompt in INTERVAL_INVERSION_PROMPTS.values()
            and bool(q.staff)
        )
        if reveal:
            first, second = (note for column in q.staff for note in column)
            low, high = sorted(
                (first, second),
                key=lambda n: (n.diatonic, n.midi),
            )
            raised = high.transpose(Interval.between(low, high=high).inversion)
            if len(q.staff) == 1:
                notes = [[high] if high == raised else [high, raised]]
            else:
                notes = (
                    [[raised], [high]]
                    if first == high and first != second
                    else [[high], [raised]]
                )
        position = q.fingerboard or q.picture
        if ok and isinstance(position, PicturePosition) and position.notes:
            notes = [[Note.parse(name) for name in position.notes]]
        elif ok and position and position.note:
            notes = [[Note.parse(position.note)]]
        self._finish(
            AnswerResult(
                kind,
                ok,
                choice,
                selected,
                notes,
                reveal_interval=reveal,
            ),
        )

    def place_note(self, note: Note) -> None:
        """
        Grade one spelled pitch on the construction staff.

        Parameters
        ----------
        note : Note
            Spelled pitch entered by the learner.

        Examples
        --------
        An interval construction can accept an enharmonic spelling.
        """
        q = self.question
        if not q or q.construct is None or self.session.answered or self.busy:
            return
        ok = q.check_placed(note)
        hint = ""
        if not ok and q.staff:
            signs = (
                range(-2, 3)
                if isinstance(self.exercise, IntervalConstruction)
                else range(-1, 2)
            )
            right = any(
                q.check_placed(
                    Note.from_diatonic(note.diatonic, accidental=sign),
                )
                for sign in signs
            )
            hint = (
                "Check the accidental."
                if right
                else "Check the staff position."
            )
        choice = note_name(
            note,
            naming=settings.note_names.naming,
            key=None if q.notes_only else q.key,
            minor=q.minor,
        )
        self._finish(
            AnswerResult(
                "note",
                ok,
                choice,
                notes=q.placement_columns(note),
                note=note,
                hint=hint,
            ),
        )

    def submit_scale(  # noqa: PLR0917 (Qt signal arguments)
        self,
        notes: list[Note],
        steps: list[str],
    ) -> None:
        """
        Check the notes and optional steps of a completed scale.

        Parameters
        ----------
        notes : list[Note]
            Pitches in the order entered on the staff.
        steps : list[str]
            Whole and half steps marked between notes.

        Examples
        --------
        Scale construction can ask for both notes and whole or half
        steps.
        """
        q = self.question
        if (
            not q
            or q.construct_scale is None
            or self.session.answered
            or self.busy
        ):
            return
        label = " ".join(
            note_name(n, naming=settings.note_names.naming) for n in notes
        )
        if q.construct_steps is not None:
            label += " | " + " ".join(steps)
        self._finish(
            AnswerResult(
                "scale",
                q.check_scale(notes) and q.check_steps(steps),
                label,
                notes=[[n] for n in notes],
            ),
        )

    def submit_clef(self, symbol: str, step: int) -> None:  # noqa: PLR0917 (Qt signal arguments)
        """
        Check the symbol and its position on the staff.

        Parameters
        ----------
        symbol : str
            Clef symbol entered on the staff.
        step : int
            Staff position in diatonic steps from the bottom line.

        Examples
        --------
        A treble clef places the G symbol on the second staff line.
        """
        q = self.question
        if q and q.place_clef and not self.session.answered and not self.busy:
            self._finish(
                AnswerResult(
                    "clef",
                    (symbol, step) in clef_targets(q.place_clef),
                    f"{symbol} clef at {step}",
                ),
            )

    def submit_fork(self, count: int) -> None:
        """
        Check the signed number of accidentals.

        Parameters
        ----------
        count : int
            Signed number of sharps or flats.

        Examples
        --------
        A count of minus two represents a two-flat key signature.
        """
        q = self.question
        if q and q.build_key and not self.session.answered and not self.busy:
            self._finish(
                AnswerResult(
                    "fork",
                    q.check_built(count),
                    format_key_signature(count),
                ),
            )

    def submit_signature(self, notes: list[Note]) -> None:
        """
        Check the signs entered on the signature staff.

        Parameters
        ----------
        notes : list[Note]
            Pitches in the order entered on the staff.

        Examples
        --------
        The submitted staff positions distinguish the chosen
        accidentals.
        """
        q = self.question
        if q and q.place_signature and not self.session.answered:
            choice = " ".join(map(str, notes)) or "No accidentals"
            self._finish(
                AnswerResult("signature", q.check(choice), choice),
            )

    def submit_beats(self, marks: list[int]) -> None:
        """
        Grade the positions marked across the two measures.

        Parameters
        ----------
        marks : list[int]
            Onset positions the learner marked as beats.

        Examples
        --------
        Beat Construction compares marked onsets across both measures.
        """
        q = self.question
        if (
            marks
            and q
            and isinstance(self.exercise, BeatConstruction)
            and not self.session.answered
        ):
            ok, choice = grade_beat_marks(
                marks,
                expected=beat_positions(BEAT_METERS[q.answer]),
            )
            self._finish(AnswerResult("beats", ok, choice))

    def played_pitch(self, pitch: int) -> None:
        """
        Interpret a MIDI note using the active question's pitch
        spelling.

        Parameters
        ----------
        pitch : int
            MIDI note number, including its octave.

        Examples
        --------
        MIDI note 60 can answer a question asking for middle C.
        """
        q = self.question
        if q is None or self.session.answered or self.busy:
            return
        if (
            isinstance(self.exercise, NoteNames)
            and not q.identify_scale
            and q.staff
            and q.staff[0]
        ):
            target = q.staff[0][0]
            self.pending.clear()
            self.selection_changed.emit({})
            prompt = self.exercise.card_prompt(q)
            if pitch % 12 != target.pitch_class or (
                q.octaves and pitch != target.midi
            ):
                played = settings.key_name(pitch)
                self.submit_choice(f"Played {played}", kind="midi")
                if not self.session.answered:
                    self.prompt_changed.emit(
                        f"Played {played}. Try again. {prompt}",
                    )
            else:
                self.prompt_changed.emit(prompt)
                if q.octaves:
                    octave = str(target.octave)
                    self.select_part(
                        "name",
                        q.answer.removesuffix(q.joiner + octave),
                    )
                    self.select_part("octave", octave)
                else:
                    self.submit_choice(q.answer)
        elif q.construct_scale:
            spelling = next(
                (n for n in q.construct_scale if n.pitch_class == pitch % 12),
                None,
            )
            note = (
                replace(
                    spelling,
                    octave=spelling.octave + (pitch - spelling.midi) // 12,
                )
                if spelling
                else Note.parse(settings.key_name(pitch))
            )
            self.midi_note.emit(note)
        elif q.construct is not None:
            note = q.construct
            if note.midi != pitch:
                note = next(
                    (n for n in map(Note.parse, q.accept) if n.midi == pitch),
                    Note.parse(settings.key_name(pitch)),
                )
            self.place_note(note)

    def locate(self, hit: bool) -> None:
        """
        Translate a notation hit test into an answer for the current
        card.

        Parameters
        ----------
        hit : bool
            Whether the pointer hit the requested staff symbol.

        Examples
        --------
        Clicking the requested symbol submits its accepted answer.
        """
        if self.question is not None:
            self.submit_choice(
                self.question.answer if hit else "Incorrect location",
                kind="notation",
            )
