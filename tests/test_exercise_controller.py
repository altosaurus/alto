"""Independent practice controller and display behavior."""

import random

import pytest
from PySide6.QtCore import QAbstractAnimation
from PySide6.QtTest import QSignalSpy

from alto.exercises.base import Question
from alto.exercises.library import BeatIdentification, NoteNames
from alto.theory.pitch import Note
from alto.ui import motion
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.exercise_controller import AnswerResult, ExerciseController
from alto.ui.exercise_feedback import ExerciseFeedback
from alto.ui.exercise_view import ExerciseView


def test_grade_pair_once_without_a_view() -> None:
    """Grade an octave-first pair once."""
    controller = ExerciseController(NoteNames(), rng=random.Random(1))
    controller.set_next_question_mode("Wait")
    controller.next_question()
    controller.question = Question(
        "",
        choices=["C", "D"],
        answer="C4",
        octaves=["4", "5"],
    )
    graded = QSignalSpy(controller.graded)
    controller.select_part("octave", "9")
    controller.submit_scale([], [])
    assert not controller.pending and controller.session.attempts == 0
    controller.select_part("octave", "4")
    assert not controller.session.answered and graded.count() == 0
    controller.select_part("name", "C")
    controller.select_part("name", "D")
    assert graded.count() == 1 and controller.session.correct == 1
    assert graded.at(0)[0].selected == ("C", "4")
    controller.feedback_finished(0)
    assert not controller._advance.isActive()


def test_retry_callback_cannot_reset_a_replacement_question() -> None:
    """Replacing a wrong pair discards its pending retry."""
    controller = ExerciseController(NoteNames(), rng=random.Random(1))
    controller.set_next_question_mode("Wait")
    controller.next_question()
    controller.question = Question(
        "",
        choices=["C", "D"],
        answer="C4",
        octaves=["4", "5"],
    )
    reset = QSignalSpy(controller.retry_ready)
    controller.select_part("name", "D")
    controller.select_part("octave", "4")
    assert controller.busy
    controller.next_question()
    motion.settle()
    assert reset.count() == 0 and not controller.busy


@pytest.mark.usefixtures("app")
def test_passive_view_emits_input_without_grading() -> None:
    """A standalone display reports a click without grading it."""
    view = ExerciseView(NoteNames())
    assert view.question_view.displayed_question is None
    question = Question("", choices=["C", "D"], answer="C")
    view.show_question(question)
    selected = QSignalSpy(view.control_area.answers.choice_selected)
    view.question_view.key_action("up")
    assert selected.count() == 0
    view.control_area.answers.buttons[0].click()
    assert selected.at(0) == ["C"]
    assert view.session.attempts == 0
    assert view.question_view.displayed_question is question
    view.show_result(AnswerResult("choice", True, "C", ("C",)), "Wait")
    assert (
        CORRECT_ANSWER_COLOR
        in view.control_area.answers.buttons[0].styleSheet()
    )


@pytest.mark.usefixtures("app")
def test_controller_connects_displayed_choices_to_grading() -> None:
    """An attached display receives questions and sends answers back."""
    controller = ExerciseController(BeatIdentification(), rng=random.Random(1))
    view = ExerciseView(controller.exercise)
    controller.connect_view(view)
    view.settings_panel.next_question_mode = "Wait"
    controller.next_question()
    question = controller.question
    assert (
        question is not None
        and view.question_view.displayed_question is question
    )
    buttons = view.control_area.answers.buttons
    buttons[question.choices.index(question.answer)].click()
    assert view.session == controller.session and view.session.correct == 1
    (fade,) = controller.animations.tracked
    assert fade.state() == QAbstractAnimation.State.Running
    view.show_question(question)
    assert not controller.animations.tracked
    assert fade.state() == QAbstractAnimation.State.Stopped


@pytest.mark.usefixtures("app")
def test_late_feedback_on_an_empty_display() -> None:
    """Ignore feedback after the last question leaves the screen."""
    view = ExerciseView(NoteNames())
    music = view.question_view
    music.update_placement()
    music.pick_accidental(1)
    music.move_caret(1)
    music.place_here()
    music.enter_midi_note(Note.parse("C4"))
    music.show_result(AnswerResult("note", False, "C", hint="Try again"))
    music.reset_placement("note")
    assert music.placement_hint == ""
    view.show_selection({"name": "C"})
    view.show_result(AnswerResult("choice", True, "C"), "Wait")
    view.show_retry("pair")
    view.show_silent_feedback()
    view.question_view.light_answer_notes(None)
    view.control_area.answers.placement.answer_button.click()
    assert (
        view.question_view.displayed_question is None
        and view.session.attempts == 0
    )
    notice = Question("No reviews due.", choices=[], answer="")
    sample = Question("Name the note.", choices=["C"], answer="C")
    view.show_question(notice, empty_sample=sample)
    view.show_result(AnswerResult("notation", False, "C"), "Wait")
    assert view.question_view.displayed_question is notice
    assert view.question_view.interactive_question is None
    assert view.question_view.prompt.text() == notice.prompt


@pytest.mark.usefixtures("app")
def test_playback_requires_a_correct_answer_and_current_question() -> None:
    """Ignore late or incorrect feedback before starting playback."""
    controller = ExerciseController(NoteNames(), rng=random.Random(1))
    view = ExerciseView(controller.exercise)
    feedback = ExerciseFeedback(view, controller=controller)
    feedback.play(AnswerResult("choice", True, "C"), mode="Wait")
    assert feedback.generation == -1
    controller.next_question()
    feedback.play(AnswerResult("choice", False, "D"), mode="Wait")
    assert feedback.generation == -1


@pytest.mark.usefixtures("app")
def test_new_question_stops_controller_owned_fades() -> None:
    """Stop a running fade before displaying the next question."""
    controller = ExerciseController(NoteNames(), rng=random.Random(1))
    controller.next_question()
    controller.animations.fade(lambda _value: None)
    (animation,) = controller.animations.tracked
    assert animation.parent() is controller.animations
    assert animation.state() == QAbstractAnimation.State.Running
    controller.next_question()
    assert animation.state() == QAbstractAnimation.State.Stopped
    assert not controller.animations.tracked
