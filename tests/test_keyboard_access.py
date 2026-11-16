"""
Using the exercises without the mouse.

Every answer can be given from the keyboard, and everything that can be done by clicking the staff can be done with buttons
or keys.
"""

from __future__ import annotations

import random

import pytest
from PySide6.QtCore import (
    QEvent,
    QPointF,
    Qt,
)
from PySide6.QtGui import (
    QMouseEvent,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.exercises import REGISTRY
from alto.exercises.base import (
    Exercise,
    Question,
)
from alto.exercises.library import (
    ArpeggioNames,
    KeyboardNotes,
    KeySignatureConstruction,
    NoteConstruction,
    NoteNames,
    ScaleConstruction,
)
from alto.theory.pitch import (
    Note,
    key_accidental,
)
from alto.ui.exercise_view import (
    ExerciseView,
    choice_keys,
    note_name,
    note_words,
    second_row_keys,
)
from alto.ui.home import ExerciseCard
from alto.ui.main_window import MainWindow
from alto.ui.staff_input import (
    ScaleInput,
    StaffInput,
)
from keys import (
    opened,
    press,
)


def reach(
    view: ExerciseView,
    target: Note,
) -> None:
    """
    Move the note that would be placed to a note, using only the keys: its letter, the octave keys, then the sign keys.

    Parameters
    ----------
    view : ExerciseView
        The screen, showing a staff to place notes on.
    target : Note
        The note to reach, with the sign it has to be placed with.

    Raises
    ------
    AssertionError
        If the keys cannot reach it.
    """
    # noinspection PyProtectedMember
    staff = view._input()
    press(view, "ABCDEFG"[(target.letter - 5) % 7])  # the letter: C is 0 in a note, so A is 5
    assert staff.caret is not None
    while target.diatonic - staff.caret >= 7:
        press(view, "PgUp")
    while target.diatonic - staff.caret <= -7:
        press(view, "PgDown")
    for _ in range(5):  # the signs go round in a cycle of four at most
        if staff.caret_note() == target:
            return
        press(view, "Right")
    raise AssertionError(f"could not reach {target}")


# -- the keys of the answer buttons -----------------------------------------------------------------------------------


def test_few_answers_take_the_digits_and_many_take_the_note_names() -> None:
    """
    Check which key each answer gets, for few answers, for the notes of a keyboard, and for any other long list.
    """
    assert choice_keys(["a", "b", "c"]) == ["1", "2", "3"]
    assert choice_keys([str(n) for n in range(9)]) == list("123456789")
    notes = [*"CDEFGAB", "C♯", "D♭", "F♯", "B♭"]
    assert choice_keys(notes) == ["C", "D", "E", "F", "G", "A", "B", "Shift+C", "Ctrl+D", "Shift+F", "Ctrl+B"]
    assert choice_keys([str(n) for n in range(12)]) == [*"123456789", "0", "", ""]
    assert choice_keys([]) == []


def test_the_second_row_never_uses_a_key_of_the_first() -> None:
    """
    Check that the second row of a two-part answer takes the home row beside digits and the digits beside letters.
    """
    assert second_row_keys(["1", "2", "3", "4"], labels=["root", "first", "second", "third"]) == list("ASDF")
    assert second_row_keys(["C", "D", "Shift+C"], labels=["3", "4", "5"]) == ["3", "4", "5"]
    assert second_row_keys(["C", "Shift+C"], labels=["10", "x"]) == ["", ""]  # only a single digit can be typed


@pytest.mark.parametrize("cls", REGISTRY, ids=lambda c: c.name)
def test_every_answer_button_of_every_exercise_has_a_key(
    app: QApplication,
    cls: type[Exercise],
) -> None:
    """
    Check that in every exercise every button that answers has its own key, and that no two buttons share one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    cls : type of Exercise
        The exercise.
    """
    settings.keyboard.require_octave = True  # the largest layout: the piano keys, and the octave row
    view = ExerciseView(cls(), rng=random.Random(2))
    for _ in range(30):
        buttons = [b for b in view.buttons if b.isEnabled()]
        keys = [b.shortcut().toString() for b in buttons]
        assert all(keys), (cls.name, [b.text() for b in buttons if not b.shortcut().toString()])
        assert len(set(keys)) == len(keys), (cls.name, keys)
        view.next_question()


def test_a_key_answers_the_question_in_a_choice_exercise(app: QApplication) -> None:
    """
    Check that pressing the key of the right answer answers it, in an exercise with few answers.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = opened(NoteNames())
    q = view.question
    assert q is not None
    press(view, str(q.choices.index(q.answer) + 1))
    assert view.answered and view.correct == 1
    view._advance.stop()


def test_the_notes_of_a_keyboard_are_typed_by_name(app: QApplication) -> None:
    """
    Check that on the piano keyboard a natural is its letter, a sharp is Shift and the letter, and a flat Ctrl and the letter.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.keyboard.require_octave = False
    view = opened(KeyboardNotes())
    for _ in range(25):
        q = view.question
        assert q is not None
        key = choice_keys(q.choices)[q.choices.index(q.answer)]
        press(view, key)
        assert view.answered, (q.answer, key)
        view._advance.stop()
        view.next_question()
    assert view.correct == 25


def test_the_octave_of_a_keyboard_note_is_typed_as_its_number(app: QApplication) -> None:
    """
    Check that with the octave asked for, the octave is typed as a digit and the name by its letters.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.keyboard.require_octave = True
    view = opened(KeyboardNotes())
    for _ in range(10):
        q = view.question
        assert q is not None and q.octaves is not None
        name, octave = q.answer.split(q.joiner) if q.joiner else (q.answer[:-1], q.answer[-1])
        press(view, choice_keys(q.choices)[q.choices.index(name)])
        press(view, octave)
        assert view.answered, q.answer
        view._advance.stop()
        view.next_question()


def test_a_two_part_answer_is_given_with_the_number_keys_then_the_home_row(app: QApplication) -> None:
    """
    Check that for the arpeggios the type is a digit and the inversion a letter of the home row.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = opened(ArpeggioNames())
    for _ in range(8):
        q = view.question
        assert q is not None and q.octaves is not None
        kind, inversion = q.answer.split(q.joiner)
        press(view, str(q.choices.index(kind) + 1))
        press(view, "ASDF"[q.octaves.index(inversion)])
        assert view.answered, q.answer
        view._advance.stop()
        view.next_question()


# -- the staff, with a caret ------------------------------------------------------------------------------------------


def test_the_caret_starts_in_the_middle_and_moves_by_steps_and_octaves(app: QApplication) -> None:
    """
    Check where the caret starts, how it moves, and that it stays within the ledger lines.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = StaffInput()
    staff.reset("treble")
    assert staff.caret is None and staff.caret_note() is None
    staff.move_cursor(0)
    assert str(staff.caret_note()) == "B4"  # the middle line of the treble staff
    staff.move_cursor(2)
    assert str(staff.caret_note()) == "D5"
    staff.move_cursor(-7)
    assert str(staff.caret_note()) == "D4"
    staff.move_cursor(-1000)
    low = staff.caret
    staff.move_cursor(-1)
    assert staff.caret == low  # no further than the staff can be clicked
    staff.move_cursor(1000)
    high = staff.caret
    staff.move_cursor(1)
    assert staff.caret == high and high is not None and low is not None and high > low
    staff.reset("bass")
    staff.move_cursor(0)
    assert str(staff.caret_note()) == "D3"
    staff.reset("grand")
    staff.move_cursor(0)
    assert str(staff.caret_note()) == "C4"  # middle C, where the two staves meet


def test_a_letter_jumps_to_the_nearest_note_with_that_name(app: QApplication) -> None:
    """
    Check that a letter goes to the nearest note of that name, above or below, and never off the staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = StaffInput()
    staff.reset("treble")
    staff.move_cursor(0)  # B4
    expected = {0: "C5", 1: "D5", 2: "E5", 3: "F4", 4: "G4", 5: "A4", 6: "B4"}  # the nearest of each, above or below
    for letter, name in expected.items():
        staff.jump_to_letter(letter)
        assert str(staff.caret_note()) == name, letter
        staff.reset("treble")
        staff.move_cursor(0)
    low, high = settings.RANGE_LIMITS["treble"]
    for letter in range(7):
        staff.caret = low
        staff.jump_to_letter(letter)
        assert low <= (staff.caret or 0) <= high and (staff.caret or 0) % 7 == letter


def test_the_note_at_the_caret_is_shown_and_takes_the_chosen_sign_and_the_signature(app: QApplication) -> None:
    """
    Check that the caret's note is drawn in the preview colour, follows the sign chosen, and follows the key signature.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = StaffInput()
    staff.reset("treble", key=-2)  # B and E are flat
    staff.resize(600, 330)
    staff.move_cursor(0)  # B
    assert str(staff.caret_note()) == "B♭4" and len(staff.columns) == 1
    staff.accidental = 0
    staff.refresh_preview()
    assert str(staff.caret_note()) == "B4" and staff.columns[0][0].accidental == 0


def test_a_click_leaves_no_caret_behind_and_the_keyboard_carries_on_from_the_last_scale_note(app: QApplication) -> None:
    """
    Check that a mouse user sees no ghost note, and that the keyboard of the scale staff starts from the last note placed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=8)
    staff.resize(900, 330)
    staff.move_cursor(3)
    assert staff.caret is not None
    staff.place_next(Note.parse("D4"))  # a note placed another way: the staff has it
    assert str(Note.from_diatonic(staff.caret_start())) == "D4"
    single = StaffInput()
    single.reset("treble")
    assert single.caret is None
    single.resize(600, 330)
    point = QPointF(50, single.staff_bottoms()["treble"])
    single.mousePressEvent(
        QMouseEvent(
            QEvent.Type.MouseButtonPress,
            point,
            point,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        ),
    )
    assert single.caret is None


# -- placing a note with the keyboard or the buttons ------------------------------------------------------------------


def test_the_note_construction_screen_has_buttons_for_everything_the_staff_does(app: QApplication) -> None:
    """
    Check that the screen shows the buttons that move the note, choose its sign and place it, and the line that says what to do.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.construction.accidentals = True
    view = opened(NoteConstruction())
    assert view.pitch_row.isVisibleTo(view) and view.accidental_row.isVisibleTo(view) and view.place_button.isVisibleTo(view)
    assert not view.step_row.isVisibleTo(view) and not view.answer_button.isVisibleTo(view) and not view.undo_button.isVisible()
    assert [b.text() for b in view.pitch_buttons.values()] == ["Octave ↓", "Lower ↓", "Higher ↑", "Octave ↑"]
    assert view.place_status.isVisibleTo(view) and "Press ↑ or ↓" in view.place_status.text()


def test_a_note_is_placed_with_the_keyboard_alone(app: QApplication) -> None:
    """
    Check that a named note is placed using a letter, the octave keys, the sign keys and Return, with no mouse.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.construction.accidentals = True
    settings.construction.key_signature = True
    view = opened(NoteConstruction())
    for _ in range(12):
        q = view.question
        assert q is not None and q.construct is not None
        reach(view, q.construct)
        press(view, "Return")
        assert view.answered and not view.missed, q.answer
        view._advance.stop()
        view.next_question()
    assert view.correct == 12


def test_a_note_is_placed_with_the_buttons_alone(app: QApplication) -> None:
    """
    Check that the same note is placed by clicking only buttons: Higher, Lower, the octaves, the signs and Place note.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.construction.accidentals = True
    view = ExerciseView(NoteConstruction(), rng=random.Random(5))
    view.resize(1000, 800)
    for _ in range(10):
        q = view.question
        assert q is not None and q.construct is not None
        staff = view.input_staff
        view.pitch_buttons["higher"].click()  # the caret appears at its starting place
        while q.construct.diatonic - (staff.caret or 0) >= 7:
            view.pitch_buttons["octave_up"].click()
        while q.construct.diatonic - (staff.caret or 0) <= -7:
            view.pitch_buttons["octave_down"].click()
        while (staff.caret or 0) < q.construct.diatonic:
            view.pitch_buttons["higher"].click()
        while (staff.caret or 0) > q.construct.diatonic:
            view.pitch_buttons["lower"].click()
        if q.construct.accidental:
            view.accidental_buttons[q.construct.accidental].click()
        view.place_button.click()
        assert view.answered and not view.missed, q.answer
        view._advance.stop()
        view.next_question()
    assert view.correct == 10


def test_a_wrong_note_is_cleared_and_the_caret_comes_back_for_another_try(app: QApplication) -> None:
    """
    Check that after a wrong note the staff clears and the keyboard can try again from where it was.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = opened(NoteConstruction())
    q = view.question
    assert q is not None and q.construct is not None
    press(view, "Up")
    while view.input_staff.caret_note() == q.construct:
        press(view, "Up")  # make sure it is not the note asked for
    caret = view.input_staff.caret
    press(view, "Return")
    assert view.missed and not view.answered and not view.place_button.isEnabled()
    QTest.qWait(1200)
    assert view.place_button.isEnabled() and not view.input_staff.locked
    assert view.input_staff.caret == caret and len(view.input_staff.columns) == 1  # the caret's note is back
    reach(view, q.construct)
    press(view, "Return")
    assert view.answered and view.correct == 0  # only the first try counts toward the score
    view._advance.stop()


def test_the_line_under_the_staff_says_what_comes_next_and_is_spoken_in_words(app: QApplication) -> None:
    """
    Check the line that says what the next press will do, and the same said in words for a screen reader.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.steps = True
    view = opened(ScaleConstruction())
    assert view.place_status.text().startswith("Note 1 of 8: press ↑ or ↓")
    press(view, "G")
    shown, spoken = view._placement_text()
    note = view.scale_input.caret_note()
    assert note is not None and shown == f"Note 1 of 8: {note_name(note)}" and spoken == f"Note 1 of 8: {note_words(note)}"
    assert view.place_status.accessibleDescription() == spoken and view.scale_input.accessibleDescription() == spoken
    assert view.scale_input.accessibleName() == "Staff: place the scale"
    q = view.question
    assert q is not None and q.construct_scale is not None
    for note in q.construct_scale:
        reach(view, note)
        press(view, "Return")
    assert view.place_status.text().startswith("Step 1 of 7: W") and "whole step" in view.place_status.accessibleDescription()
    for step in q.construct_steps or []:
        press(view, step)
        press(view, "Return")
    assert view.place_status.text() == "Everything is placed. Press Return to answer."


def test_notes_are_spoken_with_their_signs_in_words() -> None:
    """
    Check the words a screen reader is given for a note.
    """
    assert note_words(Note.parse("F#4")) == "F sharp 4"
    assert note_words(Note.parse("Bb3")) == "B flat 3"
    assert note_words(Note.parse("C4")) == "C 4"
    assert note_name(Note.parse("F#4")) == "F♯4"


# -- the scale, with the keyboard or the buttons ----------------------------------------------------------------------


def test_a_whole_scale_is_built_and_answered_with_the_keyboard_alone(app: QApplication) -> None:
    """
    Check that every note, sign, step and the answer itself can be given without the mouse, using Return for each.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.steps = True
    settings.scale_construction.staff_keys = {-2, 0, 3}
    view = opened(ScaleConstruction())
    for _ in range(4):
        q = view.question
        assert q is not None and q.construct_scale is not None and q.construct_steps is not None
        for note in q.construct_scale:
            reach(view, note)
            press(view, "Return")
        assert view.scale_input.notes == q.construct_scale
        assert view.step_row.isVisibleTo(view) and not view.pitch_row.isVisibleTo(view)
        assert view.place_button.text() == "Mark step" and not view.answer_button.isEnabled()
        for step in q.construct_steps:
            press(view, step)  # W or H
            press(view, "Return")
        assert view.answer_button.isEnabled() and not view.place_button.isEnabled()
        press(view, "Return")  # Return answers, now that everything is placed
        assert view.answered and not view.missed
        view._advance.stop()
        view.next_question()
    assert view.correct == 4


def test_return_places_and_then_answers_and_never_both(app: QApplication) -> None:
    """
    Check that Place note and Answer, which both use Return, are never on at once, so Return is never ambiguous.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.steps = True
    view = opened(ScaleConstruction())
    q = view.question
    assert q is not None and q.construct_scale is not None and q.construct_steps is not None
    assert view.place_button.isEnabled() and not view.answer_button.isEnabled()
    for note in q.construct_scale:
        assert view.place_button.isEnabled() ^ view.answer_button.isEnabled()
        reach(view, note)
        press(view, "Return")
    for step in q.construct_steps:
        assert view.place_button.isEnabled() ^ view.answer_button.isEnabled()
        press(view, step)
        press(view, "Return")
    assert view.answer_button.isEnabled() and not view.place_button.isEnabled()
    press(view, "Return")
    assert view.answered
    view._advance.stop()


def test_a_whole_scale_is_built_and_answered_with_the_buttons_alone(app: QApplication) -> None:
    """
    Check that no click on the staff is needed: the buttons move the note, choose signs and steps, place, undo and answer.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.steps = True
    settings.scale_construction.staff_keys = {-3}
    view = ExerciseView(ScaleConstruction(), rng=random.Random(6))
    view.resize(1000, 800)
    q = view.question
    assert q is not None and q.construct_scale is not None and q.construct_steps is not None
    staff = view.scale_input
    for note in q.construct_scale:
        view.pitch_buttons["higher"].click()
        while note.diatonic - (staff.caret or 0) >= 7:
            view.pitch_buttons["octave_up"].click()
        while note.diatonic - (staff.caret or 0) <= -7:
            view.pitch_buttons["octave_down"].click()
        while (staff.caret or 0) < note.diatonic:
            view.pitch_buttons["higher"].click()
        while (staff.caret or 0) > note.diatonic:
            view.pitch_buttons["lower"].click()
        implied = key_accidental(note.letter, count=staff.key)
        if note.accidental != implied:
            view.accidental_buttons[note.accidental].click()
        view.place_button.click()
    assert staff.notes == q.construct_scale
    view.undo_button.click()  # takes back the last note ...
    assert len(staff.notes) == 7 and view.pitch_row.isVisibleTo(view)
    view.pitch_buttons["octave_up"].click()
    view.pitch_buttons["octave_down"].click()
    view.place_button.click()  # ... and it is put back at the caret, which was left where that note was
    assert staff.notes == q.construct_scale
    for step in q.construct_steps:
        view.step_buttons[step].click()
        view.place_button.click()
    assert staff.steps == q.construct_steps and view.answer_button.isEnabled()
    view.answer_button.click()
    assert view.answered and not view.missed
    view._advance.stop()


def test_backspace_takes_back_the_last_thing_placed(app: QApplication) -> None:
    """
    Check that Backspace undoes a note, and a step before any note.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.steps = True
    view = opened(ScaleConstruction())
    q = view.question
    assert q is not None and q.construct_scale is not None
    for note in q.construct_scale[:3]:
        reach(view, note)
        press(view, "Return")
    press(view, "Backspace")
    assert len(view.scale_input.notes) == 2
    press(view, "Backspace")
    press(view, "Backspace")
    press(view, "Backspace")  # nothing left to take back
    assert view.scale_input.notes == []


def test_place_keeps_its_return_key_when_its_label_changes(app: QApplication) -> None:
    """
    Check that Place note still answers to Return after it becomes Mark step, and goes back again.

    Setting the text of a button makes Qt forget its shortcut, so the button has to be given it again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.steps = True
    view = opened(ScaleConstruction())
    q = view.question
    assert q is not None and q.construct_scale is not None
    assert view.place_button.text() == "Place note" and view.place_button.shortcut().toString() == "Return"
    for note in q.construct_scale:
        view.scale_input.place_next(note)
    assert view.place_button.text() == "Mark step" and view.place_button.shortcut().toString() == "Return"
    view.scale_input.undo()
    assert view.place_button.text() == "Place note" and view.place_button.shortcut().toString() == "Return"


def test_the_arrow_keys_switch_the_step_while_steps_are_marked(app: QApplication) -> None:
    """
    Check that once the notes are placed all four arrows switch between whole and half, and Page Up does nothing.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.steps = True
    view = opened(ScaleConstruction())
    q = view.question
    assert q is not None and q.construct_scale is not None
    for note in q.construct_scale:
        reach(view, note)
        press(view, "Return")
    seen = []
    for key in ("Up", "Down", "Left", "Right"):
        press(view, key)
        seen.append(view.scale_input.pending_step)
    assert seen == ["H", "W", "H", "W"]
    press(view, "PgUp")
    assert view.scale_input.pending_step == "W" and len(view.scale_input.notes) == 8
    press(view, "H")
    assert view.step_buttons["H"].isChecked()


# -- the fork ---------------------------------------------------------------------------------------------------------


def test_the_key_signature_is_built_and_answered_with_the_keyboard_alone(app: QApplication) -> None:
    """
    Check that the arrows move along the fork wherever the keyboard is on the screen, Home goes back, and Return answers.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = opened(KeySignatureConstruction())
    for _ in range(10):
        q = view.question
        assert q is not None
        press(view, "Home")
        key = {True: "Up", False: "Down"}[q.key > 0]
        for _ in range(abs(q.key)):
            press(view, key)
        assert view.fork.value == q.key and view.staff.key == q.key
        press(view, "Return")
        assert view.answered and not view.missed, q.caption
        view._advance.stop()
        view.next_question()
    assert view.correct == 10


def test_the_fork_arrows_all_work_and_the_buttons_are_right(app: QApplication) -> None:
    """
    Check that Right and Left work like Up and Down, and that Return needs no button to be focused.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = opened(KeySignatureConstruction())
    for key, expected in (("Right", 1), ("Right", 2), ("Left", 1), ("Down", 0), ("Left", -1), ("Home", 0)):
        press(view, key)
        assert view.fork.value == expected, key
    assert view.answer_button.isVisibleTo(view) and view.answer_button.isEnabled() and not view.place_button.isVisibleTo(view)


# -- where the keys work ----------------------------------------------------------------------------------------------


def test_the_staff_keys_only_work_when_the_exercise_has_the_keyboard(app: QApplication) -> None:
    """
    Check that the arrows and letters do nothing while the keyboard is elsewhere, such as in a text box next to the exercise.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    host = QWidget()
    lay = QVBoxLayout(host)
    box = QLineEdit()
    view = ExerciseView(NoteConstruction(), rng=random.Random(4))
    lay.addWidget(box)
    lay.addWidget(view)
    host.resize(1000, 800)
    host.show()
    host.activateWindow()
    QTest.qWaitForWindowActive(host, 2000)
    box.setFocus()
    press(host, "Up")
    press(host, "G")
    assert view.input_staff.caret is None  # the keys went to the text box
    view.setFocus()
    press(host, "Up")
    assert view.input_staff.caret is not None


def test_the_staff_keys_are_off_in_the_exercises_that_do_not_use_them(app: QApplication) -> None:
    """
    Check that in a choice exercise the arrows and the note letters are not bound, so they cannot be pressed by mistake.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = opened(NoteNames())
    assert not any(k.isEnabled() for k in view._arrow_keys) and not any(k.isEnabled() for k in view._letter_keys)
    assert not view.pitch_row.isVisibleTo(view) and not view.place_button.isVisibleTo(view)
    press(view, "Up")
    press(view, "C")
    assert view.total == 0
    view2 = opened(NoteConstruction())
    assert all(k.isEnabled() for k in view2._arrow_keys) and all(k.isEnabled() for k in view2._letter_keys)
    fork = opened(KeySignatureConstruction())
    assert all(k.isEnabled() for k in fork._arrow_keys) and not any(k.isEnabled() for k in fork._letter_keys)


def test_the_keys_do_nothing_once_the_question_is_answered(app: QApplication) -> None:
    """
    Check that after the right answer the staff keys do not move or place anything while the next question is awaited.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = opened(NoteConstruction())
    q = view.question
    assert q is not None and q.construct is not None
    reach(view, q.construct)
    press(view, "Return")
    assert view.answered
    caret = view.input_staff.caret
    for key in ("Up", "PgUp", "G", "Return"):
        press(view, key)
    assert view.input_staff.caret == caret and view.total == 1
    view._advance.stop()


# -- opening an exercise, and the names that a screen reader reads ----------------------------------------------------


def test_opening_an_exercise_gives_it_the_keyboard(app: QApplication) -> None:
    """
    Check that choosing an exercise from the list puts the keyboard on the exercise, so that its keys work at once.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    window.activateWindow()
    QTest.qWaitForWindowActive(window, 2000)
    window.open_exercise(NoteConstruction)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView)
    QTest.qWait(50)
    assert QApplication.focusWidget() is view
    press(window, "Up")
    assert view.input_staff.caret is not None


def test_buttons_with_no_text_have_a_name_for_a_screen_reader(app: QApplication) -> None:
    """
    Check that the buttons that show only a picture, and the cards of the home page, are named.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(NoteConstruction(), rng=random.Random(4))
    for button in (view.sound_btn, view.gear, view.help_btn):
        assert button.accessibleName(), button
    assert view.sound_btn.accessibleName() in {"Sound on", "Sound muted"}
    window = MainWindow()
    for button in (window.menu_button, window.pane_button, window.view_button, window.stats_button, window.database_button):
        assert button.accessibleName(), button
    card = ExerciseCard(NoteConstruction)
    assert card.accessibleName().startswith("Note Construction") and card.accessibleDescription() == NoteConstruction.description
    for button in view.findChildren(QPushButton):
        assert button.text() or button.accessibleName(), button
    unnamed = [b for b in view.findChildren(QAbstractButton) if not (b.text() or b.accessibleName())]
    assert unnamed == []


def test_the_buttons_say_their_keys(app: QApplication) -> None:
    """
    Check that the sign and step buttons carry their keys, so that they are listed in the tooltips and shown to a screen reader.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    assert {a: b.shortcut().toString() for a, b in view.accidental_buttons.items()} == {-1: "-", 0: "0", 1: "+"}
    assert {s: b.shortcut().toString() for s, b in view.step_buttons.items()} == {"W": "W", "H": "H"}
    assert view.place_button.shortcut().toString() == "Return" == view.answer_button.shortcut().toString()
    assert view.undo_button.shortcut().toString() == "Backspace"
    for name, button in view.pitch_buttons.items():
        assert "arrow" in button.toolTip() or "Page" in button.toolTip(), name


def test_the_help_of_every_exercise_mentions_its_keys(app: QApplication) -> None:
    """
    Check that the help text of every exercise tells the reader which keys to use.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.construction.accidentals = True
    for cls in REGISTRY:
        text = cls().instructions()
        assert any(word in text for word in ("number", "Return", "Press Return", "keys", "arrow")), cls.name


def test_a_question_without_a_staff_has_no_status_line(app: QApplication) -> None:
    """
    Check that the line that says what comes next is only for the exercises where a note is placed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(NoteNames(), rng=random.Random(4))
    assert view._placement_text() == ("", "") and not view.place_status.isVisibleTo(view)
    q = view.question
    assert isinstance(q, Question)
