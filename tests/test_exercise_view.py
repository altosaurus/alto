"""
The exercise screen: the sound and settings buttons, placing notes on
the staff, and what is ignored.
"""

from __future__ import annotations

import ast
import operator
import random
from dataclasses import replace
from fractions import Fraction
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from PySide6.QtCore import QEvent, Qt
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
    ScaleConstruction,
)
from alto.learning import Database, Learner
from alto.theory.pitch import Note
from alto.ui import motion
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.exercise_page import ExercisePage
from alto.ui.exercise_settings import load_exercise_settings
from alto.ui.key_fork import KeyFork
from alto.ui.pictures import ValuePictures
from alto.ui.settings_menu import ChoiceChecklist, ToggleRow
from alto.ui.staff_input import ScaleInput, StaffInput
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
) -> ExercisePage:
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
    ExercisePage
        The view, showing its first question.
    """
    return ExercisePage(exercise, rng=random.Random(seed), learner=learner)


def asked(view: ExercisePage) -> Question:
    """
    Return the question on screen (there is always one).

    Parameters
    ----------
    view : ExercisePage
        The view.

    Returns
    -------
    Question
        The question on screen.
    """
    assert view.question is not None
    return view.question


def test_question_view_mounts_only_the_current_question_widgets(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Reuse matching editors and retire them when the display changes.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Supply different question types to the same view.
    """
    view = view_of(NoteNames())
    question_view = view.question_view
    staff = question_view.staff
    assert staff is not None and staff.parentWidget() is question_view
    assert (
        question_view.editor is None
        and question_view.findChild(StaffInput) is None
    )
    rng = random.Random(1)
    note = NoteConstruction().generate(rng)
    scale = ScaleConstruction().generate(rng)
    keyboard = replace(KeyboardNotes().generate(rng), key_staff=True, key=2)
    questions = iter((note, note, scale, keyboard, asked(view)))
    monkeypatch.setattr(view.controller, "_pick_question", questions.__next__)

    view.next_question()
    editor = question_view.editor
    assert (
        type(editor) is StaffInput and editor.parentWidget() is question_view
    )
    assert question_view.staff is None and staff.isHidden()
    submissions = QSignalSpy(question_view.note_submitted)
    view.next_question()
    assert question_view.editor is editor and note.construct is not None
    editor.placed.emit(note.construct)
    assert submissions.count() == 1 and view.session.answered
    view.next_question()
    assert isinstance(question_view.editor, ScaleInput) and editor.isHidden()
    editor.placed.emit(note.construct)
    assert submissions.count() == 1 and not view.session.answered
    view.next_question()
    assert question_view.editor is None and question_view.staff is None
    assert (
        question_view.keyboard is not None
        and question_view.key_staff is not None
    )
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert question_view.findChild(StaffInput) is None
    view.next_question()
    assert question_view.staff is not None
    assert question_view.keyboard is None and question_view.key_staff is None


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
    view.toolbar.set_sound_enabled(sounds.enabled)
    assert (
        "mute)" in view.toolbar.sound_btn.toolTip()
        and view.toolbar.sound_btn.toolTip().startswith("Sound on")
    )
    view.toolbar.sound_btn.click()
    assert not sounds.enabled and view.toolbar.sound_btn.toolTip().startswith(
        "Muted",
    )
    view.toolbar.sound_btn.click()
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
    wrong = next(
        b
        for b in view.control_area.answers.buttons
        if b.text() != before.answer
    )
    right = next(
        b
        for b in view.control_area.answers.buttons
        if b.text() == before.answer
    )
    wrong.click()
    assert (
        view.session.missed
        and not view.session.answered
        and view.control_area.next_button.isHidden()
    )
    with patch.object(sounds, "_play_sequence") as play:
        right.click()
        play.assert_called_once()
        on_step = play.call_args.kwargs["on_step"]
        on_step(0)
        if mode == "Immediately":
            assert (
                not view.question_view.staff.column_colors
                and CORRECT_ANSWER_COLOR in right.styleSheet()
            )
        else:
            assert (
                view.question_view.staff.column_colors[0].name()
                == CORRECT_ANSWER_COLOR
            )
            assert not view.controller._advance.isActive()
            on_step(None)
            assert not view.question_view.staff.column_colors
    if mode == "Wait":
        for animation in view.controller.animations.tracked:
            animation.setCurrentTime(animation.duration())
        assert (
            view.control_area.next_button.isVisible()
            and not view.controller._advance.isActive()
        )
        assert (
            asked(view) is before
            and CORRECT_ANSWER_COLOR in right.styleSheet()
        )
        view.control_area.next_button.click()
    else:
        assert (
            view.control_area.next_button.isHidden()
            and view.controller._advance.isActive()
        )
        motion.settle()  # the next question comes
    assert (
        asked(view) is not before
        and view.control_area.next_button.isHidden()
        and not view.session.answered
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
        view.control_area.answers.buttons[
            question.choices.index(question.answer)
        ].click()
        assert (
            play.call_count == 1 and not view.question_view.staff.column_colors
        )
        motion.settle()  # the next question comes
        assert asked(view) is not question
        assert QSignalSpy(view.feedback.immediate_playback.step).wait(2000)
        assert [call.args[0] for call in play.call_args_list] == [
            [n.midi for n in column] for column in question.staff
        ]
        assert (
            not view.question_view.staff.column_colors
            and not view.controller._advance.isActive()
        )
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
    fork = view.question_view.editor
    assert isinstance(fork, KeyFork)
    q = asked(view)
    fork.set_value(q.key, slide=False)
    view.control_area.answers.placement.answer_button.click()
    assert view.session.answered
    if mode == "Wait":
        assert (
            not view.controller._advance.isActive()
            and not view.control_area.next_button.isHidden()
        )
        for animation in view.controller.animations.tracked:
            animation.setCurrentTime(animation.duration())
        assert (
            CORRECT_ANSWER_COLOR
            in view.control_area.answers.placement.answer_button.styleSheet()
        )
        view.control_area.next_button.click()
        assert (
            not view.control_area.answers.placement.answer_button.styleSheet()
        )
    else:
        assert (
            not view.controller.animations.tracked
            and CORRECT_ANSWER_COLOR
            in view.control_area.answers.placement.answer_button.styleSheet()
        )

    settings.notation.question_type = "staff"
    store().setValue("nextQuestion/NotationIdentification", mode)
    view = view_of(NotationIdentification())
    view.submit(asked(view).answer, button=None)
    assert view.session.answered
    assert view.controller._advance.isActive() == (mode == "Immediately")
    assert bool(view.controller.animations.tracked) == (mode == "Wait")


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
    assert (
        not view.settings_pane.isVisible()
        and view.settings_pane.maximumWidth() == 0
    )
    view.toolbar.gear.setChecked(True)
    view._pane_anim.setCurrentTime(view._pane_anim.duration())
    assert (
        view.settings_pane.isVisible()
        and view.settings_pane.maximumWidth() == view.settings_panel.PANE_WIDTH
    )
    view.toolbar.gear.setChecked(False)
    view._pane_anim.setCurrentTime(view._pane_anim.duration())
    assert (
        view.settings_pane.maximumWidth() == 0
        and not view.settings_pane.isVisible()
    )


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
    arpeggios = view_of(ArpeggioNames())
    assert arpeggios.toolbar.book_btn is None
    assert arpeggios.reference_pane is None
    view = view_of(CircleOfFifths())
    book = view.toolbar.book_btn
    assert book is not None and book.toolTip() == "Reference"
    view.resize(900, 700)
    view.show()
    assert book.parentWidget() is view.toolbar
    assert view.toolbar.score is view.toolbar.score
    assert (
        view.toolbar.help_btn.geometry().right()
        < book.geometry().left()
        < view.toolbar.sound_btn.geometry().left()
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
    assert (
        view.toolbar.book_btn is not None and view.reference_pane is not None
    )
    settings_slide = view._pane_anim
    reference_slide = view._reference_anim
    view.toolbar.gear.setChecked(True)
    settings_slide.setCurrentTime(settings_slide.duration())
    assert view.settings_pane.maximumWidth() == view.settings_panel.PANE_WIDTH
    view.toolbar.book_btn.setChecked(True)
    reference_slide.setCurrentTime(reference_slide.duration())
    settings_slide.setCurrentTime(settings_slide.duration())
    assert (
        view.reference_pane.maximumWidth()
        == view.reference_pane.REFERENCE_WIDTH
    )
    assert (
        view.reference_pane.isVisible() and not view.toolbar.gear.isChecked()
    )
    assert (
        view.settings_pane.maximumWidth() == 0
        and view.settings_pane.isHidden()
    )
    view.toolbar.gear.setChecked(True)
    assert not view.toolbar.book_btn.isChecked()
    reference_slide.setCurrentTime(reference_slide.duration())
    settings_slide.setCurrentTime(settings_slide.duration())
    assert view.reference_pane.maximumWidth() == 0
    assert view.reference_pane.isHidden() and view.settings_pane.isVisible()
    view.close()


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
    assert [b.toolTip() for b in view.control_area.answers.buttons] == [
        f"Key {i + 1}" for i in range(len(view.control_area.answers.buttons))
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
    assert [
        b.toolTip() for b in arpeggio.control_area.answers.buttons
    ] == first + second


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
    assert view.toolbar.score.text() == "0/0 (–)   streak 0"
    q = asked(view)
    wrong = next(
        b for b in view.control_area.answers.buttons if b.text() != q.answer
    )
    right = next(
        b for b in view.control_area.answers.buttons if b.text() == q.answer
    )
    wrong.click()
    right.click()
    assert (
        view.toolbar.score.text() == "0/1 (0%)   streak 0"
    )  # the miss counted, the later right answer did not
    right.click()  # answered already: ignored
    assert (view.session.correct, view.session.total) == (0, 1)
    view.controller._advance.stop()


# -- placing a note on the staff
# ----------------------------------------------------------------------


@pytest.fixture
def construction(app: QApplication) -> ExercisePage:
    """
    Build a note construction view with accidentals on and no key
    signature.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.

    Returns
    -------
    ExercisePage
        The view.
    """
    settings.construction.accidentals = True
    settings.construction.key_signature = False
    return view_of(NoteConstruction(), seed=4)


def test_a_construction_question_shows_the_staff_to_click_and_the_sign_buttons(
    construction: ExercisePage,
) -> None:
    """
    Check that a construction question shows the staff to click and the
    sign buttons.

    Parameters
    ----------
    construction : ExercisePage
        The note construction view or panel under test.
    """
    q = asked(construction)
    assert q.construct is not None and construction.question_view.staff is None
    assert construction.question_view.note_input.isVisibleTo(
        construction,
    ) and construction.question_view.accidental_row.isVisibleTo(construction)
    assert construction.question_view.accidental_buttons.keys() == {-1, 0, 1}


def test_the_sign_buttons_act_like_a_radio_group_that_can_be_cleared(
    construction: ExercisePage,
) -> None:
    """
    Check that the sign buttons act like a radio group that can be
    cleared.

    Parameters
    ----------
    construction : ExercisePage
        The note construction view or panel under test.
    """
    sharp, flat = (
        construction.question_view.accidental_buttons[1],
        construction.question_view.accidental_buttons[-1],
    )
    sharp.click()
    assert (
        sharp.isChecked()
        and construction.question_view.note_input.accidental == 1
    )
    flat.click()
    assert (
        flat.isChecked()
        and not sharp.isChecked()
        and construction.question_view.note_input.accidental == -1
    )
    flat.click()  # the lit one again: no sign
    assert (
        not flat.isChecked()
        and construction.question_view.note_input.accidental is None
    )


def test_right_click_steps_through_the_signs(
    construction: ExercisePage,
) -> None:
    """
    Check that right click steps through the signs.

    Parameters
    ----------
    construction : ExercisePage
        The note construction view or panel under test.
    """
    seen = []
    for _ in range(4):
        construction.question_view.note_input.accidental_cycled.emit()
        seen.append(construction.question_view.note_input.accidental)
    assert seen == [
        1,
        -1,
        None,
        1,
    ]  # with no key signature, a natural is the same as no sign
    construction.question.key = 2
    construction.question_view.note_input.accidental = -1
    construction.question_view.note_input.accidental_cycled.emit()
    assert (
        construction.question_view.note_input.accidental == 0
    )  # under a key signature there is a natural too
    construction.question_view.note_input.accidental_cycled.emit()
    assert construction.question_view.note_input.accidental is None
    # noinspection PyUnreachableCode
    construction.question_view.note_input.accidental = (
        99  # something outside the cycle starts it again
    )
    # noinspection PyUnreachableCode
    construction.question_view.note_input.accidental_cycled.emit()
    # noinspection PyUnreachableCode
    assert construction.question_view.note_input.accidental is None


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
    view.question_view.note_input.accidental_cycled.emit()
    assert view.question_view.note_input.accidental == 1
    other = view_of(KeySignatures())
    other.question_view.cycle_accidental()


@pytest.mark.parametrize("has_sound", [True, False])
def test_placing_the_right_note_scores_locks_the_staff_and_moves_on(
    construction: ExercisePage,
    has_sound: bool,
) -> None:
    """
    Check that placing the right note scores locks the staff and moves
    on.

    Parameters
    ----------
    construction : ExercisePage
        The note construction view or panel under test.
    has_sound : bool
        Whether the exercise plays the placed note.
    """
    q = asked(construction)
    assert q.construct is not None
    first = q
    construction.controller.exercise.has_sound = has_sound
    construction.question_view.note_input.caret = q.construct.diatonic
    construction.question_view.note_input.accidental = q.construct.accidental
    construction.question_view.note_input.place_caret()
    assert construction.session.answered and (
        construction.session.correct,
        construction.session.total,
    ) == (1, 1)
    assert construction.question_view.note_input.locked
    assert construction.controller._advance.isActive() == (not has_sound)
    if has_sound:
        assert construction.question_view.note_input.columns == [[q.construct]]
        assert (
            construction.question_view.note_input.column_colors[0].name()
            == "#2e7d32"
        )
    construction.question_view.note_input.placed.emit(
        q.construct,
    )  # a second click on the same question is ignored
    assert construction.session.total == 1
    construction.controller._advance.stop()
    construction.next_question()
    assert (
        construction.question is not first
        and not construction.question_view.note_input.locked
    )


def test_a_wrong_note_is_shown_then_cleared_for_another_try(
    construction: ExercisePage,
) -> None:
    """
    Check that a wrong note is shown then cleared for another try.

    Parameters
    ----------
    construction : ExercisePage
        The note construction view or panel under test.
    """
    q = asked(construction)
    assert q.construct is not None
    wrong = Note(q.construct.octave, letter=(q.construct.letter + 1) % 7)
    construction.question_view.note_input.placed.emit(wrong)
    assert (
        construction.session.missed
        and not construction.session.answered
        and construction.question_view.busy
        and construction.session.total == 1
    )
    construction.question_view.note_input.placed.emit(
        q.construct,
    )  # while the miss is showing, clicks are ignored
    assert not construction.session.answered
    motion.settle()
    assert (
        not construction.question_view.busy
        and not construction.question_view.note_input.locked
        and construction.question_view.note_input.columns == []
    )
    construction.question_view.note_input.placed.emit(q.construct)
    assert construction.session.answered and (
        construction.session.correct,
        construction.session.total,
    ) == (0, 1)  # still a miss overall
    construction.controller._advance.stop()


def test_a_new_question_cancels_the_clearing_of_the_old_one(
    construction: ExercisePage,
) -> None:
    """
    Check that a new question cancels the clearing of the old one.

    Parameters
    ----------
    construction : ExercisePage
        The note construction view or panel under test.
    """
    q = asked(construction)
    # noinspection PyUnresolvedReferences
    construction.question_view.note_input.placed.emit(
        Note(q.construct.octave, letter=(q.construct.letter + 2) % 7),
    )
    construction.next_question()  # before the 900 ms are up
    assert not construction.question_view.busy
    QTest.qWait(
        1000,
    )  # the old timer fires and must leave the new question alone
    assert (
        not construction.question_view.note_input.locked
        and not construction.question_view.busy
    )


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
    view.question_view.note_submitted.emit(Note(4, letter=0))
    assert view.session.total == 0


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
    names = {b.text(): b for b in view.control_area.answers.buttons}
    wrong = next(t for t in q.choices if t != kind)
    names[wrong].click()
    names[inversion].click()  # a wrong pair: a miss is showing
    assert view.question_view.busy
    names[kind].click()
    assert (
        view.controller.pending.get("name") is not None
        and view.controller.pending["name"] == wrong
    )  # ignored while busy
    motion.settle()
    names[kind].click()
    names[inversion].click()
    assert view.session.answered
    other = next(t for t in q.choices if t != kind)
    names[other].click()
    assert view.controller.pending["name"] == kind  # ignored once answered
    view.controller._advance.stop()


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
    names = {b.text(): b for b in view.control_area.answers.buttons}
    first, second = asked(view).choices[:2]
    names[first].click()
    names[second].click()
    assert names[second].isChecked() and not names[first].isChecked()
    view.controller._advance.stop()


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
    wrong = next(
        b for b in view.control_area.answers.buttons if b.text() != q.answer
    )
    if keyboard:
        wrong.setFocus()
        QTest.keyClick(wrong, Qt.Key.Key_Space)
    else:
        QTest.mouseClick(wrong, Qt.MouseButton.LeftButton)
    assert view.session.missed and not wrong.isEnabled()
    assert app.focusWidget() is None
    right = next(
        b for b in view.control_area.answers.buttons if b.text() == q.answer
    )
    clicked = QSignalSpy(right.clicked)
    QTest.keySequence(view, right.shortcut())
    assert clicked.count() or clicked.wait(1000)
    assert view.session.answered
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
    right = next(
        b for b in view.control_area.answers.buttons if b.text() == q.answer
    )
    right.click()
    animation = view.controller.animations.tracked[-1]
    animation.setCurrentTime(animation.duration())
    assert view.question_view.staff.column_colors[0].name() == "#2e7d32"
    assert "#2e7d32" in right.styleSheet()
    view.controller._advance.stop()


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
        assert (
            not view.question_view.staff.column_colors
            and view.question_view.staff.note_color is None
        )
        for index in range(len(q.staff)):
            on_step(index)
            assert (
                list(view.question_view.staff.column_colors) == [index]
                and view.question_view.staff.column_colors[index].name()
                == "#2e7d32"
            )
            assert not view.controller._advance.isActive()
        on_step(None)
        assert (
            not view.question_view.staff.column_colors
            and view.controller._advance.isActive()
        )
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
    assert (
        view.settings_panel is not None
        and view.question_view.keyboard.isVisibleTo(
            view,
        )
    )
    q = asked(view)
    assert q.keyboard is not None
    original = view.question_view.keyboard.highlight_color
    with patch.object(sounds, "_play_sequence") as play:
        next(
            b
            for b in view.control_area.answers.buttons
            if b.text() == q.answer
        ).click()
        on_step = play.call_args.kwargs["on_step"]
        assert view.question_view.keyboard.highlight_color == original
        on_step(0)
        assert (
            view.question_view.keyboard.highlight == q.keyboard.midi
            and view.question_view.keyboard.highlight_color.name() == "#2e7d32"
        )
        on_step(None)
        assert (
            view.question_view.keyboard.highlight_color == original
            and view.controller._advance.isActive()
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
    view.controller.exercise.has_sound = True
    with patch.object(sounds, "play_correct") as cue:
        next(
            b
            for b in view.control_area.answers.buttons
            if b.text() == asked(view).answer
        ).click()
        cue.assert_called_once_with(1)
    assert (
        view.controller._advance.isActive()
        and not view.question_view.staff.column_colors
    )
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
    right = next(
        b for b in view.control_area.answers.buttons if b.text() == q.answer
    )
    right.click()
    view.submit(
        q.answer,
        button=right,
    )  # the button is disabled and the question answered
    # The shared recording path also rejects a duplicate graded answer.
    view.controller.record(True, choice=q.answer)
    assert db.conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 1
    assert view.session.attempts == 1
    assert (view.session.correct, view.session.total) == (1, 1)
    view.controller._advance.stop()


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
    names = {b.text(): b for b in view.control_area.answers.buttons}
    names[wrong].click()
    names[inversion].click()
    assert view.question_view.busy
    view.next_question()  # before the 700 ms are up
    QTest.qWait(800)  # the old timer fires and finds its question gone
    assert not view.question_view.busy and view.controller.pending == {}
    view.controller._advance.stop()


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
    staff = view.question_view.staff
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
    assert (
        view.question_view.note_input.width()
        == view.question_view.note_input.maximumWidth()
        < 1000
    )
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
        and view.question_view.rhythm_equation.isVisible()
        and view.question_view.prompt.isHidden()
    )
    assert view.question_view.rhythm_terms.count() == 5
    assert all(
        not button.icon().isNull()
        for button in view.control_area.answers.buttons
    )
    view.control_area.answers.buttons[
        question.choices.index(question.answer)
    ].click()
    assert view.session.answered
    assert "blank" not in view.question_view.rhythm_equation.accessibleName()
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
                item = view.question_view.rhythm_terms.itemAt(index)
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
    assert (
        view.question_view.prompt.isVisible()
        and not view.question_view.rhythm_equation.isVisible()
    )
    view.close()


@pytest.mark.usefixtures("app")
def test_keyboard_feedback_colors_the_key_during_the_flash() -> None:
    """A keyboard question uses the staff feedback color on its key."""
    view = view_of(KeyboardNotes())
    view._flash(None, target="#c62828", staff=True)
    animation = view.controller.animations.tracked[-1]
    animation.setCurrentTime(animation.duration())
    assert view.question_view.keyboard.highlight_color.name() == "#c62828"
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
    shared_signature = view.controller.exercise.settings_signature()
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
    split_signature = view.controller.exercise.settings_signature()
    assert split_signature != shared_signature
    first, second = asked(view).prompt.split(" = ")
    assert " + " in first and " × " in second
    left.boxes["×"].click()
    left.boxes["+"].click()
    right.boxes["+"].click()
    right.boxes["×"].click()
    assert view.controller.exercise.settings_signature() != split_signature
    first, second = asked(view).prompt.split(" = ")
    assert " × " in first and " + " in second
    settings.rhythm_left_operators = 0
    right_only = view.controller.exercise.settings_signature()
    settings.rhythm_left_signs = settings.rhythm_right_signs.copy()
    assert view.controller.exercise.settings_signature() == right_only
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
    original = view.controller.exercise.settings_signature()
    right.setValue(2)
    left.setValue(0)
    question = asked(view)
    assert question.prompt.split()[1] == "="
    assert view.controller.exercise.settings_signature() != original
    assert view.question_view.rhythm_terms.count() == len(
        question.prompt.split(),
    )
    app.processEvents()
    assert (
        view.question_view.rhythm_scroll.viewport().height()
        >= view.question_view.rhythm_equation.height()
    )
    view.question_view.rhythm_scroll.setFixedWidth(
        view.question_view.rhythm_equation.width() // 2,
    )
    app.processEvents()
    assert view.question_view.rhythm_scroll.horizontalScrollBar().maximum() > 0
    assert (
        view.question_view.rhythm_scroll.height()
        > view.question_view.rhythm_equation.height()
    )
    view.control_area.answers.buttons[
        question.choices.index(question.answer)
    ].click()
    assert (
        view.session.answered
        and "blank" not in view.question_view.rhythm_equation.accessibleName()
    )
    ungrouped = view.controller.exercise.settings_signature()
    switch.click()
    assert switch.isOn() and settings.rhythm_parentheses
    assert view.controller.exercise.settings_signature() != ungrouped
    assert not view.session.answered
    settings.rhythm_parentheses = False
    settings.rhythm_left_operators, settings.rhythm_right_operators = 1, 0
    load_exercise_settings()
    assert (
        settings.rhythm_left_operators,
        settings.rhythm_right_operators,
    ) == (0, 2)
    assert settings.rhythm_parentheses
    switch.click()
    assert view.controller.exercise.settings_signature() == ungrouped
    left.setValue(1)
    right.setValue(0)
    assert view.controller.exercise.settings_signature() == original
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
        view.question_view.prompt.text() == q.caption
        and q.caption in exercise.card_prompt(q)
    )
    assert [b.text() for b in view.control_area.answers.buttons] == q.choices
    assert all(
        b.icon().isNull() and b.toolTip() == f"Key {b.text()}"
        for b in view.control_area.answers.buttons
    )
    view.control_area.answers.buttons[q.choices.index(q.answer)].click()
    item = view.question_view.rhythm_terms.itemAt(q.prompt.split().index("_"))
    assert item is not None
    label = item.widget()
    assert isinstance(label, QLabel) and label.text() == q.answer
    assert view.session.answered
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
