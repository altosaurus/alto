"""
The scale construction exercise.

Placing the notes of a named scale on a blank staff, left to right: the question, the staff that takes the notes, the
exercise screen and the settings.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import (
    QEvent,
    QPoint,
    QPointF,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QMouseEvent,
    QPainter,
    QWheelEvent,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
)

from alto import settings
from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import (
    KeySignatures,
    NoteConstruction,
    ScaleConstruction,
)
from alto.learning import (
    Database,
    Learner,
)
from alto.theory.pitch import (
    Note,
    key_accidental,
)
from alto.ui import settings_panel as sp
from alto.ui.exercise_view import ExerciseView
from alto.ui.home import (
    EXERCISE_ICONS,
    ExerciseCard,
)
from alto.ui.question_preview import QuestionPreview
from alto.ui.staff import (
    BOTTOM_LINE,
    StaffWidget,
)
from alto.ui.staff_input import ScaleInput
from alto.ui.store import store

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def questions(
    n: int = 200,
    *,
    seed: int = 1,
    **choose: object,
) -> list[Question]:
    """
    `n` questions made with these settings (clefs, modes, keys).

    Parameters
    ----------
    n : int
        How many questions.
    seed : int
        The random seed.
    choose : object
        Scale construction settings to change before asking.

    Returns
    -------
    list of Question
        The questions.
    """
    for name, value in choose.items():
        setattr(settings.scale_construction, name, value)
    rng = random.Random(seed)
    return [ScaleConstruction().generate(rng) for _ in range(n)]


def click(
    staff: ScaleInput,
    note: Note,
    *,
    button: Qt.MouseButton = Qt.MouseButton.LeftButton,
) -> None:
    """
    Click the staff at the height of a note's line or space.

    Parameters
    ----------
    staff : ScaleInput
        The staff.
    note : Note
        The note whose height to click at; its sign is not used, the staff's chosen sign is.
    button : Qt.MouseButton
        The mouse button. Keyword-only.
    """
    y = staff.staff_bottoms()[staff.clef] - (note.diatonic - BOTTOM_LINE[staff.clef]) * staff.GAP / 2
    point = QPointF(50, y)
    staff.mousePressEvent(
        QMouseEvent(QEvent.Type.MouseButtonPress, point, point, button, button, Qt.KeyboardModifier.NoModifier),
    )


def roll(
    staff: ScaleInput,
    *,
    delta: int,
) -> None:
    """
    Turn the mouse wheel over the staff.

    Parameters
    ----------
    staff : ScaleInput
        The staff.
    delta : int
        The wheel's angle delta: 120 is one notch up.
    """
    here = QPointF(100, 50)
    staff.wheelEvent(
        QWheelEvent(
            here,
            here,
            QPoint(0, 0),
            QPoint(0, delta),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        ),
    )


def place_scale(
    view: ExerciseView,
    *,
    notes: list[Note],
) -> None:
    """
    Place notes on the exercise screen, giving each its sign first the way a learner does.

    Parameters
    ----------
    view : ExerciseView
        The screen.
    notes : list of Note
        The notes to place, left to right.
    """
    for note in notes:
        implied = key_accidental(note.letter, count=view.scale_input.key)  # what the staff's signature already says
        # noinspection PyProtectedMember
        view._set_accidental(None if note.accidental == implied else note.accidental)
        click(view.scale_input, note)


def ready_scale(
    monkeypatch: pytest.MonkeyPatch,
    *,
    gap_ms: int,
) -> tuple[ExerciseView, Question]:
    """
    Make an exercise screen with the right scale already placed, with a quick scale, ready for Answer.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces the time between the notes of the scale.
    gap_ms : int
        The time between the notes of the scale that plays after a right answer. Keyword-only.

    Returns
    -------
    tuple of ExerciseView and Question
        The screen, and its question.
    """
    monkeypatch.setattr("alto.ui.exercise_view.SCALE_GAP_MS", gap_ms)
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None
    place_scale(view, notes=q.construct_scale)
    return view, q


# -- the question -----------------------------------------------------------------------------------------------------


def test_the_exercise_is_registered_in_scales_and_keys_and_plays_the_scale() -> None:
    """
    Check that the exercise is registered under Scales & keys with its name, and makes a sound.
    """
    assert ScaleConstruction in REGISTRY
    assert ScaleConstruction.name == "Scale Construction" and ScaleConstruction.category == "Scales & keys"
    assert ScaleConstruction.has_sound is True
    assert "Scale Construction" in ScaleConstruction().instructions()


def test_a_question_names_the_scale_and_asks_for_eight_notes_up_to_the_octave() -> None:
    """
    Check that a question names the scale under a blank staff and wants its eight notes, tonic to tonic an octave up.
    """
    for q in questions(
        100,
        modes={"Dorian"},
        clefs={"alto"},
        keys={2},
    ):
        assert q.construct_scale is not None and len(q.construct_scale) == 8
        assert q.staff == [] and q.choices == [] and q.key == 0 and q.accidentals and not q.build_key
        assert q.caption == "E Dorian" and q.clef == "alto"
        assert [n.name for n in q.construct_scale] == ["E", "F♯", "G", "A", "B", "C♯", "D", "E"]
        assert q.construct_scale[-1].octave == q.construct_scale[0].octave + 1
        assert q.answer.split()[0] == f"E{q.construct_scale[0].octave}"
        assert q.explanation == "E Dorian: E F♯ G A B C♯ D E"


def test_the_scale_sits_on_the_staff_in_every_clef() -> None:
    """
    Check that in every clef the whole scale fits on the staff and no more than one ledger line away from it.
    """
    for clef in settings.CLEFS:
        for q in questions(
            200,
            clefs={clef},
            modes=set(settings.KEY_MODES),
        ):
            bottom = BOTTOM_LINE[clef]
            steps = [n.diatonic - bottom for n in q.construct_scale or []]
            assert min(steps) >= -3 and max(steps) <= 10, (clef, q.answer)


def test_by_default_major_and_minor_scales_come_on_the_treble_and_bass_staves() -> None:
    """
    Check that by default major and minor scales come in the treble and bass clefs, with all fifteen signatures.
    """
    asked = questions(800)
    assert {q.clef for q in asked} == {"treble", "bass"}
    assert {q.caption.split()[-1] for q in asked} == {"Major", "minor"}
    assert len({q.caption for q in asked}) >= 28  # the fifteen major and fifteen minor keys, give or take a few
    assert all(abs(n.accidental) <= 1 for q in asked for n in q.construct_scale or [])


def test_the_scale_is_right_in_any_octave_so_long_as_all_of_it_is_in_the_same_one() -> None:
    """
    Check that the same scale an octave or two higher or lower is right, and that one note in another octave is not.
    """
    for q in questions(
        60,
        modes={"Major (Ionian)", "Locrian"},
    ):
        assert q.construct_scale is not None
        for octaves in (-2, -1, 0, 1, 2):
            moved = [Note(n.octave + octaves, letter=n.letter, accidental=n.accidental) for n in q.construct_scale]
            assert q.check_scale(moved), (q.caption, octaves)  # including a scale that crosses from B to C part way
        for place in range(8):
            one_off = [
                Note(n.octave + (1 if i == place else 0), letter=n.letter, accidental=n.accidental)
                for i, n in enumerate(q.construct_scale)
            ]
            assert not q.check_scale(one_off), (q.caption, place)
        low_half = [
            Note(n.octave - (1 if i < 4 else 0), letter=n.letter, accidental=n.accidental)
            for i, n in enumerate(q.construct_scale)
        ]
        assert not q.check_scale(low_half)  # the first half an octave down: not one scale any more


def test_only_the_exact_notes_in_order_are_right() -> None:
    """
    Check that the notes must be the scale's, spelled and ordered exactly, whichever octave they are in.
    """
    q = questions(1, keys={-3}, modes={"Major (Ionian)"}, clefs={"treble"})[0]
    assert q.construct_scale is not None
    scale = list(q.construct_scale)
    assert q.check_scale(scale)
    assert not q.check_scale(scale[:-1]) and not q.check_scale([*scale, scale[0]])
    assert not q.check_scale([*scale[:2][::-1], *scale[2:]])  # the right notes in the wrong order
    enharmonic = [Note.from_diatonic(n.diatonic, accidental=n.accidental + 1) if n.accidental == -1 else n for n in scale]
    assert not q.check_scale(enharmonic)  # B♭ is not A♯ spelt B♮ and the like
    assert not Question("no scale", choices=["a"], answer="a").check_scale(scale)


def test_a_question_comes_back_with_its_scale() -> None:
    """
    Check that a stored question has its scale back, and that old stored questions are not scales.
    """
    for q in questions(30):
        again = Question.from_dict(q.to_dict())
        assert again == q and again.construct_scale == q.construct_scale and again.item_key() == q.item_key()
    old = {k: v for k, v in questions(1)[0].to_dict().items() if k != "construct_scale"}
    assert Question.from_dict(old).construct_scale is None


def test_the_settings_are_kept_apart_from_the_key_exercises() -> None:
    """
    Check that the scale construction settings change the exercise's signature and nobody else's.
    """
    before = ScaleConstruction().settings_signature()
    settings.key_construction.modes = {"Dorian"}
    settings.key_signatures.keys = {1}
    assert ScaleConstruction().settings_signature() == before
    settings.scale_construction.modes = {"Dorian"}
    assert ScaleConstruction().settings_signature() != before


# -- the staff --------------------------------------------------------------------------------------------------------


def test_the_staff_starts_blank_with_every_place_drawn_and_a_fixed_width(app: QApplication) -> None:
    """
    Check that the staff starts with no notes and room for all of them, and does not change width as notes are placed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=8, caption="D Major")
    staff.resize(900, 300)
    assert staff.notes == [] and staff.key == 0 and staff.caption == "D Major"
    assert len(staff.columns) == 8 and all(column == [] for column in staff.columns)
    widths = {staff.maximumWidth()}
    for note in ("D4", "E4", "F#4"):
        click(staff, Note.parse(note))
        widths.add(staff.maximumWidth())
        assert len(staff.columns) == 8
    assert len(widths) == 1


def test_each_click_fills_the_next_place_from_the_left(app: QApplication) -> None:
    """
    Check that notes are placed one after another, left to right, whatever the pointer's horizontal position.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=4)
    staff.resize(900, 300)
    changes = []
    staff.notes_changed.connect(lambda: changes.append(1))
    for name in ("G4", "C4", "A4"):
        click(staff, Note.parse(name))
    assert [str(n) for n in staff.notes] == ["G4", "C4", "A4"] and len(changes) == 3
    assert [len(column) for column in staff.columns] == [1, 1, 1, 0]
    assert not staff.complete
    click(staff, Note.parse("D5"))
    assert staff.complete
    click(staff, Note.parse("E5"))  # every place is taken
    assert len(staff.notes) == 4 and len(changes) == 4


def test_the_next_note_follows_the_pointer_in_the_next_place_in_a_lighter_colour(app: QApplication) -> None:
    """
    Check that the note under the pointer is shown in the next place and in its own colour, and goes when the pointer leaves.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=4)
    staff.resize(900, 300)
    click(staff, Note.parse("C4"))
    point = QPointF(50, staff.staff_bottoms()["treble"])
    staff.mouseMoveEvent(
        QMouseEvent(
            QEvent.Type.MouseMove,
            point,
            point,
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        ),
    )
    assert [len(c) for c in staff.columns] == [1, 1, 0, 0] and set(staff.column_colors) == {1}
    assert [str(n) for n in staff.notes] == ["C4"]  # the preview has not been placed
    staff.leaveEvent(QEvent(QEvent.Type.Leave))
    assert [len(c) for c in staff.columns] == [1, 0, 0, 0] and staff.column_colors == {}


def test_undo_takes_back_the_last_note_and_a_locked_staff_ignores_everything(app: QApplication) -> None:
    """
    Check that undo removes notes from the right, and that nothing changes while the staff is locked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("bass", slots=4)
    staff.resize(900, 300)
    for name in ("C3", "D3"):
        click(staff, Note.parse(name))
    staff.undo()
    assert [str(n) for n in staff.notes] == ["C3"]
    staff.undo()
    staff.undo()  # nothing left to take back
    assert staff.notes == []
    click(staff, Note.parse("E3"))
    staff.locked = True
    click(staff, Note.parse("F3"))
    staff.undo()
    assert len(staff.notes) == 1


def test_right_click_asks_for_the_next_sign_and_the_chosen_sign_goes_on_the_next_note(app: QApplication) -> None:
    """
    Check that a right click says so, and that the sign chosen is the one the note is placed with.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=4)
    staff.resize(900, 300)
    asked = []
    staff.accidental_cycled.connect(lambda: asked.append(1))
    click(staff, Note.parse("F4"), button=Qt.MouseButton.RightButton)
    assert asked == [1] and staff.notes == []  # a right click places nothing
    staff.accidental = 1
    click(staff, Note.parse("F4"))
    staff.accidental = -1
    click(staff, Note.parse("B4"))
    assert [str(n) for n in staff.notes] == ["F♯4", "B♭4"]


# -- the exercise screen ----------------------------------------------------------------------------------------------


def test_the_screen_shows_a_blank_staff_with_the_scale_name_and_the_buttons(app: QApplication) -> None:
    """
    Check that the screen shows the staff you click, the scale's name on it, the sign buttons, Undo and Answer.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    view.show()
    q = view.question
    assert q is not None
    assert view.scale_input.isVisibleTo(view) and view.scale_input.caption == q.caption and view.prompt.isHidden()
    assert not view.staff.isVisibleTo(view) and not view.input_staff.isVisibleTo(view) and not view.fork.isVisibleTo(view)
    assert view.accidental_row.isVisibleTo(view) and view.undo_button.isVisibleTo(view) and view.answer_button.isVisibleTo(view)
    assert view.answer_button.text() == "Answer" and not view.answer_button.isEnabled()
    assert view.buttons == []


def test_the_answer_waits_until_every_note_is_placed(app: QApplication) -> None:
    """
    Check that Answer is off until all eight notes are down, and off again if one is taken back.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None
    place_scale(view, notes=q.construct_scale[:7])
    assert not view.answer_button.isEnabled()
    view.answer_button.click()  # nothing to hand in yet
    assert view.total == 0
    place_scale(view, notes=q.construct_scale[7:])
    assert view.answer_button.isEnabled()
    view.undo_button.click()
    assert len(view.scale_input.notes) == 7 and not view.answer_button.isEnabled()


def test_the_sign_is_used_up_by_each_note(app: QApplication) -> None:
    """
    Check that a sign chosen for a note is cleared once the note is placed, so the next note starts with none.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    view.accidental_buttons[1].click()
    assert view.scale_input.accidental == 1 and view.accidental_buttons[1].isChecked()
    click(view.scale_input, Note.parse("F4"))
    assert view.scale_input.accidental is None and not view.accidental_buttons[1].isChecked()
    assert str(view.scale_input.notes[0]) == "F♯4"


def test_right_click_steps_through_no_sign_sharp_and_flat(app: QApplication) -> None:
    """
    Check that right clicking the staff steps through no sign, a sharp and a flat, and round again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    seen = []
    for _ in range(4):
        click(view.scale_input, Note.parse("C4"), button=Qt.MouseButton.RightButton)
        seen.append(view.scale_input.accidental)
    assert seen == [1, -1, None, 1]
    assert view.scale_input.notes == []


def test_a_right_scale_is_scored_plays_the_scale_and_moves_on(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a right scale scores once, plays the eight notes one after another and moves on.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    played = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr("alto.ui.exercise_view.sounds.play_notes", lambda notes, **_: played.append(notes))
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    first = view.question
    assert first is not None and first.construct_scale is not None
    place_scale(view, notes=first.construct_scale)
    view.answer_button.click()
    assert view.answered and (view.correct, view.total, view.streak) == (1, 1, 1) and view.scale_input.locked
    assert played == [[[n] for n in first.construct_scale]]
    view.answer_button.click()  # a second press does not score again
    assert view.total == 1
    view._advance.stop()
    view.next_question()
    assert view.question is not first and view.scale_input.notes == [] and not view.scale_input.locked


def test_the_notes_turn_green_one_by_one_as_the_scale_plays(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the notes turn green one after another as they play, and are all green once the scale is over.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    view, _ = ready_scale(monkeypatch, gap_ms=40)
    lit: list[tuple[int, ...]] = []
    original = view._light_scale_note

    def watch(
        index: int | None,
        *,
        token: int,
    ) -> None:
        """
        Pass a note's colouring on, noting which columns are green afterwards.

        Parameters
        ----------
        index : int or None
            The place of the note that started, or None for the end.
        token : int
            Which question it is for.
        """
        original(index, token=token)
        lit.append(tuple(view.scale_input.column_colors))

    monkeypatch.setattr(view, "_light_scale_note", watch)
    assert view.scale_input.note_color is None and view.scale_input.column_colors == {}  # black until the scale plays
    view.answer_button.click()
    assert view.scale_input.note_color is None  # the notes are not turned green all at once: only as they sound
    QTest.qWait(600)
    assert lit == [tuple(range(i + 1)) for i in range(8)] + [tuple(range(8))]  # one more each time, and all at the end
    view._advance.stop()


def test_the_notes_turn_green_on_time_even_with_the_sound_off(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the notes turn green on time while muted, and the next question waits for the scale to finish.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    view, first = ready_scale(monkeypatch, gap_ms=60)
    view.answer_button.click()
    QTest.qWait(150)
    assert 0 < len(view.scale_input.column_colors) < 8 and view.question is first  # part way through, on this question
    QTest.qWait(60 * 8 + 700)
    assert view.question is not first and view.scale_input.column_colors == {}


def test_a_scale_that_was_playing_does_not_colour_the_next_questions_staff(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that changing a setting while a scale plays does not leave the old scale colouring notes on the new, blank staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    view, _ = ready_scale(monkeypatch, gap_ms=60)
    view.answer_button.click()
    QTest.qWait(100)
    view.settings_panel.changed.emit()  # a new question, while the old scale is still playing
    QTest.qWait(300)
    assert view.scale_input.column_colors == {} and view.scale_input.notes == []
    view._advance.stop()


def test_a_right_scale_on_another_octave_is_marked_right_and_plays_as_placed(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a scale an octave away from the one the question was made in is scored right and played where it was placed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    heard: list[list[list[Note]]] = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr("alto.ui.exercise_view.sounds.play_notes", lambda notes, **_: heard.append(list(notes)))
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None
    higher = [Note.from_diatonic(n.diatonic + 7, accidental=n.accidental) for n in q.construct_scale]
    place_scale(view, notes=higher)
    view.answer_button.click()
    assert view.answered and not view.missed and (view.correct, view.total) == (1, 1)
    assert heard == [[[n] for n in higher]]
    view._advance.stop()


def test_a_wrong_scale_counts_against_the_first_try_and_the_staff_is_cleared_to_try_again(app: QApplication) -> None:
    """
    Check that a wrong scale fails the question and that the staff is then cleared so that another can be tried.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None
    wrong = [Note.from_diatonic(n.diatonic + 1, accidental=0) for n in q.construct_scale]
    place_scale(view, notes=wrong)
    view.answer_button.click()
    assert view.missed and not view.answered and (view.total, view.correct, view.streak) == (1, 0, 0)
    assert view.scale_input.locked and not view.answer_button.isEnabled()
    QTest.qWait(1200)
    assert not view.scale_input.locked and view.scale_input.notes == [] and view.scale_input.caption == q.caption
    place_scale(view, notes=q.construct_scale)
    view.answer_button.click()
    assert view.answered and view.total == 1 and view.correct == 0  # only the first try counts toward the score
    view._advance.stop()


def test_every_try_is_recorded_with_the_notes_that_were_placed(app: QApplication) -> None:
    """
    Check that the learner's history gets each attempt with the notes placed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4), learner=learner)
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None
    wrong = [Note.from_diatonic(n.diatonic, accidental=0) for n in q.construct_scale]
    place_scale(view, notes=wrong)
    view.answer_button.click()
    QTest.qWait(1200)
    place_scale(view, notes=q.construct_scale)
    view.answer_button.click()
    view._advance.stop()
    rows = db.conn.execute("SELECT answer, correct FROM attempts ORDER BY id").fetchall()
    assert [r[1] for r in rows] == [0, 1]
    assert rows[1][0].split() == [f"{n.name}{n.octave}" for n in q.construct_scale]


def test_a_changed_setting_gives_a_fresh_blank_staff(app: QApplication) -> None:
    """
    Check that changing a setting replaces the question and clears the staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    click(view.scale_input, Note.parse("C4"))
    assert view.scale_input.notes
    view.settings_panel.changed.emit()
    assert view.scale_input.notes == [] and not view.answer_button.isEnabled()


def test_other_exercises_do_not_show_the_scale_staff(app: QApplication) -> None:
    """
    Check that an exercise that is not about building a scale has no scale staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(NoteConstruction(), rng=random.Random(4))
    view.show()
    assert not view.scale_input.isVisibleTo(view) and not view.undo_button.isVisibleTo(view)
    assert view.input_staff.isVisibleTo(view)


# -- the preview, the home page and the settings ----------------------------------------------------------------------


def test_the_preview_shows_the_scale_and_can_play_it(app: QApplication) -> None:
    """
    Check that the popup for a stored question shows the scale on a staff, with its name, and a Play button.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    q = questions(1, keys={2}, modes={"Major (Ionian)"}, clefs={"treble"})[0]
    dialog = QuestionPreview("Scale Construction", question=q)
    text = " ".join(label.text() for label in dialog.findChildren(QLabel))
    assert dialog.grab().width() > 0 and "D4 E4 F♯4" in text
    assert "Play" in [b.text() for b in dialog.findChildren(QPushButton)]


def test_the_home_card_has_its_own_icon_and_its_name_fits(app: QApplication) -> None:
    """
    Check that the exercise has an icon of its own and a card whose text fits.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert EXERCISE_ICONS["ScaleConstruction"] not in {EXERCISE_ICONS["ScaleIdentification"], EXERCISE_ICONS["NoteConstruction"]}
    card = ExerciseCard(ScaleConstruction)
    card.show()
    app.processEvents()
    assert card.toolTip() == ScaleConstruction.description
    for label in card.findChildren(QLabel):
        if label.wordWrap():
            assert label.heightForWidth(label.width()) <= label.height(), label.text()


def test_the_settings_pane_saves_under_its_own_name(app: QApplication) -> None:
    """
    Check that the scale settings are edited, saved and loaded apart from those of the key exercises.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.KeySignatureSettingsPanel) and pane.cfg is settings.scale_construction
    pane.key_list.boxes[5].setChecked(False)
    pane.modes.boxes["Lydian"].setChecked(True)
    assert "Lydian" in settings.scale_construction.modes and 5 not in settings.scale_construction.keys
    assert "Lydian" in str(store().value("scaleConstruction/modes")).split("|")
    assert store().value("keySignatures/modes") is None and store().value("keyConstruction/modes") is None
    settings.scale_construction.modes, settings.scale_construction.keys = {"Major (Ionian)"}, set(range(-7, 8))
    sp.load_scale_construction()
    assert "Lydian" in settings.scale_construction.modes and 5 not in settings.scale_construction.keys
    assert "Lydian" not in settings.key_construction.modes and 5 in settings.key_signatures.keys


# -- the steps --------------------------------------------------------------------------------------------------------


def steps_on(
    n: int = 1,
    *,
    seed: int = 1,
    **choose: object,
) -> list[Question]:
    """
    `n` questions made with the steps switched on.

    Parameters
    ----------
    n : int
        How many questions.
    seed : int
        The random seed.
    choose : object
        Other scale construction settings to change before asking.

    Returns
    -------
    list of Question
        The questions.
    """
    settings.scale_construction.steps = True
    return questions(n, seed=seed, **choose)


def mark(
    staff: ScaleInput,
    steps: list[str],
) -> None:
    """
    Mark steps on the staff the way a learner does: choose each one, then click.

    Parameters
    ----------
    staff : ScaleInput
        The staff, with all its notes placed.
    steps : list of str
        The steps to mark, each "W" or "H".
    """
    for step in steps:
        staff.set_pending_step(step)
        click(staff, Note.parse("C4"))


def view_with_steps(
    *,
    place: bool = True,
    learner: Learner | None = None,
) -> tuple[ExerciseView, Question]:
    """
    Make an exercise screen that asks for the steps, by default with its notes already placed.

    Parameters
    ----------
    place : bool, default True
        Place the right notes, leaving the steps to mark. Keyword-only.
    learner : Learner or None, default None
        Whose history to record. Keyword-only.

    Returns
    -------
    tuple of ExerciseView and Question
        The screen, and its question.
    """
    settings.scale_construction.steps = True
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4), learner=learner)
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None and q.construct_steps is not None
    if place:
        place_scale(view, notes=q.construct_scale)
    return view, q


def test_the_steps_are_off_by_default_and_a_question_without_them_has_none() -> None:
    """
    Check that nothing about steps is asked unless the setting is on.
    """
    assert settings.scale_construction.steps is False
    assert all(q.construct_steps is None and "step" not in q.prompt for q in questions(50))


def test_the_steps_of_a_question_are_those_between_the_notes_of_its_scale() -> None:
    """
    Check that the steps are seven letters, whole where the notes are two semitones apart and half where they are one.
    """
    for q in steps_on(
        200,
        modes=set(settings.KEY_MODES),
    ):
        assert q.construct_scale is not None and q.construct_steps is not None
        steps = q.construct_steps
        assert len(steps) == 7 and set(steps) <= {"W", "H"}
        semitones = [b.midi - a.midi for a, b in zip(q.construct_scale, q.construct_scale[1:], strict=False)]
        assert steps == ["W" if s == 2 else "H" for s in semitones]
        assert "step" in q.prompt and f"({' '.join(steps)})" in q.explanation
    major = steps_on(1, modes={"Major (Ionian)"})[0]
    assert major.construct_steps == ["W", "W", "H", "W", "W", "W", "H"]
    assert steps_on(1, modes={"Natural minor (Aeolian)"})[0].construct_steps == ["W", "H", "W", "W", "H", "W", "W"]
    assert steps_on(1, modes={"Dorian"})[0].construct_steps == ["W", "H", "W", "W", "W", "H", "W"]


def test_the_steps_are_checked_exactly_and_only_when_they_are_asked_for() -> None:
    """
    Check that the right steps are accepted, any others are not, and that a question with no steps accepts anything.
    """
    q = steps_on(1, modes={"Major (Ionian)"})[0]
    assert q.construct_steps is not None
    assert q.check_steps(list(q.construct_steps))
    assert not q.check_steps(q.construct_steps[:-1]) and not q.check_steps([*q.construct_steps, "W"])
    assert not q.check_steps(["H" if s == "W" else "W" for s in q.construct_steps])
    settings.scale_construction.steps = False
    plain = questions(1, seed=3)[0]
    assert plain.construct_steps is None and plain.check_steps([]) and plain.check_steps(["W"])


def test_a_question_comes_back_with_its_steps() -> None:
    """
    Check that stored steps come back, and that an old stored question has none.
    """
    for q in steps_on(20):
        again = Question.from_dict(q.to_dict())
        assert again == q and again.construct_steps == q.construct_steps and again.item_key() == q.item_key()
    old = {k: v for k, v in steps_on(1)[0].to_dict().items() if k != "construct_steps"}
    assert Question.from_dict(old).construct_steps is None


def test_a_question_with_steps_is_a_different_question_from_one_without() -> None:
    """
    Check that the same scale asked with and without its steps is not mixed up in the learner's history.
    """
    plain = questions(1, keys={2}, modes={"Major (Ionian)"}, clefs={"treble"}, seed=7)[0]
    with_steps = steps_on(1, keys={2}, modes={"Major (Ionian)"}, clefs={"treble"}, seed=7)[0]
    assert plain.construct_scale == with_steps.construct_scale and plain.item_key() != with_steps.item_key()


def test_the_staff_asks_for_steps_only_after_every_note_is_placed(app: QApplication) -> None:
    """
    Check that the step phase begins when the last note is placed, and not before, and not at all when steps are not asked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=3, with_steps=True)
    staff.resize(900, 400)
    assert not staff.placing_steps and not staff.done and staff.with_steps
    for name in ("C4", "D4"):
        click(staff, Note.parse(name))
    assert not staff.placing_steps
    click(staff, Note.parse("E4"))
    assert staff.complete and staff.placing_steps and not staff.done
    assert staff.wedges == ["W", ""]  # the step to be marked, in the first place
    plain = ScaleInput()
    plain.reset_scale("treble", slots=1)
    click(plain, Note.parse("C4"))
    assert plain.done and not plain.placing_steps and not plain.with_steps and plain.wedges == []


def test_a_left_click_marks_the_chosen_step_and_the_next_starts_as_a_whole_step(app: QApplication) -> None:
    """
    Check that a click marks the step shown, in order, and that the choice goes back to whole each time.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=4, with_steps=True)
    staff.resize(900, 400)
    for name in ("C4", "D4", "E4", "F4"):
        click(staff, Note.parse(name))
    chosen: list[str] = []
    staff.step_selected.connect(chosen.append)
    staff.set_pending_step("H")
    click(staff, Note.parse("C4"))
    assert staff.steps == ["H"] and staff.pending_step == "W" and chosen == ["H", "W"]
    click(staff, Note.parse("C4"))
    assert staff.steps == ["H", "W"] and not staff.done
    assert staff.wedges == ["H", "W", "W"]  # the third is the one to be marked next
    click(staff, Note.parse("C4"))
    assert staff.done and staff.steps == ["H", "W", "W"] and not staff.placing_steps
    click(staff, Note.parse("C4"))  # everything is placed
    assert len(staff.steps) == 3


def test_the_step_can_be_changed_with_a_right_click_or_the_mouse_wheel(app: QApplication) -> None:
    """
    Check that both switch between whole and half, that two notches of the wheel come back, and that the sign is left alone.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=2, with_steps=True)
    staff.resize(900, 400)
    signs = []
    staff.accidental_cycled.connect(lambda: signs.append(1))
    click(staff, Note.parse("C4"), button=Qt.MouseButton.RightButton)
    assert signs == [1]  # while notes are placed, a right click is for the sign
    click(staff, Note.parse("C4"))
    click(staff, Note.parse("D4"))
    click(staff, Note.parse("C4"), button=Qt.MouseButton.RightButton)
    assert staff.pending_step == "H" and signs == [1]
    click(staff, Note.parse("C4"), button=Qt.MouseButton.RightButton)
    assert staff.pending_step == "W"
    for delta, expected in ((120, "H"), (-120, "W"), (240, "W"), (-360, "H"), (60, "H"), (60, "W")):
        roll(staff, delta=delta)
        assert staff.pending_step == expected, delta


def test_the_wheel_does_nothing_once_everything_is_placed_or_when_locked(app: QApplication) -> None:
    """
    Check that the wheel has nothing to change once all notes and steps are placed, and that a locked staff ignores it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=2, with_steps=True)
    staff.resize(900, 400)
    signs: list[int] = []
    staff.accidental_stepped.connect(signs.append)
    staff.locked = True
    roll(staff, delta=120)
    assert signs == []
    staff.locked = False
    click(staff, Note.parse("C4"))
    click(staff, Note.parse("D4"))
    mark(staff, ["H"])
    assert staff.done
    roll(staff, delta=120)
    assert staff.pending_step == "W" and signs == []  # the "W" it went back to when the last step was marked


def test_during_note_placement_the_wheel_steps_through_the_signs(app: QApplication) -> None:
    """
    Check that each notch of the wheel asks for the next sign (up) or the one before (down), and saves up part of a notch.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=3, with_steps=True)
    staff.resize(900, 400)
    signs: list[int] = []
    staff.accidental_stepped.connect(signs.append)
    roll(staff, delta=120)
    roll(staff, delta=-240)
    assert signs == [1, -1, -1]
    roll(staff, delta=60)
    assert signs == [1, -1, -1]  # half a notch is not enough
    roll(staff, delta=60)
    assert signs == [1, -1, -1, 1]
    assert staff.pending_step == "W" and staff.notes == []  # the wheel is for the signs now, and places nothing


def test_the_wheel_cycles_none_sharp_flat_and_round_again_and_the_sign_is_used_by_the_next_note(app: QApplication) -> None:
    """
    Check on the screen that the wheel goes none, sharp, flat and round, lights the sign buttons, and is used up by a note.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    staff = view.scale_input
    seen = []
    for delta in (120, 120, 120, 120, -120, -120, -120):
        roll(staff, delta=delta)
        seen.append(staff.accidental)
    assert seen == [1, -1, None, 1, None, -1, 1]  # up goes none, sharp, flat; down goes back, and both wrap round
    assert view.accidental_buttons[1].isChecked() and not view.accidental_buttons[-1].isChecked()
    click(staff, Note.parse("F4"))
    assert str(staff.notes[0]) == "F♯4" and staff.accidental is None and not view.accidental_buttons[1].isChecked()
    roll(staff, delta=-120)
    assert staff.accidental == -1 and view.accidental_buttons[-1].isChecked()
    click(staff, Note.parse("B4"))
    assert str(staff.notes[1]) == "B♭4"


def test_a_step_wheel_turn_does_not_change_the_sign(app: QApplication) -> None:
    """
    Check that once the notes are placed the wheel is for the steps and leaves the sign alone.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, _ = view_with_steps()
    view._set_accidental(None)
    roll(view.scale_input, delta=120)
    assert view.scale_input.pending_step == "H" and view.scale_input.accidental is None


def wedge_image(
    *,
    left_y: float,
    right_y: float,
) -> QImage:
    """
    Draw one wedge between two notes, on white, and return the picture.

    Parameters
    ----------
    left_y : float
        The height of the left note's head, in pixels from the top. Keyword-only.
    right_y : float
        The height of the right note's head. Keyword-only.

    Returns
    -------
    QImage
        The picture: 200 by 100 pixels, the notes at x of 40 and 160, and a gap of 12 between staff lines.
    """
    image = QImage(200, 100, QImage.Format.Format_ARGB32)
    image.fill(QColor("white"))
    painter = QPainter(image)
    # noinspection PyProtectedMember
    StaffWidget()._draw_wedge(
        painter,
        left=QPointF(40, left_y),
        right=QPointF(160, right_y),
        text="W",
        gap=12,
        color=QColor("black"),
    )
    painter.end()
    return image


def inked(
    image: QImage,
    *,
    x: int,
    y: int,
) -> bool:
    """
    Report whether a pixel of a picture has been drawn on.

    Parameters
    ----------
    image : QImage
        The picture, which started white.
    x : int
        The pixel's column. Keyword-only.
    y : int
        The pixel's row. Keyword-only.

    Returns
    -------
    bool
        True if it is not the white it started as.
    """
    return image.pixelColor(x, y).name() != "#ffffff"


def test_a_step_is_two_lines_from_the_notes_up_to_a_point_with_the_letter_over_it(app: QApplication) -> None:
    """
    Check that a step is drawn as two plain lines that rise from the two notes and meet above them, not as a filled shape.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    level = wedge_image(left_y=80, right_y=80)
    assert inked(level, x=100, y=55)  # the point, halfway between the notes, above them
    assert any(inked(level, x=70, y=y) for y in range(62, 66)) and any(inked(level, x=130, y=y) for y in range(62, 66))
    assert any(inked(level, x=50, y=y) for y in range(68, 72)) and any(
        inked(level, x=150, y=y) for y in range(68, 72)
    )  # from above the notes
    assert not inked(level, x=70, y=72) and not inked(level, x=100, y=66)  # and nothing filled in under the lines
    assert any(inked(level, x=x, y=y) for x in range(92, 110) for y in range(38, 54))  # the letter, over the point
    assert not inked(level, x=100, y=28) and not inked(level, x=100, y=80)  # and nothing above it or below the lines
    after = wedge_image(left_y=80, right_y=60)
    assert inked(after, x=100, y=35) and not inked(after, x=100, y=55)  # the point is above the higher of the two notes


def test_undo_takes_back_the_steps_before_the_notes(app: QApplication) -> None:
    """
    Check that undo removes the last step first, then the steps before it, and only then the notes.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=3, with_steps=True)
    staff.resize(900, 400)
    for name in ("C4", "D4", "E4"):
        click(staff, Note.parse(name))
    mark(staff, ["W", "W"])
    staff.undo()
    assert staff.steps == ["W"] and len(staff.notes) == 3 and staff.placing_steps
    staff.undo()
    staff.undo()
    assert staff.steps == [] and len(staff.notes) == 2 and not staff.placing_steps


def test_the_lines_of_a_step_are_drawn_above_the_notes_they_join_and_take_their_own_colour(app: QApplication) -> None:
    """
    Check that on the staff the step is drawn above the notes, not under the staff, and that its colour can be its own.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=3, with_steps=True)
    staff.resize(900, 330)
    for name in ("E4", "F4", "G4"):
        click(staff, Note.parse(name))
    bare = staff.grab().toImage()
    staff.wedges = ["H", "W"]
    staff.update()
    marked = staff.grab().toImage()
    bottom = int(staff.staff_bottoms()["treble"])
    changed = [(x, y) for y in range(marked.height()) for x in range(marked.width()) if marked.pixel(x, y) != bare.pixel(x, y)]
    assert changed, "the steps were not drawn"
    assert max(y for _, y in changed) < bottom  # nothing is added under the staff: the steps are above the notes
    staff.wedge_colors = {0: QColor("#c62828")}
    staff.update()
    tinted = staff.grab().toImage()
    red = [
        (x, y)
        for y in range(tinted.height())
        for x in range(tinted.width())
        if tinted.pixelColor(x, y).red() > 150 > tinted.pixelColor(x, y).green()
    ]
    assert red and max(y for _, y in red) < bottom  # the first step takes its own colour
    assert len({x for x, _ in red}) < 400  # and only the first, not the second


def test_the_screen_shows_the_step_buttons_only_while_steps_are_marked(app: QApplication) -> None:
    """
    Check that the sign buttons give way to the whole and half step buttons once the notes are placed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = view_with_steps(place=False)
    view.show()
    assert q.construct_scale is not None
    assert view.accidental_row.isVisibleTo(view) and not view.step_row.isVisibleTo(view)
    place_scale(view, notes=q.construct_scale)
    assert view.step_row.isVisibleTo(view) and not view.accidental_row.isVisibleTo(view)
    assert not view.answer_button.isEnabled()  # the steps are still to come
    assert [view.step_buttons[s].text() for s in "WH"] == ["W", "H"] and view.step_buttons["W"].isChecked()
    mark(view.scale_input, ["W"] * 7)
    assert not view.step_row.isVisibleTo(view) and view.answer_button.isEnabled()
    view.undo_button.click()
    assert view.step_row.isVisibleTo(view) and not view.answer_button.isEnabled()


def test_the_step_buttons_choose_the_step_and_follow_the_wheel_and_the_right_click(app: QApplication) -> None:
    """
    Check that the buttons set the step a click marks, and that they light up to match the wheel and the right click.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, _ = view_with_steps()
    view.step_buttons["H"].click()
    assert view.scale_input.pending_step == "H" and view.step_buttons["H"].isChecked()
    click(view.scale_input, Note.parse("C4"))
    assert view.scale_input.steps == ["H"] and view.step_buttons["W"].isChecked()  # used up: back to whole
    roll(view.scale_input, delta=120)
    assert view.scale_input.pending_step == "H" and view.step_buttons["H"].isChecked()
    click(view.scale_input, Note.parse("C4"), button=Qt.MouseButton.RightButton)
    assert view.scale_input.pending_step == "W" and view.step_buttons["W"].isChecked()


def test_the_right_notes_and_the_right_steps_are_right(app: QApplication) -> None:
    """
    Check that the right notes with the right steps score and move on, and that the steps are recorded.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    view, q = view_with_steps(learner=learner)
    assert q.construct_steps is not None
    mark(view.scale_input, q.construct_steps)
    view.answer_button.click()
    assert view.answered and (view.correct, view.total) == (1, 1)
    view._advance.stop()
    row = db.conn.execute("SELECT answer, correct FROM attempts").fetchone()
    assert row[1] == 1 and row[0].endswith(f"| {' '.join(q.construct_steps)}")


def test_wrong_steps_make_the_scale_wrong_even_with_the_right_notes(app: QApplication) -> None:
    """
    Check that wrong steps fail the question and that the staff is cleared, steps and all, to try again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = view_with_steps()
    assert q.construct_steps is not None
    mark(view.scale_input, ["H" if s == "W" else "W" for s in q.construct_steps])
    view.answer_button.click()
    assert view.missed and not view.answered and (view.total, view.correct) == (1, 0)
    QTest.qWait(1200)
    staff = view.scale_input
    assert staff.notes == [] and staff.steps == [] and staff.with_steps and not staff.locked
    assert view.accidental_row.isVisibleTo(view) and not view.step_row.isVisibleTo(view)  # back to placing notes
    place_scale(view, notes=q.construct_scale or [])
    mark(staff, q.construct_steps)
    view.answer_button.click()
    assert view.answered and view.correct == 0  # only the first try counts toward the score
    view._advance.stop()


def test_wrong_notes_make_the_scale_wrong_even_with_the_right_steps(app: QApplication) -> None:
    """
    Check that the right steps do not save a scale whose notes are wrong.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = view_with_steps(place=False)
    assert q.construct_scale is not None and q.construct_steps is not None
    place_scale(view, notes=[Note.from_diatonic(n.diatonic + 1) for n in q.construct_scale])
    mark(view.scale_input, q.construct_steps)
    view.answer_button.click()
    assert view.missed and not view.answered
    QTest.qWait(1200)
    view._advance.stop()


def test_a_scale_on_another_octave_with_its_steps_is_right(app: QApplication) -> None:
    """
    Check that the octave still does not matter when the steps are asked for.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = view_with_steps(place=False)
    assert q.construct_scale is not None and q.construct_steps is not None
    place_scale(view, notes=[Note.from_diatonic(n.diatonic + 7, accidental=n.accidental) for n in q.construct_scale])
    mark(view.scale_input, q.construct_steps)
    view.answer_button.click()
    assert view.answered and not view.missed
    view._advance.stop()


def test_the_wedges_turn_green_with_the_notes_as_the_scale_plays(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that as each note turns green the wedge that leads up to it does too.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    monkeypatch.setattr("alto.ui.exercise_view.SCALE_GAP_MS", 40)
    view, q = view_with_steps()
    assert q.construct_steps is not None
    mark(view.scale_input, q.construct_steps)
    staff = view.scale_input
    view.answer_button.click()
    view._advance.stop()
    QTest.qWait(40 * 3 + 20)
    greens = set(staff.column_colors)
    assert greens and max(greens) < 7
    QTest.qWait(500)
    assert set(staff.column_colors) == set(range(8)) and staff.wedge_colors == {}


def test_the_switch_for_steps_is_in_the_settings_and_is_saved(app: QApplication) -> None:
    """
    Check that scale construction has a Steps switch that changes the setting, saves it and loads it back.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.KeySignatureSettingsPanel) and pane.steps_row is not None
    assert not pane.steps_row.isOn()
    pane.steps_row.click()
    assert settings.scale_construction.steps is True and store().value("scaleConstruction/steps") == "true"
    assert view.question is not None and view.question.construct_steps is not None  # a new question asks for them
    settings.scale_construction.steps = False
    sp.load_scale_construction()
    assert settings.scale_construction.steps is True
    pane.steps_row.click()
    assert settings.scale_construction.steps is False
    other = ExerciseView(KeySignatures(), rng=random.Random(4)).settings_panel
    assert isinstance(other, sp.KeySignatureSettingsPanel) and other.steps_row is None  # only scale construction has it


def test_the_preview_shows_the_steps(app: QApplication) -> None:
    """
    Check that the popup for a stored question shows the steps under the notes.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    q = steps_on(1, keys={2}, modes={"Major (Ionian)"}, clefs={"treble"})[0]
    dialog = QuestionPreview("Scale Construction", question=q)
    assert dialog.grab().width() > 0 and "W W H W W W H" in " ".join(label.text() for label in dialog.findChildren(QLabel))


# -- the staff's key signature, apart from the scale's ----------------------------------------------------------------


def c_major_on_two_flats() -> list[Question]:
    """
    Ask for a C major scale on a staff whose key signature is B♭ major's: two flats.

    Returns
    -------
    list of Question
        A few questions, all of that scale on that staff, in the treble clef.
    """
    return questions(
        5,
        keys={0},
        staff_keys={-2},
        modes={"Major (Ionian)"},
        clefs={"treble"},
    )


def view_on_two_flats() -> tuple[ExerciseView, Question]:
    """
    Make an exercise screen that asks for a C major scale on a staff with two flats.

    Returns
    -------
    tuple of ExerciseView and Question
        The screen, and its question.
    """
    settings.scale_construction.staff_keys = {-2}
    settings.scale_construction.keys = {0}
    settings.scale_construction.modes = {"Major (Ionian)"}
    settings.scale_construction.clefs = {"treble"}
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None
    return view, q


def test_the_staff_has_no_key_signature_unless_one_is_chosen() -> None:
    """
    Check that by default the staff is blank, whatever the scale is.
    """
    assert settings.scale_construction.staff_keys == {0} and settings.scale_construction.active_staff_keys() == [0]
    asked = questions(100)
    assert {q.key for q in asked} == {0} and len({q.caption for q in asked}) > 10


def test_the_staff_key_signature_is_chosen_apart_from_the_scales_own() -> None:
    """
    Check that the signature drawn on the staff comes from its own setting and is independent of the scale's.
    """
    for q in c_major_on_two_flats():
        assert q.key == -2 and q.caption == "C Major"  # the staff has B♭ major's signature; the scale is C major
        assert q.construct_scale is not None and [n.name for n in q.construct_scale] == list("CDEFGABC")
        assert "The staff has 2 flats, but the scale has no sharps or flats" in q.explanation
    asked = questions(
        400,
        keys={0, 2},
        staff_keys={-2, 3},
    )
    assert {q.key for q in asked} == {-2, 3}
    assert {(q.key, q.caption.split()[0]) for q in asked if q.caption in {"C Major", "D Major"}} == {
        (-2, "C"),
        (3, "C"),
        (-2, "D"),
        (3, "D"),
    }  # either scale on either staff
    same = questions(1, keys={2}, staff_keys={2}, modes={"Major (Ionian)"})[0]
    assert same.key == 2 and "The staff has" not in same.explanation  # nothing to point out when they agree


def test_a_question_comes_back_with_its_staff_key_signature() -> None:
    """
    Check that a stored question keeps the signature of its staff, and that it tells one staff from another.
    """
    q = c_major_on_two_flats()[0]
    assert Question.from_dict(q.to_dict()).key == -2
    plain = questions(1, keys={0}, staff_keys={0}, modes={"Major (Ionian)"}, clefs={"treble"}, seed=1)[0]
    on_flats = questions(1, keys={0}, staff_keys={-2}, modes={"Major (Ionian)"}, clefs={"treble"}, seed=1)[0]
    assert plain.construct_scale == on_flats.construct_scale and plain.item_key() != on_flats.item_key()


def test_the_staffs_signature_is_drawn_and_a_note_without_a_sign_takes_what_it_says(app: QApplication) -> None:
    """
    Check that the staff shows its signature and gives a plain click the signs the signature gives, as a reader would.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = ScaleInput()
    staff.reset_scale("treble", slots=8, key=-2)
    staff.resize(900, 330)
    assert staff.key == -2
    for name in ("B4", "E5", "C5"):
        click(staff, Note.parse(name.replace("#", "")))
    assert [str(n) for n in staff.notes] == ["B♭4", "E♭5", "C5"]  # B and E are flat on this staff, and C is not
    plain = ScaleInput()
    plain.reset_scale("treble", slots=8)
    click(plain, Note.parse("B4"))
    assert str(plain.notes[0]) == "B4"  # with no signature the same click is a B natural


def test_the_staff_keeps_its_width_whatever_signature_it_has(app: QApplication) -> None:
    """
    Check that the staff is as wide with seven flats as with none.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    widths = set()
    for key in (0, -2, 3, -7, 7):
        staff = ScaleInput()
        staff.reset_scale("treble", slots=8, key=key)
        widths.add((staff.maximumWidth(), staff.sizeHint().width()))
    assert len(widths) == 1


def test_a_natural_is_needed_for_a_note_the_staff_flattens_and_the_right_signs_make_the_scale_right(app: QApplication) -> None:
    """
    Check the example in full: on a staff with two flats a C major scale needs naturals on its B and E, and is right with them.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = view_on_two_flats()
    assert q.construct_scale is not None and q.key == -2 and view.scale_input.key == -2
    place_scale(view, notes=q.construct_scale)  # E and B with a natural sign each, the rest with none
    assert [str(n) for n in view.scale_input.notes] == [str(n) for n in q.construct_scale]
    assert view.scale_input.notes[2].accidental == 0 and view.scale_input.notes[6].accidental == 0
    view.answer_button.click()
    assert view.answered and not view.missed
    view._advance.stop()


def test_leaving_out_the_naturals_gives_a_different_scale(app: QApplication) -> None:
    """
    Check that placing the notes with no signs on a staff with two flats gives the flat B and E, which is not C major.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = view_on_two_flats()
    assert q.construct_scale is not None
    for note in q.construct_scale:
        click(view.scale_input, note)  # no sign chosen: each takes what the staff's signature says
    assert [n.name for n in view.scale_input.notes] == ["C", "D", "E♭", "F", "G", "A", "B♭", "C"]
    view.answer_button.click()
    assert view.missed and not view.answered
    QTest.qWait(1200)
    assert view.scale_input.notes == [] and view.scale_input.key == -2  # cleared, with the signature still on the staff
    view._advance.stop()


def test_natural_is_one_of_the_signs_the_wheel_and_right_click_step_through_on_a_staff_with_a_signature(
    app: QApplication,
) -> None:
    """
    Check that with a signature on the staff the signs are none, sharp, flat and natural, round again, as in note construction.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.staff_keys = {-2}
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    seen = []
    for _ in range(5):
        click(view.scale_input, Note.parse("C4"), button=Qt.MouseButton.RightButton)
        seen.append(view.scale_input.accidental)
    assert seen == [1, -1, 0, None, 1]
    roll(view.scale_input, delta=-120)
    assert view.scale_input.accidental is None  # one notch back from a sharp: no sign


def test_a_retry_keeps_the_staffs_signature_and_the_steps_still_work_with_it(app: QApplication) -> None:
    """
    Check that steps can be asked for on a staff with a signature, and that the scale is checked on its notes and steps.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.staff_keys = {3}
    view, q = view_with_steps()
    assert q.construct_steps is not None and view.scale_input.key == 3
    mark(view.scale_input, q.construct_steps)
    view.answer_button.click()
    assert view.answered
    view._advance.stop()


def test_the_preview_shows_the_staffs_signature(app: QApplication) -> None:
    """
    Check that the popup for a stored question draws the signature of its staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    q = c_major_on_two_flats()[0]
    dialog = QuestionPreview("Scale Construction", question=q)
    assert dialog.grab().width() > 0 and "The staff has 2 flats" in " ".join(
        label.text() for label in dialog.findChildren(QLabel)
    )


def test_the_settings_have_a_staff_key_signature_apart_from_the_scales(app: QApplication) -> None:
    """
    Check that scale construction has a Staff keys page and a Scale keys page next to each other, each with its own choice.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.KeySignatureSettingsPanel) and pane.staff_keys_row is not None and pane.staff_key_list is not None
    assert "Staff keys" in pane.staff_keys_row.title.text() and "Scale keys" in pane.keys_row.title.text()
    assert pane.stack.count() == 5  # the menu, then clefs, scales, and the staff's key and the scale's next to each other
    for row, index in ((pane.clefs_row, 1), (pane.modes_row, 2), (pane.staff_keys_row, 3), (pane.keys_row, 4)):
        row.click()
        QTest.qWait(300)
        assert pane.stack.currentIndex() == index
        pane._go(0)
        QTest.qWait(300)
    pane.staff_key_list.boxes[-2].setChecked(True)
    assert settings.scale_construction.staff_keys == {0, -2} and settings.scale_construction.keys == set(range(-7, 8))
    assert store().value("scaleConstruction/staffKeys") == "-2,0"
    pane.key_list.boxes[5].setChecked(False)
    assert 5 not in settings.scale_construction.keys and settings.scale_construction.staff_keys == {0, -2}
    assert view.question is not None and view.question.key in {0, -2}
    settings.scale_construction.staff_keys, settings.scale_construction.keys = {0}, set(range(-7, 8))
    sp.load_scale_construction()
    assert settings.scale_construction.staff_keys == {0, -2} and 5 not in settings.scale_construction.keys
    assert ScaleConstruction().settings_signature().count("-2") >= 1


def test_the_names_of_the_rows_fit_beside_their_pictures(app: QApplication) -> None:
    """
    Check that no row of the settings menu has its name cut off, even in a font wider than the usual one.

    The keys are all ticked, so that the pictures are as wide as they get, and the pane has the width it has in the window.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    usual = app.font()
    wider = QFont(usual)
    wider.setPointSizeF(usual.pointSizeF() + 2)  # a screen or a system whose type is larger than ours
    app.setFont(wider)
    try:
        settings.scale_construction.staff_keys = set(range(-7, 8))
        pane = sp.KeySignatureSettingsPanel(settings.scale_construction, prefix="scaleConstruction")
        pane.setFixedWidth(ExerciseView.PANE_WIDTH - 2 * 9)  # the width the pane gives it
        pane.resize(pane.width(), 600)
        pane.show()
        app.processEvents()
        for row in (pane.clefs_row, pane.modes_row, pane.staff_keys_row, pane.keys_row):
            assert row is not None
            assert row.title.sizeHint().width() <= row.title.width(), row.title.text()
    finally:
        app.setFont(usual)


def test_the_other_key_exercises_have_one_key_signature_setting(app: QApplication) -> None:
    """
    Check that only scale construction has two key signature settings: the other exercises keep their one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    other = ExerciseView(KeySignatures(), rng=random.Random(4)).settings_panel
    assert isinstance(other, sp.KeySignatureSettingsPanel) and other.staff_keys_row is None and other.staff_key_list is None
    assert "Key signatures" in other.keys_row.title.text() and other.stack.count() == 4


def test_the_help_mentions_the_staffs_signature_only_when_the_staff_can_have_one() -> None:
    """
    Check that the help explains the staff's own signature once the staff can have one.
    """
    assert "staff may have a key signature" not in ScaleConstruction().instructions()
    settings.scale_construction.staff_keys = {-2, 0}
    assert "staff may have a key signature" in ScaleConstruction().instructions()


# -- the octave --------------------------------------------------------------------------------------------------------


def scale_of(q: Question) -> list[Note]:
    """
    Return the notes of a question's scale.

    Parameters
    ----------
    q : Question
        A question made by the exercise.

    Returns
    -------
    list of Note
        Its scale, or no notes for a question that has none.
    """
    return q.construct_scale or []


def octave_on(
    n: int = 1,
    *,
    seed: int = 1,
    **choose: object,
) -> list[Question]:
    """
    `n` questions made with the octave switched on.

    Parameters
    ----------
    n : int
        How many questions.
    seed : int
        The random seed.
    choose : object
        Other scale construction settings to change before asking.

    Returns
    -------
    list of Question
        The questions.
    """
    settings.scale_construction.octave = True
    return questions(n, seed=seed, **choose)


def test_the_octave_is_off_by_default_and_the_scale_is_then_named_without_one() -> None:
    """
    Check that by default the name has no octave and any octave is accepted.
    """
    assert settings.scale_construction.octave is False
    for q in questions(60):
        assert not q.exact_octave and not any(c.isdigit() for c in q.caption)  # "D Major", not "D4 Major"
        assert q.construct_scale is not None
        higher = [Note(n.octave + 1, letter=n.letter, accidental=n.accidental) for n in q.construct_scale]
        assert q.check_scale(higher)


def test_with_the_octave_on_the_name_says_which_octave_to_start_in() -> None:
    """
    Check that the name is the first note with its octave, such as G2 Major, and that the answer starts there.
    """
    for q in octave_on(
        200,
        clefs=set(settings.CLEFS),
        modes=set(settings.KEY_MODES),
    ):
        assert q.exact_octave and q.construct_scale is not None
        first = q.construct_scale[0]
        tonic, kind = q.caption.split(" ", 1)
        assert tonic == f"{first.name}{first.octave}", q.caption  # "G2", "B♭4"
        assert q.prompt == f"Place the notes of the {q.caption} scale on the staff."
        assert q.explanation.startswith(f"{q.caption}: {first.name} ")
    g2 = octave_on(
        1,
        keys={1},
        modes={"Major (Ionian)"},
        clefs={"bass"},
        seed=3,
    )
    assert g2[0].caption.startswith("G") and g2[0].caption.endswith(" Major")


def test_with_the_octave_on_only_the_octave_asked_is_right() -> None:
    """
    Check that the scale has to start in the octave named: the same scale an octave away is wrong.
    """
    for q in octave_on(40):
        assert q.construct_scale is not None
        exact = list(q.construct_scale)
        assert q.check_scale(exact)
        for octaves in (-2, -1, 1, 2):
            moved = [Note(n.octave + octaves, letter=n.letter, accidental=n.accidental) for n in exact]
            assert not q.check_scale(moved), (q.caption, octaves)
        one_off = [Note(n.octave + (1 if i == 3 else 0), letter=n.letter, accidental=n.accidental) for i, n in enumerate(exact)]
        assert not q.check_scale(one_off)


def test_with_the_octave_on_every_scale_asked_fits_on_the_staff_and_its_ledger_lines() -> None:
    """
    Check that in every clef and every scale, the whole scale lies within the range the staff can be clicked in.
    """
    for clef in settings.CLEFS:
        low, high = settings.RANGE_LIMITS[clef]
        asked = octave_on(
            300,
            clefs={clef},
            modes=set(settings.KEY_MODES),
            keys=set(range(-7, 8)),
        )
        for q in asked:
            assert q.construct_scale is not None
            assert all(low <= n.diatonic <= high for n in q.construct_scale), (clef, q.caption, q.answer)
        octaves = {scale_of(q)[0].octave for q in asked}
        assert len(octaves) >= 3, (clef, octaves)  # the octave really is part of the question


def test_with_the_octave_on_the_scales_are_spread_over_more_than_the_usual_place_on_the_staff() -> None:
    """
    Check that with the octave on, scales are asked above and below where they sit by default, on ledger lines.
    """
    settings.scale_construction.octave = False
    usual = questions(300, clefs={"treble"}, modes={"Major (Ionian)"}, keys={0, 1, 2, 3})
    usual_span = {n.diatonic for q in usual for n in scale_of(q)}
    wide = octave_on(300, clefs={"treble"}, modes={"Major (Ionian)"}, keys={0, 1, 2, 3})
    wide_span = {n.diatonic for q in wide for n in scale_of(q)}
    assert min(wide_span) < min(usual_span) and max(wide_span) > max(usual_span)


def test_with_the_octave_on_every_note_of_every_scale_can_be_placed_by_clicking(app: QApplication) -> None:
    """
    Check that clicking at the height of each note of a scale asked gives that very note, so none is out of reach.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for q in octave_on(
        80,
        clefs=set(settings.CLEFS),
        modes=set(settings.KEY_MODES),
    ):
        assert q.construct_scale is not None
        staff = ScaleInput()
        staff.reset_scale(q.clef, slots=8, key=q.key)
        staff.resize(900, 330)
        for note in q.construct_scale:
            staff.accidental = note.accidental
            click(staff, note)
        assert staff.notes == q.construct_scale, (q.clef, q.caption)
        assert q.check_scale(staff.notes)


def test_the_octave_is_scored_on_the_screen(app: QApplication) -> None:
    """
    Check that the right scale in the octave named is right, and the same scale in another octave is wrong.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.scale_construction.octave = True
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    view.resize(1000, 700)
    q = view.question
    assert q is not None and q.construct_scale is not None and q.exact_octave
    place_scale(view, notes=[Note.from_diatonic(n.diatonic + 7, accidental=n.accidental) for n in q.construct_scale])
    view.answer_button.click()
    assert view.missed and not view.answered  # right notes, wrong octave
    QTest.qWait(1200)
    place_scale(view, notes=q.construct_scale)
    view.answer_button.click()
    assert view.answered and view.correct == 0  # only the first try counts toward the score
    view._advance.stop()


def test_a_question_comes_back_with_its_octave_rule_and_is_not_mixed_up_with_one_without(app: QApplication) -> None:
    """
    Check that the octave rule is stored with the question, and that the same scale asked either way is told apart.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for q in octave_on(20):
        again = Question.from_dict(q.to_dict())
        assert again == q and again.exact_octave
    old = {k: v for k, v in octave_on(1)[0].to_dict().items() if k != "exact_octave"}
    assert Question.from_dict(old).exact_octave is False
    settings.scale_construction.octave = False
    plain = questions(1, keys={2}, modes={"Major (Ionian)"}, clefs={"treble"}, seed=5)[0]
    named = octave_on(1, keys={2}, modes={"Major (Ionian)"}, clefs={"treble"}, seed=5)[0]
    assert plain.item_key() != named.item_key()


def test_the_octave_switch_is_in_the_settings_for_scale_construction_only(app: QApplication) -> None:
    """
    Check that the Octave switch changes the setting, is saved and loaded, gives a new question, and is not in other panels.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(ScaleConstruction(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.KeySignatureSettingsPanel) and pane.octave_row is not None and pane.steps_row is not None
    assert not pane.octave_row.isOn()
    pane.octave_row.click()
    assert settings.scale_construction.octave is True and store().value("scaleConstruction/octave") == "true"
    assert view.question is not None and view.question.exact_octave and view.question.caption[1:].lstrip("♯♭")[0].isdigit()
    assert settings.scale_construction.steps is False  # separate from the steps
    settings.scale_construction.octave = False
    sp.load_scale_construction()
    assert settings.scale_construction.octave is True
    pane.octave_row.click()
    assert settings.scale_construction.octave is False and view.question is not None and not view.question.exact_octave
    other = ExerciseView(KeySignatures(), rng=random.Random(4)).settings_panel
    assert isinstance(other, sp.KeySignatureSettingsPanel) and other.octave_row is None


def test_the_help_says_which_rule_about_the_octave_is_in_force() -> None:
    """
    Check that the help explains that any octave will do, or that the scale must start in the octave named.
    """
    assert "Any octave will do" in ScaleConstruction().instructions()
    settings.scale_construction.octave = True
    text = ScaleConstruction().instructions()
    assert "Any octave will do" not in text and "G2 Major" in text
