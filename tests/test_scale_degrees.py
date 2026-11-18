"""
Scale-degree names follow the question's key in each exercise that shares note naming.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pytest
from PySide6.QtWidgets import QCheckBox, QGroupBox

from alto import settings
from alto.exercises.library import (
    KeyboardNotes,
    NoteConstruction,
    NoteNames,
)
from alto.theory.pitch import (
    MAJOR_KEYS,
    Note,
)
from alto.theory.scales import (
    SCALES,
    build,
)
from alto.ui.degree_text import DegreeCheckBox
from alto.ui.exercise_view import (
    ExerciseView,
    choice_keys,
    note_name,
    note_words,
    second_row_keys,
)
from alto.ui.question_preview import QuestionPreview
from alto.ui.settings_panel import (
    NoteNameSettingsPanel,
    load_note_names,
)
from keys import (
    opened,
    press,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


@pytest.mark.parametrize("key", range(-7, 8))
def test_diatonic_degrees_follow_the_major_scale(key: int) -> None:
    """
    Check all seven degrees against scale spelling, including the extreme signatures.

    Parameters
    ----------
    key : int
        The major key signature.
    """
    tonic = Note.parse(f"{MAJOR_KEYS[key].replace('♭', 'b').replace('♯', '#')}4")
    notes = build(tonic, intervals=SCALES["Major (Ionian)"])
    assert [settings.spell(n, naming="degrees", key=key) for n in notes[:7]] == [f"{i}̂" for i in range(1, 8)]
    for index, note in enumerate(notes[:7], start=1):
        lowered = Note(note.octave, letter=note.letter, accidental=note.accidental - 1)
        raised = Note(note.octave, letter=note.letter, accidental=note.accidental + 1)
        assert settings.spell(lowered, naming="degrees", key=key) == f"♭{index}̂"
        assert settings.spell(raised, naming="degrees", key=key) == f"♯{index}̂"


@pytest.mark.parametrize("accidentals", [False, True])
def test_identification_degree_answers_and_columns(accidentals: bool) -> None:
    """
    Check answers, key context and degree columns with multiple active signatures.

    Parameters
    ----------
    accidentals : bool
        Whether chromatic notes are included.
    """
    cfg = settings.note_names
    cfg.naming, cfg.accidentals, cfg.key_signatures = "degrees", accidentals, {-7, -2, 0, 1, 7}
    rng = random.Random(12)
    for _ in range(200):
        question = NoteNames().generate(rng)
        assert question.answer in question.choices
        assert question.check(question.answer)
        assert question.grid is not None
        assert len(set(question.choices)) == len(question.choices)
        assert question.caption == ""
        for label in question.choices:
            assert question.grid[label][1] == int(label.replace("̂", "")[-1]) - 1
        if not accidentals:
            assert question.choices == [f"{i}̂" for i in range(1, 8)]


@pytest.mark.parametrize("signature", [False, True])
@pytest.mark.parametrize("octave", [False, True])
def test_keyboard_degree_answers_include_enharmonics_and_octaves(
    signature: bool,
    *,
    octave: bool,
) -> None:
    """
    Check that keyboard answers remain reachable for every key and spelling.

    Parameters
    ----------
    signature : bool
        Whether to show a key signature.
    octave : bool
        Whether to require an octave. Keyword-only.
    """
    settings.note_names.naming = "degrees"
    cfg = settings.keyboard
    cfg.key_signature, cfg.require_octave, cfg.keys = signature, octave, {-7, -2, 0, 1, 7}
    cfg.low, cfg.high = 60, 72
    rng = random.Random(14)
    for _ in range(200):
        question = KeyboardNotes().generate(rng)
        assert question.keyboard is not None
        assert question.check(question.answer)
        assert question.answer == settings.spell(
            question.keyboard,
            naming="degrees",
            key=question.key,
            octave=octave,
        )
        for answer in (question.answer, *question.accept):
            degree, _, number = answer.partition(question.joiner) if octave else (answer, "", "")
            assert degree in question.choices
            if octave:
                assert question.octaves is not None
                assert number in question.octaves
        assert question.prompt == ""
    if not signature:
        cfg.low = cfg.high = 61
        question = KeyboardNotes().generate(rng)
        suffix = " / 4" if octave else ""
        assert {question.answer, *question.accept} == {f"♯1̂{suffix}", f"♭2̂{suffix}"}


def test_construction_degree_prompt_and_accessible_caret() -> None:
    """
    Keep target labels, placement feedback and accessible names in the same key.
    """
    settings.note_names.naming = "degrees"
    settings.construction.key_signature = True
    settings.construction.keys = {1}
    settings.construction.accidentals = True
    rng = random.Random(16)
    for _ in range(50):
        question = NoteConstruction().generate(rng)
        assert question.construct is not None
        assert question.check_placed(question.construct)
        assert question.answer == note_name(question.construct, key=question.key)
        assert question.caption == question.prompt
        degree, octave = question.answer.split(" / ")
        subscript = octave.translate(str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋"))
        assert question.prompt == f"GM {degree}{subscript}"
    note = Note.parse("F4")
    assert note_name(note, key=1) == "♭7̂ / 4"
    assert note_words(note, key=1) == "flat degree 7, octave 4"
    assert note_name(note) == "F4"  # scale construction has no degree reference


def test_degree_shortcuts_leave_octave_keys_available() -> None:
    """
    Ensure chromatic degree banks have unique shortcuts and a separate octave row.
    """
    labels = [f"{sign}{degree}" for sign in ("", "♯", "♭", "𝄪", "𝄫") for degree in range(1, 8)]
    keys = choice_keys(labels)
    assert len(set(keys)) == len(labels)
    assert keys[0] == "1"
    assert keys[7] == "Shift+1"
    assert keys[14] == "Ctrl+1"
    assert keys[21] == "Alt+Shift+1"
    assert keys[28] == "Alt+Ctrl+1"
    assert second_row_keys(keys, labels=["3", "4", "5"]) == ["A", "S", "D"]


def test_degree_option_saves_and_reloads(app: QApplication) -> None:
    """
    Check the settings control offers degrees and persists the selection.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    panel = NoteNameSettingsPanel(settings.note_names)
    panel.naming_radios["degrees"].click()
    assert settings.note_names.naming == "degrees"
    settings.note_names.naming = "letters"
    load_note_names()
    assert settings.note_names.naming == "degrees"
    panel.close()


def test_chromatic_degree_and_octave_shortcuts_answer_the_question(app: QApplication) -> None:
    """
    Answer a black key with its altered degree and octave using the actual buttons' shortcuts.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.note_names.naming = "degrees"
    settings.keyboard.low = settings.keyboard.high = 61
    settings.keyboard.require_octave = True
    view = opened(KeyboardNotes())
    press(view, "Shift+1")
    press(view, "A")
    assert view.answered and not view.missed
    view.close()


def test_construction_degree_caption_is_shown_on_the_staff(app: QApplication) -> None:
    """
    Show the key and octave context below the input staff rather than hiding the target prompt.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.note_names.naming = "degrees"
    settings.construction.key_signature = True
    settings.construction.keys = {-2}
    view = ExerciseView(NoteConstruction(), rng=random.Random(4))
    assert view.question is not None
    assert view.input_staff.caption == view.question.prompt
    assert view.input_staff.caption == "B♭M 6̂₃"
    assert view.prompt.isHidden()
    preview = QuestionPreview("Note Construction", question=view.question)
    # noinspection PyProtectedMember
    assert preview._answer_text() == view.question.answer
    preview.close()
    view.close()


def test_note_name_labels_and_degree_group(app: QApplication) -> None:
    """
    Keep text visible beside every preview and both degree subtypes in one exclusive group.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    panel = NoteNameSettingsPanel(settings.note_names)
    radios = panel.naming_radios
    assert radios["letters"].text() == "Letters"
    assert radios["solfege"].text() == "Solfège"
    group = radios["degrees"].parentWidget()
    assert isinstance(group, QGroupBox)
    assert group.title() == "Scale degrees"
    assert radios["functions"].parentWidget() is group
    assert radios["degrees"].text() == "Caret"
    assert radios["functions"].text() == "Function"
    for naming in ("functions", "letters", "degrees", "solfege"):
        radios[naming].click()
        assert sum(r.isChecked() for r in radios.values()) == 1
        assert settings.note_names.naming == naming
        settings.note_names.naming = "letters"
        load_note_names()
        assert settings.note_names.naming == naming
    panel.close()


@pytest.mark.parametrize("key", [-7, -2, 0, 1, 7])
def test_function_names_and_exercise_answers(key: int) -> None:
    """
    Check function names against each major scale and exercise answer banks.

    Parameters
    ----------
    key : int
        The major key signature.
    """
    functions = ["Tonic", "Supertonic", "Mediant", "Subdominant", "Dominant", "Submediant", "Leading tone"]
    tonic = Note.parse(f"{MAJOR_KEYS[key].replace('♭', 'b').replace('♯', '#')}4")
    notes = build(tonic, intervals=SCALES["Major (Ionian)"])
    assert [settings.spell(n, naming="functions", key=key) for n in notes[:7]] == functions
    settings.note_names.naming = "functions"
    settings.note_names.key_signatures = {key}
    settings.note_names.accidentals = True
    settings.keyboard.key_signature = True
    settings.keyboard.keys = {key}
    settings.keyboard.require_octave = True
    settings.construction.key_signature = True
    settings.construction.keys = {key}
    rng = random.Random(18)
    for _ in range(30):
        question = NoteNames().generate(rng)
        assert question.answer in question.choices
        keys = choice_keys(question.choices)
        assert len(set(keys)) == len(keys)
        question = KeyboardNotes().generate(rng)
        assert question.answer.split(" / ")[0] in question.choices
        question = NoteConstruction().generate(rng)
        assert question.construct is not None
        assert question.answer == settings.spell(
            question.construct,
            naming="functions",
            key=key,
            octave=True,
        )
        assert question.answer == note_name(question.construct, key=key)


def test_function_notation_uses_degree_shortcuts_and_accessible_names(app: QApplication) -> None:
    """
    Answer an altered function with the degree shortcut and announce the chosen function in words.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.note_names.naming = "functions"
    settings.keyboard.low = settings.keyboard.high = 61
    settings.keyboard.require_octave = True
    view = opened(KeyboardNotes())
    press(view, "Shift+1")
    press(view, "A")
    assert view.answered and not view.missed
    assert note_words(Note.parse("F4"), key=1) == "lowered leading tone, octave 4"
    view.close()


@pytest.mark.parametrize(
    ("note", "expected"),
    [
        ("C#4", "Raised Tonic"),
        ("Cb4", "Lowered Tonic"),
        ("Cx4", "Doubly raised Tonic"),
        ("Cbb4", "Doubly lowered Tonic"),
    ],
)
def test_altered_functions_use_words(
    note: str,
    *,
    expected: str,
) -> None:
    """
    Spell altered functions in words while keeping caret accidentals unchanged.

    Parameters
    ----------
    note : str
        The chromatic note in C major.
    expected : str
        The full function label. Keyword-only.
    """
    assert settings.spell(Note.parse(note), naming="functions") == expected


def test_function_buttons_fit_the_answer_area(app: QApplication) -> None:
    """
    Give long altered function names enough width and keep their shortcuts unique.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    settings.note_names.naming = "functions"
    settings.note_names.accidentals = True
    settings.note_names.key_signatures = {7}
    view = opened(NoteNames())
    question = view.question
    assert question is not None and question.grid is not None
    assert max(col for _, col in question.grid.values()) == 3
    assert all(button.width() >= button.minimumSizeHint().width() for button in view.buttons)
    assert all(button.height() >= button.minimumSizeHint().height() for button in view.buttons)
    assert all(button.geometry().right() < view.choice_area.width() for button in view.buttons)
    assert any("Lowered\n" in button.text() for button in view.buttons)
    keys = choice_keys(question.choices)
    assert len(set(keys)) == len(keys)
    view.close()


def test_minor_degree_selection_and_notes_only_preview(app: QApplication) -> None:
    """
    Practice only the seventh in A minor and read a Notes Only question independently of degree naming.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.construction
    cfg.key_signature, cfg.major, cfg.minor = True, False, True
    cfg.keys, cfg.minor_keys, cfg.degrees = {0}, {0}, {7}
    cfg.accidentals = False
    settings.note_names.naming = "functions"
    exercise = NoteConstruction()
    rng = random.Random(4)
    for _ in range(12):
        q = exercise.generate(rng)
        assert q.construct is not None and q.construct.name == "G"
        assert "Subtonic" in q.answer
    assert settings.spell(Note.parse("G#4"), naming="functions", key=0, minor=True) == "Leading tone"

    cfg.question_type, cfg.octave = "notes", False
    signature = exercise.settings_signature()
    cfg.keys, cfg.minor_keys, cfg.degrees = {3}, {-4}, {1}
    assert exercise.settings_signature() == signature
    q = exercise.generate(rng)
    assert q.construct is not None
    assert QuestionPreview(exercise.name, question=q)._answer_text() == q.construct.name == q.answer


def test_plain_degree_checkbox_uses_the_native_label(app: QApplication) -> None:
    """
    Render an ordinary checkbox label through the same native control as the settings pane.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    native, degree = QCheckBox("All degrees"), DegreeCheckBox("All degrees")
    for box in (native, degree):
        box.setChecked(True)
        box.resize(140, 32)
    assert native.grab().toImage() == degree.grab().toImage()
