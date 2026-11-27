"""
The exercise screen: the sound and settings buttons, placing notes on
the staff, and what is ignored.
"""

from __future__ import annotations

import ast
import operator
import random
from fractions import Fraction
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QLabel, QRadioButton, QSpinBox, QToolButton

from alto import settings
from alto.audio import sounds
from alto.exercises.library import (
    ArpeggioNames,
    ChordQualities,
    CircleOfFifths,
    IntervalNames,
    KeyboardNotes,
    KeySignatureConstruction,
    KeySignatures,
    NotationIdentification,
    NoteConstruction,
    NoteNames,
    RythmicEquations,
)
from alto.learning import Database, Learner
from alto.theory.pitch import Note
from alto.ui import motion
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.exercise_settings import load_exercise_settings
from alto.ui.exercise_view import ExerciseView
from alto.ui.pictures import ValuePictures
from alto.ui.settings_menu import ChoiceChecklist, ToggleRow
from alto.ui.store import store

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from alto.exercises.base import (
        Exercise,
        Question,
    )


def view_of(
    exercise: Exercise,
    *,
    seed: int = 1,
    learner: Learner | None = None,
) -> ExerciseView:
    """
    Build an exercise view with a fixed random source.

    Parameters
    ----------
    exercise : Exercise
        The exercise to ask.
    seed : int
        The random seed.
    learner : Learner or None
        The learner to record answers, if any.

    Returns
    -------
    ExerciseView
        The view, showing its first question.
    """
    return ExerciseView(exercise, rng=random.Random(seed), learner=learner)


def asked(view: ExerciseView) -> Question:
    """
    Return the question on screen (there is always one).

    Parameters
    ----------
    view : ExerciseView
        The view.

    Returns
    -------
    Question
        The question on screen.
    """
    assert view.question is not None
    return view.question


def test_the_speaker_button_mutes_and_unmutes(app: QApplication) -> None:
    """
    Check that the speaker button mutes and unmutes.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(KeySignatures())
    sounds.enabled = True
    view._show_sound_state()
    assert (
        "mute)" in view.sound_btn.toolTip()
        and view.sound_btn.toolTip().startswith("Sound on")
    )
    view.sound_btn.click()
    assert not sounds.enabled and view.sound_btn.toolTip().startswith("Muted")
    view.sound_btn.click()
    assert sounds.enabled


def test_chord_quality_has_buttons_and_next_question_settings(
    app: QApplication,
) -> None:
    """
    Check that chord quality offers its answer-button setting.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(ChordQualities())
    assert (
        view.settings_panel is not None
        and view.settings_panel.choice_buttons_row is not None
    )
    assert view.settings_panel.stack.count() == 3


@pytest.mark.parametrize("mode", ["Immediately", "Wait", "After Animation"])
def test_next_question_paces_interval_feedback(
    app: QApplication,
    mode: str,
) -> None:
    """
    Set the pace from the menu and verify the answer, animation and next
    question.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    mode : str
        The setting selected for Interval Identification.
    """
    view = view_of(IntervalNames())
    view.show()
    panel = view.settings_panel
    before = asked(view)
    panel.next_question_row.click()
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    page = panel.stack.currentWidget()
    radios = page.findChildren(QRadioButton)
    assert [radio.text() for radio in radios] == [
        "Immediately",
        "Wait",
        "After Animation",
    ]
    next(radio for radio in radios if radio.text() == mode).click()
    next(
        button
        for button in page.findChildren(QToolButton)
        if "Back" in button.text()
    ).click()
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    assert panel.stack.currentIndex() == 0
    assert (
        asked(view) is before and panel.next_question_row.value.text() == mode
    )
    assert view_of(IntervalNames()).settings_panel.next_question_mode == mode
    assert (
        view_of(NoteNames()).settings_panel.next_question_mode
        == "After Animation"
    )
    wrong = next(b for b in view.buttons if b.text() != before.answer)
    right = next(b for b in view.buttons if b.text() == before.answer)
    wrong.click()
    assert view.missed and not view.answered and view.next_button.isHidden()
    with patch.object(sounds, "_play_sequence") as play:
        right.click()
        play.assert_called_once()
        on_step = play.call_args.kwargs["on_step"]
        on_step(0)
        if mode == "Immediately":
            assert (
                not view.staff.column_colors
                and CORRECT_ANSWER_COLOR in right.styleSheet()
            )
        else:
            assert view.staff.column_colors[0].name() == CORRECT_ANSWER_COLOR
            assert not view._advance.isActive()
            on_step(None)
            assert not view.staff.column_colors
    if mode == "Wait":
        for animation in view._anims:
            animation.setCurrentTime(animation.duration())
        assert view.next_button.isVisible() and not view._advance.isActive()
        assert (
            asked(view) is before
            and CORRECT_ANSWER_COLOR in right.styleSheet()
        )
        view.next_button.click()
    else:
        assert view.next_button.isHidden() and view._advance.isActive()
        motion.settle()  # the next question comes
    assert (
        asked(view) is not before
        and view.next_button.isHidden()
        and not view.answered
    )


def test_immediate_melody_continues_across_questions(
    app: QApplication,
) -> None:
    """
    Sound the second interval note after the next question appears, with
    no staff highlights.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    store().setValue("nextQuestion/IntervalNames", "Immediately")
    settings.intervals.displays = {"Melodic"}
    view = view_of(IntervalNames())
    view.show()
    sounds.enabled = True
    question = asked(view)
    with (
        patch.object(sounds, "_effect", return_value=object()),
        patch.object(sounds, "_play_column") as play,
    ):
        view.buttons[question.choices.index(question.answer)].click()
        assert play.call_count == 1 and not view.staff.column_colors
        motion.settle()  # the next question comes
        assert asked(view) is not question
        assert QSignalSpy(view._immediate_playback.step).wait(2000)
        assert [call.args[0] for call in play.call_args_list] == [
            [n.midi for n in column] for column in question.staff
        ]
        assert not view.staff.column_colors and not view._advance.isActive()
        view.hide()


@pytest.mark.parametrize("mode", ["Immediately", "Wait"])
def test_next_question_on_construction_and_staff_clicks(
    app: QApplication,
    mode: str,
) -> None:
    """
    Apply the selected pace to a construction and a button-free notation
    answer.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    mode : str
        The saved pace for each exercise.
    """
    store().setValue("nextQuestion/KeySignatureConstruction", mode)
    view = view_of(KeySignatureConstruction())
    q = asked(view)
    view.fork.set_value(q.key, slide=False)
    view.answer_button.click()
    assert view.answered
    if mode == "Wait":
        assert not view._advance.isActive() and not view.next_button.isHidden()
        for animation in view._anims:
            animation.setCurrentTime(animation.duration())
        assert CORRECT_ANSWER_COLOR in view.answer_button.styleSheet()
        view.next_button.click()
        assert not view.answer_button.styleSheet()
    else:
        assert (
            not view._anims
            and CORRECT_ANSWER_COLOR in view.answer_button.styleSheet()
        )

    settings.notation.question_type = "staff"
    store().setValue("nextQuestion/NotationIdentification", mode)
    view = view_of(NotationIdentification())
    view.submit(asked(view).answer, button=None)
    assert view.answered
    assert view._advance.isActive() == (mode == "Immediately")
    assert bool(view._anims) == (mode == "Wait")


def test_the_settings_pane_slides_open_and_shut(app: QApplication) -> None:
    """
    Check that the settings pane slides open and shut.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(NoteNames())
    view.show()
    assert not view.pane.isVisible() and view.pane.maximumWidth() == 0
    view.gear.setChecked(True)
    QTest.qWait(320)
    assert (
        view.pane.isVisible() and view.pane.maximumWidth() == view.PANE_WIDTH
    )
    view.gear.setChecked(False)
    QTest.qWait(320)
    assert view.pane.maximumWidth() == 0 and not view.pane.isVisible()


def test_only_an_exercise_with_a_reference_has_a_book_button(
    app: QApplication,
) -> None:
    """
    Check that the book button is there for the circle of fifths and not
    for an exercise with nothing to look up.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert (
        view_of(ArpeggioNames()).book_btn is None
        and view_of(ArpeggioNames()).reference_pane is None
    )
    view = view_of(CircleOfFifths())
    assert view.book_btn is not None and view.book_btn.toolTip().startswith(
        "Reference",
    )
    view.resize(900, 700)
    view.show()
    assert (
        view.help_btn.geometry().right()
        < view.book_btn.geometry().left()
        < view.sound_btn.geometry().left()
    )


def test_the_reference_pane_slides_open_beside_the_settings_and_shuts_them(
    app: QApplication,
) -> None:
    """
    Check that the reference pane slides open and shut, and that it and
    the settings pane never show together.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(CircleOfFifths())
    view.show()
    assert view.book_btn is not None and view.reference_pane is not None
    view.gear.setChecked(True)
    QTest.qWait(500)
    assert view.pane.maximumWidth() == view.PANE_WIDTH
    view.book_btn.setChecked(True)
    QTest.qWait(500)
    assert view.reference_pane.maximumWidth() == view.REFERENCE_WIDTH
    assert view.reference_pane.isVisible() and not view.gear.isChecked()
    QTest.qWait(500)
    assert view.pane.maximumWidth() == 0
    view.gear.setChecked(True)
    assert not view.book_btn.isChecked()
    QTest.qWait(500)
    assert view.reference_pane.maximumWidth() == 0
    view.gear.setChecked(False)


def test_a_change_in_the_settings_asks_a_new_question_straight_away(
    app: QApplication,
) -> None:
    """
    Check that a change in the settings asks a new question right away.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(NoteNames())
    before = view.question
    assert view.settings_panel is not None
    view.settings_panel.changed.emit()
    assert view.question is not before


def test_the_choices_have_number_key_shortcuts_when_there_are_few_enough(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the choices have number key shortcuts when there are few
    enough, and that a two-part answer has keys too.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Temporarily limit the selected keys.
    """
    monkeypatch.setattr(settings.key_signatures, "keys", {0, 1})
    view = view_of(KeySignatures())
    assert [b.toolTip() for b in view.buttons] == [
        f"Key {i + 1}" for i in range(len(view.buttons))
    ]
    arpeggio = view_of(ArpeggioNames())
    q = arpeggio.question
    assert q is not None and q.octaves is not None
    first = [
        f"Key {i + 1}" for i in range(len(q.choices))
    ]  # the type is on the number keys
    second = [
        f"Key {key}" for key in "ASDFGHJKL"[: len(q.octaves)]
    ]  # and the inversion on the home row
    assert [b.toolTip() for b in arpeggio.buttons] == first + second


def test_the_score_starts_empty_and_counts_only_first_answers(
    app: QApplication,
) -> None:
    """
    Check that the score starts empty and counts only first answers.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(KeySignatures())
    assert view.score.text() == "0/0 (–)   streak 0"
    q = asked(view)
    wrong = next(b for b in view.buttons if b.text() != q.answer)
    right = next(b for b in view.buttons if b.text() == q.answer)
    wrong.click()
    right.click()
    assert (
        view.score.text() == "0/1 (0%)   streak 0"
    )  # the miss counted, the later right answer did not
    right.click()  # answered already: ignored
    assert (view.correct, view.total) == (0, 1)
    view._advance.stop()


# -- placing a note on the staff
# ----------------------------------------------------------------------


@pytest.fixture
def construction(app: QApplication) -> ExerciseView:
    """
    Build a note construction view with accidentals on and no key
    signature.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.

    Returns
    -------
    ExerciseView
        The view.
    """
    settings.construction.accidentals = True
    settings.construction.key_signature = False
    return view_of(NoteConstruction(), seed=4)


def test_a_construction_question_shows_the_staff_to_click_and_the_sign_buttons(
    construction: ExerciseView,
) -> None:
    """
    Check that a construction question shows the staff to click and the
    sign buttons.

    Parameters
    ----------
    construction : ExerciseView
        The note construction view or panel under test.
    """
    q = asked(construction)
    assert q.construct is not None and not construction.staff.isVisibleTo(
        construction,
    )
    assert construction.input_staff.isVisibleTo(
        construction,
    ) and construction.accidental_row.isVisibleTo(construction)
    assert construction.accidental_buttons.keys() == {-1, 0, 1}


def test_the_sign_buttons_act_like_a_radio_group_that_can_be_cleared(
    construction: ExerciseView,
) -> None:
    """
    Check that the sign buttons act like a radio group that can be
    cleared.

    Parameters
    ----------
    construction : ExerciseView
        The note construction view or panel under test.
    """
    sharp, flat = (
        construction.accidental_buttons[1],
        construction.accidental_buttons[-1],
    )
    sharp.click()
    assert sharp.isChecked() and construction.input_staff.accidental == 1
    flat.click()
    assert (
        flat.isChecked()
        and not sharp.isChecked()
        and construction.input_staff.accidental == -1
    )
    flat.click()  # the lit one again: no sign
    assert not flat.isChecked() and construction.input_staff.accidental is None


def test_right_click_steps_through_the_signs(
    construction: ExerciseView,
) -> None:
    """
    Check that right click steps through the signs.

    Parameters
    ----------
    construction : ExerciseView
        The note construction view or panel under test.
    """
    seen = []
    for _ in range(4):
        construction.input_staff.accidental_cycled.emit()
        seen.append(construction.input_staff.accidental)
    assert seen == [
        1,
        -1,
        None,
        1,
    ]  # with no key signature, a natural is the same as no sign
    construction.question.key = 2
    construction.input_staff.accidental = -1
    construction.input_staff.accidental_cycled.emit()
    assert (
        construction.input_staff.accidental == 0
    )  # under a key signature there is a natural too
    construction.input_staff.accidental_cycled.emit()
    assert construction.input_staff.accidental is None
    # noinspection PyUnreachableCode
    construction.input_staff.accidental = (
        99  # something outside the cycle starts it again
    )
    # noinspection PyUnreachableCode
    construction.input_staff.accidental_cycled.emit()
    # noinspection PyUnreachableCode
    assert construction.input_staff.accidental is None


def test_right_click_cycles_note_construction_signs(app: QApplication) -> None:
    """
    Check that right click cycles signs in Note Construction.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.construction.accidentals = False
    view = view_of(NoteConstruction())
    view.input_staff.accidental_cycled.emit()
    assert view.input_staff.accidental == 1
    other = view_of(KeySignatures())
    other._cycle_accidental()  # not a construction question at all


@pytest.mark.parametrize("has_sound", [True, False])
def test_placing_the_right_note_scores_locks_the_staff_and_moves_on(
    construction: ExerciseView,
    has_sound: bool,
) -> None:
    """
    Check that placing the right note scores locks the staff and moves
    on.

    Parameters
    ----------
    construction : ExerciseView
        The note construction view or panel under test.
    has_sound : bool
        Whether the exercise plays the placed note.
    """
    q = asked(construction)
    assert q.construct is not None
    first = q
    construction.exercise.has_sound = has_sound
    construction.input_staff.caret = q.construct.diatonic
    construction.input_staff.accidental = q.construct.accidental
    construction.input_staff.place_caret()
    assert construction.answered and (
        construction.correct,
        construction.total,
    ) == (1, 1)
    assert construction.input_staff.locked
    assert construction._advance.isActive() == (not has_sound)
    if has_sound:
        assert construction.input_staff.columns == [[q.construct]]
        assert construction.input_staff.column_colors[0].name() == "#2e7d32"
    construction._place(
        q.construct,
    )  # a second click on the same question is ignored
    assert construction.total == 1
    construction._advance.stop()
    construction.next_question()
    assert (
        construction.question is not first
        and not construction.input_staff.locked
    )


def test_a_wrong_note_is_shown_then_cleared_for_another_try(
    construction: ExerciseView,
) -> None:
    """
    Check that a wrong note is shown then cleared for another try.

    Parameters
    ----------
    construction : ExerciseView
        The note construction view or panel under test.
    """
    q = asked(construction)
    assert q.construct is not None
    wrong = Note(q.construct.octave, letter=(q.construct.letter + 1) % 7)
    construction._place(wrong)
    assert (
        construction.missed
        and not construction.answered
        and construction._busy
        and construction.total == 1
    )
    construction._place(
        q.construct,
    )  # while the miss is showing, clicks are ignored
    assert not construction.answered
    motion.settle()
    assert (
        not construction._busy
        and not construction.input_staff.locked
        and construction.input_staff.columns == []
    )
    construction._place(q.construct)
    assert construction.answered and (
        construction.correct,
        construction.total,
    ) == (0, 1)  # still a miss overall
    construction._advance.stop()


def test_a_new_question_cancels_the_clearing_of_the_old_one(
    construction: ExerciseView,
) -> None:
    """
    Check that a new question cancels the clearing of the old one.

    Parameters
    ----------
    construction : ExerciseView
        The note construction view or panel under test.
    """
    q = asked(construction)
    # noinspection PyUnresolvedReferences
    construction._place(
        Note(q.construct.octave, letter=(q.construct.letter + 2) % 7),
    )
    construction.next_question()  # before the 900 ms are up
    assert not construction._busy
    QTest.qWait(
        1000,
    )  # the old timer fires and must leave the new question alone
    assert not construction.input_staff.locked and not construction._busy


def test_clicks_on_a_question_that_is_not_construction_are_ignored(
    app: QApplication,
) -> None:
    """
    Check that clicks on a question that is not construction are
    ignored.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(KeySignatures())
    view._place(Note(4, letter=0))
    assert view.total == 0


# -- two-part answers: what is ignored
# ----------------------------------------------------------------------


def test_choices_ignored_once_question_answered_or_while_miss(
    app: QApplication,
) -> None:
    """
    Check that choices are ignored once the question is answered or
    while a miss shows.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(ArpeggioNames(), seed=3)
    q = asked(view)
    kind, inversion = q.answer.split(q.joiner)
    names = {b.text(): b for b in view.buttons}
    wrong = next(t for t in q.choices if t != kind)
    names[wrong].click()
    names[inversion].click()  # a wrong pair: a miss is showing
    assert view._busy
    names[kind].click()
    assert (
        view._pending.get("name") is not None
        and view._pending["name"][0] == wrong
    )  # ignored while busy
    motion.settle()
    names[kind].click()
    names[inversion].click()
    assert view.answered
    other = next(t for t in q.choices if t != kind)
    names[other].click()
    assert view._pending["name"][0] == kind  # ignored once answered
    view._advance.stop()


def test_choosing_a_different_type_unlights_the_one_before(
    app: QApplication,
) -> None:
    """
    Check that choosing a different type unlights the one before.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(ArpeggioNames(), seed=5)
    names = {b.text(): b for b in view.buttons}
    first, second = asked(view).choices[:2]
    names[first].click()
    names[second].click()
    assert names[second].isChecked() and not names[first].isChecked()
    view._advance.stop()


# -- feedback and the less common orderings
# ----------------------------------------------------------------------


@pytest.mark.parametrize("keyboard", [False, True], ids=["mouse", "space"])
def test_wrong_answer_does_not_focus_another_button(
    app: QApplication,
    keyboard: bool,
) -> None:
    """
    Let the learner choose the next answer after a miss.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    keyboard : bool
        Activate the focused answer with Space or click it with the
        mouse.
    """
    view = view_of(IntervalNames())
    view.show()
    view.activateWindow()
    app.processEvents()
    q = asked(view)
    wrong = next(b for b in view.buttons if b.text() != q.answer)
    if keyboard:
        wrong.setFocus()
        QTest.keyClick(wrong, Qt.Key.Key_Space)
    else:
        QTest.mouseClick(wrong, Qt.MouseButton.LeftButton)
    assert view.missed and not wrong.isEnabled()
    assert app.focusWidget() is None
    right = next(b for b in view.buttons if b.text() == q.answer)
    clicked = QSignalSpy(right.clicked)
    QTest.keySequence(view, right.shortcut())
    assert clicked.count() or clicked.wait(1000)
    assert view.answered
    view.close()


def test_a_right_answer_fades_the_staff_notes_to_green(
    app: QApplication,
) -> None:
    """
    Check that a right answer fades the staff notes to green.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(NoteNames(), seed=2)
    q = asked(view)
    right = next(b for b in view.buttons if b.text() == q.answer)
    right.click()
    animation = view._anims[-1]
    animation.setCurrentTime(animation.duration())
    assert view.staff.column_colors[0].name() == "#2e7d32"
    assert "#2e7d32" in right.styleSheet()
    view._advance.stop()


@pytest.mark.parametrize("exercise", [ArpeggioNames, ChordQualities])
def test_staff_feedback_follows_the_played_notes(
    app: QApplication,
    exercise: type[Exercise],
) -> None:
    """
    Highlight only the sounding column of an arpeggio or chord,
    including after a delayed start.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    exercise : type of Exercise
        The exercise that supplies the written and played notes.
    """
    view = view_of(exercise())
    q = asked(view)
    with patch.object(sounds, "_play_sequence") as play:
        view.submit(q.answer, button=None)
        assert [midis for midis, _ in play.call_args.kwargs["steps"]] == [
            [n.midi for n in col] for col in q.staff
        ]
        on_step = play.call_args.kwargs["on_step"]
        assert not view.staff.column_colors and view.staff.note_color is None
        for index in range(len(q.staff)):
            on_step(index)
            assert (
                list(view.staff.column_colors) == [index]
                and view.staff.column_colors[index].name() == "#2e7d32"
            )
            assert not view._advance.isActive()
        on_step(None)
        assert not view.staff.column_colors and view._advance.isActive()
    view.close()


def test_a_right_answer_lights_the_sounding_key(app: QApplication) -> None:
    """
    Highlight the identified key between its playback onset and
    completion.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(KeyboardNotes(), seed=2)
    assert view.settings_panel is not None and view.keyboard.isVisibleTo(view)
    q = asked(view)
    assert q.keyboard is not None
    original = view.keyboard.highlight_color
    with patch.object(sounds, "_play_sequence") as play:
        next(b for b in view.buttons if b.text() == q.answer).click()
        on_step = play.call_args.kwargs["on_step"]
        assert view.keyboard.highlight_color == original
        on_step(0)
        assert (
            view.keyboard.highlight == q.keyboard.midi
            and view.keyboard.highlight_color.name() == "#2e7d32"
        )
        on_step(None)
        assert (
            view.keyboard.highlight_color == original
            and view._advance.isActive()
        )
    view.close()


@pytest.mark.parametrize("mode", ["Immediately", "After Animation"])
def test_correct_cue_without_playable_notes(
    app: QApplication,
    mode: str,
) -> None:
    """
    Keep the ordinary correct-answer cue when a sound-enabled question
    has no pitches.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    mode : str
        The automatic advancement setting.
    """
    store().setValue("nextQuestion/KeySignatures", mode)
    view = view_of(KeySignatures())
    view.exercise.has_sound = True
    with patch.object(sounds, "play_correct") as cue:
        next(b for b in view.buttons if b.text() == asked(view).answer).click()
        cue.assert_called_once_with(1)
    assert view._advance.isActive() and not view.staff.column_colors
    view.close()


def test_a_second_submit_after_the_question_is_answered_is_ignored(
    app: QApplication,
) -> None:
    """
    Check that a second submit after the question is answered is
    ignored.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    view = view_of(KeySignatures(), seed=2, learner=learner)
    q = asked(view)
    right = next(b for b in view.buttons if b.text() == q.answer)
    right.click()
    view.submit(
        q.answer,
        button=right,
    )  # the button is disabled and the question answered
    # The shared recording path also rejects a duplicate graded answer.
    view._record(True, choice=q.answer)
    assert db.conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 1
    assert view.session.attempts == 1
    assert (view.correct, view.total) == (1, 1)
    view._advance.stop()


def test_a_wrong_pair_clears_itself_unless_a_new_question_has_come(
    app: QApplication,
) -> None:
    """
    Check that a wrong pair clears itself unless a new question has
    come.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(ArpeggioNames(), seed=3)
    q = asked(view)
    kind, inversion = q.answer.split(q.joiner)
    wrong = next(t for t in q.choices if t != kind)
    names = {b.text(): b for b in view.buttons}
    names[wrong].click()
    names[inversion].click()
    assert view._busy
    view.next_question()  # before the 700 ms are up
    QTest.qWait(800)  # the old timer fires and finds its question gone
    assert not view._busy and view._pending == {}
    view._advance.stop()


# -- the music stays a readable size in a wide window
# -----------------------------------------------------------------


def test_in_a_wide_window_the_staff_is_capped_and_centered(
    app: QApplication,
) -> None:
    """
    Check that in a wide window the staff is capped and centered.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = view_of(NoteNames(), seed=2)
    view.resize(2400, 700)
    view.show()
    QTest.qWait(50)
    staff = view.staff
    assert (
        staff.width() == staff.maximumWidth() < 1000
    )  # a single note is not spread over the whole window
    parent = staff.parentWidget()
    assert parent is not None
    left, right = staff.x(), parent.width() - staff.x() - staff.width()
    assert left > 200 and abs(left - right) <= 2  # centered
    view.hide()


def test_the_staff_for_placing_a_note_is_capped_too(app: QApplication) -> None:
    """
    Check that the staff for placing a note is capped too.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.construction.accidentals = False
    view = view_of(NoteConstruction(), seed=4)
    view.resize(2400, 700)
    view.show()
    QTest.qWait(50)
    assert view.input_staff.width() == view.input_staff.maximumWidth() < 1000
    view.hide()


@pytest.mark.parametrize("ties", [False, True])
@pytest.mark.parametrize("operator", ["+", "−", "×", "÷"])
def test_rythmic_equations_show_and_fill_the_missing_note(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    operator: str,
    ties: bool,
) -> None:
    """
    Check the equation arithmetic and fill the visual blank through an
    answer button.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Isolates the operator selection.
    operator : str
        The operator under test.
    ties : bool
        Whether the generator may use tied notes.
    """
    monkeypatch.setattr(settings, "rhythm_left_signs", {operator})
    monkeypatch.setattr(settings, "rhythm_ties", ties)
    exercise = RythmicEquations()
    rng = random.Random(2)
    factors, tie_states = set(), set()
    for _ in range(60):
        question = exercise.generate(rng)
        left, shown_operator, right, _, result = question.prompt.replace(
            "_",
            question.answer,
        ).split()
        assert shown_operator == operator
        a, b, c = (
            int(term)
            if term.isdecimal()
            else sum(
                settings.RHYTHM_DURATIONS[value] for value in term.split("~")
            )
            for term in (left, right, result)
        )
        assert {"+": a + b, "−": a - b, "×": a * b, "÷": a / b}[operator] == c
        tie_states.add("~" in question.prompt)
        assert "~" not in question.answer
        if operator in {"×", "÷"}:
            factor = question.prompt.split()[2]
            assert factor.isdecimal()
            factors.add(int(factor))
    assert tie_states == ({False, True} if ties else {False})
    if operator in {"×", "÷"}:
        assert len(factors) > 1 and factors <= set(range(2, 9))
        if ties:
            assert 3 in factors
    view = view_of(exercise)
    view.show()
    app.processEvents()
    question = view.question
    assert (
        question is not None
        and view.rhythm_equation.isVisible()
        and view.prompt.isHidden()
    )
    assert view.rhythm_terms.count() == 5
    assert all(not button.icon().isNull() for button in view.buttons)
    view.buttons[question.choices.index(question.answer)].click()
    assert view.answered
    assert "blank" not in view.rhythm_equation.accessibleName()
    view.close()


def test_rhythm_settings_apply_symbols_and_grouped_notes(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Exercise the saved controls and render questions with a tie or a
    beam.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Keep exercise settings local to this test.
    """
    monkeypatch.setattr(
        settings,
        "rhythm_left_signs",
        settings.DEFAULT_RHYTHM_OPERATORS.copy(),
    )
    monkeypatch.setattr(
        settings,
        "rhythm_symbols",
        settings.DEFAULT_RHYTHM_SYMBOLS.copy(),
    )
    monkeypatch.setattr(settings, "rhythm_ties", False)
    monkeypatch.setattr(settings, "rhythm_beams", False)
    exercise = RythmicEquations()
    view = view_of(exercise)
    view.show()
    panel = view.settings_panel
    checklists = panel.findChildren(ChoiceChecklist)
    operators = next(
        listing
        for listing in checklists
        if listing.accessibleName() == "Left operators"
    )
    symbols = next(
        listing for listing in checklists if "dotted-quarter" in listing.boxes
    )
    operators.boxes["−"].click()
    symbols.boxes["dotted-quarter"].click()
    assert exercise.settings_signature()
    assert store().value("rythmicEquations/leftSigns") == "+"
    assert "dotted-quarter" in str(store().value("rythmicEquations/symbols"))
    switches = {
        control.toolTip(): control for control in panel.findChildren(ToggleRow)
    }
    for kind, marker in (("tied", "~"), ("beamed", "|")):
        switch = switches[f"Show two {kind} notes as one duration"]
        switch.click()
        assert exercise.settings_signature()
        for _ in range(50):
            view.next_question()
            question = view.question
            assert question is not None
            if marker in question.prompt:
                index = next(
                    index
                    for index, term in enumerate(question.prompt.split())
                    if marker in term
                )
                item = view.rhythm_terms.itemAt(index)
                assert item is not None
                picture = item.widget()
                assert (
                    isinstance(picture, ValuePictures)
                    and not picture.grab().isNull()
                )
                break
        else:
            pytest.fail(f"No {kind} question")
        switch.click()
    for name, box in symbols.boxes.items():
        if name != "quarter":
            box.setChecked(False)
    question = view.question
    assert question is not None and question.choices == []
    assert view.prompt.isVisible() and not view.rhythm_equation.isVisible()
    view.close()


@pytest.mark.usefixtures("app")
def test_keyboard_feedback_colors_the_key_during_the_flash() -> None:
    """A keyboard question uses the staff feedback color on its key."""
    view = view_of(KeyboardNotes())
    view._flash(None, target="#c62828", staff=True)
    animation = view._anims[-1]
    animation.setCurrentTime(animation.duration())
    assert view.keyboard.highlight_color.name() == "#c62828"
    view.close()


@pytest.mark.motion
def test_settle_waits_for_a_real_timer(app: QApplication) -> None:
    """
    Return after a delayed feedback step has actually run.

    Parameters
    ----------
    app : QApplication
        Owns the timer and processes its events.
    """
    completed: list[bool] = []
    motion.later(15, owner=app, step=lambda: completed.append(True))
    motion.settle()
    assert completed == [True]


def _equation_value(tokens: list[str]) -> Fraction:
    """
    Evaluate the printed notation with standard arithmetic precedence.

    Parameters
    ----------
    tokens : list of str
        One completed side of a generated equation.

    Returns
    -------
    Fraction
        The exact duration of that side.
    """
    text = []
    signs = {"−": "-", "÷": "/", "×": "*", "+": "+", "(": "(", ")": ")"}
    for token in tokens:
        if token in signs or token.isdecimal():
            text.append(signs.get(token, token))
        else:
            duration = sum(
                settings.RHYTHM_DURATIONS[n]
                for n in token.replace("|", "~").split("~")
            )
            text.append(str(duration))

    def value(node: ast.expr) -> Fraction:
        """
        Evaluate an arithmetic node from the printed expression.

        Parameters
        ----------
        node : ast.expr
            A number or a binary operation.

        Returns
        -------
        Fraction
            The value of this expression.
        """
        if isinstance(node, ast.Constant):
            assert isinstance(node.value, (int, float))
            return Fraction(node.value)
        assert isinstance(node, ast.BinOp)
        operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        return operations[type(node.op)](value(node.left), value(node.right))

    return value(ast.parse(" ".join(text), mode="eval").body)


@pytest.mark.parametrize("parentheses", [False, True])
@pytest.mark.parametrize(
    ("left_signs", "right_signs"),
    [
        (set(settings.RHYTHM_OPERATORS), set(settings.RHYTHM_OPERATORS)),
        ({"+", "÷"}, {"−", "×"}),
    ],
)
def test_rhythm_equations_use_exact_counts_and_balance(
    monkeypatch: pytest.MonkeyPatch,
    parentheses: bool,
    left_signs: set[str],
    right_signs: set[str],
) -> None:
    """
    Check the printed equation at every supported pair of counts.

    Parameters
    ----------
    parentheses : bool
        Whether to allow grouping on each side.
    left_signs, right_signs : set of str
        Signs enabled on the respective sides.
    monkeypatch : pytest.MonkeyPatch
        Isolates the options used to generate the equations.
    """
    monkeypatch.setattr(settings, "rhythm_parentheses", parentheses)
    exercise = RythmicEquations()
    rng = random.Random(591)
    monkeypatch.setattr(
        settings,
        "rhythm_symbols",
        set(settings.RHYTHM_DURATIONS),
    )
    monkeypatch.setattr(settings, "rhythm_ties", True)
    monkeypatch.setattr(settings, "rhythm_beams", True)
    monkeypatch.setattr(settings, "rhythm_left_signs", left_signs)
    monkeypatch.setattr(settings, "rhythm_right_signs", right_signs)
    saw_parentheses = False
    for left in range(settings.MAX_RHYTHM_OPERATORS + 1):
        monkeypatch.setattr(settings, "rhythm_left_operators", left)
        for right in range(settings.MAX_RHYTHM_OPERATORS + 1):
            monkeypatch.setattr(settings, "rhythm_right_operators", right)
            for _ in range(15):
                question = exercise.generate(rng)
                tokens = question.prompt.split()
                assert tokens.count("_") == 1
                tokens[tokens.index("_")] = question.answer
                split = tokens.index("=")
                a, b = tokens[:split], tokens[split + 1 :]
                assert sum(t in settings.RHYTHM_OPERATORS for t in a) == left
                assert sum(t in settings.RHYTHM_OPERATORS for t in b) == right
                assert (
                    set(a).intersection(settings.RHYTHM_OPERATORS)
                    <= left_signs
                )
                assert (
                    set(b).intersection(settings.RHYTHM_OPERATORS)
                    <= right_signs
                )
                assert _equation_value(a) == _equation_value(b)
                saw_parentheses |= "(" in tokens
    assert saw_parentheses == parentheses


def test_rhythm_operator_selections_migrate_and_reload(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Load shared signs, edit each side, and restore independent choices.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Isolates the rhythm settings.
    """
    for side in ("left", "right"):
        monkeypatch.setattr(settings, f"rhythm_{side}_signs", set())
        monkeypatch.setattr(settings, f"rhythm_{side}_operators", 1)
    saved = store()
    saved.setValue("rythmicEquations/leftOperators", "invalid")
    saved.setValue("rythmicEquations/operators", "+,×")
    saved.setValue("rythmicEquations/rightOperators", 1)
    load_exercise_settings()
    view = view_of(RythmicEquations())
    lists = {
        listing.accessibleName(): listing
        for listing in view.settings_panel.findChildren(ChoiceChecklist)
        if "+" in listing.boxes
    }
    left, right = lists["Left operators"], lists["Right operators"]
    assert left.selected() == right.selected() == {"+", "×"}
    shared_signature = view.exercise.settings_signature()
    left.boxes["×"].click()
    load_exercise_settings()
    assert settings.rhythm_left_signs == {"+"}
    assert settings.rhythm_right_signs == {"+", "×"}
    right.boxes["+"].click()
    assert not right.boxes["×"].isEnabled()
    assert not left.boxes["+"].isEnabled()
    load_exercise_settings()
    assert settings.rhythm_left_signs == {"+"}
    assert settings.rhythm_right_signs == {"×"}
    split_signature = view.exercise.settings_signature()
    assert split_signature != shared_signature
    first, second = asked(view).prompt.split(" = ")
    assert " + " in first and " × " in second
    left.boxes["×"].click()
    left.boxes["+"].click()
    right.boxes["+"].click()
    right.boxes["×"].click()
    assert view.exercise.settings_signature() != split_signature
    first, second = asked(view).prompt.split(" = ")
    assert " × " in first and " + " in second
    settings.rhythm_left_operators = 0
    right_only = view.exercise.settings_signature()
    settings.rhythm_left_signs = settings.rhythm_right_signs.copy()
    assert view.exercise.settings_signature() == right_only
    view.close()


def test_rhythm_count_fields_refresh_the_question_and_reload(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Edit both fields, solve the new question, and reload the counts.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Isolates the global operator counts.
    """
    monkeypatch.setattr(settings, "rhythm_left_operators", 1)
    monkeypatch.setattr(settings, "rhythm_right_operators", 0)
    monkeypatch.setattr(settings, "rhythm_parentheses", False)
    view = view_of(RythmicEquations())
    view.show()
    switch = next(
        row
        for row in view.settings_panel.findChildren(ToggleRow)
        if row.switch.accessibleName() == "Parentheses"
    )
    assert not switch.isOn()
    fields = {
        field.accessibleName(): field
        for field in view.settings_panel.findChildren(QSpinBox)
    }
    left, right = fields["Left operators"], fields["Right operators"]
    assert (left.value(), right.value()) == (1, 0)
    original = view.exercise.settings_signature()
    right.setValue(2)
    left.setValue(0)
    question = asked(view)
    assert question.prompt.split()[1] == "="
    assert view.exercise.settings_signature() != original
    assert view.rhythm_terms.count() == len(question.prompt.split())
    app.processEvents()
    assert (
        view.rhythm_scroll.viewport().height() >= view.rhythm_equation.height()
    )
    view.rhythm_scroll.setFixedWidth(view.rhythm_equation.width() // 2)
    app.processEvents()
    assert view.rhythm_scroll.horizontalScrollBar().maximum() > 0
    assert view.rhythm_scroll.height() > view.rhythm_equation.height()
    view.buttons[question.choices.index(question.answer)].click()
    assert (
        view.answered and "blank" not in view.rhythm_equation.accessibleName()
    )
    ungrouped = view.exercise.settings_signature()
    switch.click()
    assert switch.isOn() and settings.rhythm_parentheses
    assert view.exercise.settings_signature() != ungrouped
    assert not view.answered
    settings.rhythm_parentheses = False
    settings.rhythm_left_operators, settings.rhythm_right_operators = 1, 0
    load_exercise_settings()
    assert (
        settings.rhythm_left_operators,
        settings.rhythm_right_operators,
    ) == (0, 2)
    assert settings.rhythm_parentheses
    switch.click()
    assert view.exercise.settings_signature() == ungrouped
    left.setValue(1)
    right.setValue(0)
    assert view.exercise.settings_signature() == original
    view.close()


def test_rhythm_answer_types_mix_persist_and_fill_numeric_blanks(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Select both types, then answer and reload a number-only question.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Isolates the rhythm options.
    """
    monkeypatch.setattr(settings, "rhythm_answer_types", {"symbol"})
    monkeypatch.setattr(
        settings,
        "rhythm_left_signs",
        settings.DEFAULT_RHYTHM_OPERATORS.copy(),
    )
    monkeypatch.setattr(
        settings,
        "rhythm_symbols",
        settings.DEFAULT_RHYTHM_SYMBOLS.copy(),
    )
    exercise = RythmicEquations()
    original = exercise.settings_signature()
    view = view_of(exercise)
    view.show()
    listing = next(
        menu
        for menu in view.settings_panel.findChildren(ChoiceChecklist)
        if "symbol" in menu.boxes
    )
    assert listing.selected() == {"symbol"}
    listing.boxes["number"].click()
    mixed = exercise.settings_signature()
    rng = random.Random(0)
    assert {exercise.generate(rng).answer.isdecimal() for _ in range(30)} == {
        True,
        False,
    }
    listing.boxes["symbol"].click()
    numeric = exercise.settings_signature()
    assert len({original, mixed, numeric}) == 3
    q = asked(view)
    assert q.answer.isdecimal() and all(c.isdecimal() for c in q.choices)
    assert (
        view.prompt.text() == q.caption
        and q.caption in exercise.card_prompt(q)
    )
    assert [b.text() for b in view.buttons] == q.choices
    assert all(
        b.icon().isNull() and b.toolTip() == f"Key {b.text()}"
        for b in view.buttons
    )
    view.buttons[q.choices.index(q.answer)].click()
    item = view.rhythm_terms.itemAt(q.prompt.split().index("_"))
    assert item is not None
    label = item.widget()
    assert isinstance(label, QLabel) and label.text() == q.answer
    assert view.answered
    settings.rhythm_answer_types = {"symbol"}
    load_exercise_settings()
    assert settings.rhythm_answer_types == {"number"}
    listing.boxes["symbol"].click()
    listing.boxes["number"].click()
    assert exercise.settings_signature() == original
    view.close()


@pytest.mark.parametrize("parentheses", [False, True])
def test_numeric_rhythm_blanks_have_one_balancing_answer(
    monkeypatch: pytest.MonkeyPatch,
    parentheses: bool,
) -> None:
    """
    Substitute every numeric button into the printed equation.

    Parameters
    ----------
    parentheses : bool
        Whether to allow grouping on each side.
    monkeypatch : pytest.MonkeyPatch
        Isolates operators, answer types, and the selected note values.
    """
    monkeypatch.setattr(settings, "rhythm_parentheses", parentheses)
    exercise = RythmicEquations()
    rng = random.Random(9)
    monkeypatch.setattr(settings, "rhythm_answer_types", {"number"})
    monkeypatch.setattr(
        settings,
        "rhythm_symbols",
        {"quarter", "half", "eighth"},
    )
    monkeypatch.setattr(settings, "rhythm_ties", True)
    monkeypatch.setattr(settings, "rhythm_beams", True)
    for left_signs, right_signs in (
        ({"+", "−"}, {"+", "−"}),
        ({"×", "÷"}, {"×", "÷"}),
        (set(settings.RHYTHM_OPERATORS), set(settings.RHYTHM_OPERATORS)),
        ({"+", "×"}, {"−", "÷"}),
    ):
        monkeypatch.setattr(settings, "rhythm_left_signs", left_signs)
        monkeypatch.setattr(settings, "rhythm_right_signs", right_signs)
        for left, right in ((0, 0), (0, 1), (1, 0), (3, 2)):
            monkeypatch.setattr(settings, "rhythm_left_operators", left)
            monkeypatch.setattr(settings, "rhythm_right_operators", right)
            for _ in range(12):
                q = exercise.generate(rng)
                tokens = q.prompt.split()
                index = tokens.index("_")
                for c in q.choices:
                    replacement = [c]
                    if q.caption:
                        unit = q.caption.split()[2]
                        replacement = ["(", c, "×", unit, ")"]
                    sides = tokens[:index] + replacement + tokens[index + 1 :]
                    eq = sides.index("=")
                    balanced = _equation_value(sides[:eq]) == _equation_value(
                        sides[eq + 1 :],
                    )
                    assert q.check(c) == balanced
    monkeypatch.setattr(settings, "rhythm_symbols", {"quarter"})
    monkeypatch.setattr(settings, "rhythm_left_signs", {"+"})
    monkeypatch.setattr(settings, "rhythm_left_operators", 1)
    monkeypatch.setattr(settings, "rhythm_right_operators", 0)
    monkeypatch.setattr(settings, "rhythm_ties", False)
    q = exercise.generate(rng)
    assert (q.prompt, q.answer, q.caption) == (
        "quarter + quarter = _",
        "2",
        "Count in quarter notes.",
    )
