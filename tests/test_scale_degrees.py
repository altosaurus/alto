"""
Scale-degree names follow the question's key in each exercise that
uses them.
"""

from __future__ import annotations

import random
from dataclasses import replace
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
from alto.ui import motion
from alto.ui.degree_text import DegreeCheckBox
from alto.ui.exercise_settings import (
    load_keyboard,
    load_note_names,
    save_note_names,
)
from alto.ui.exercise_view import (
    ExerciseView,
    choice_keys,
    note_name,
    note_words,
    second_row_keys,
)
from alto.ui.question_preview import QuestionPreview
from alto.ui.settings_panel import KeyboardSettingsPanel, NoteNameSettingsPanel
from alto.ui.store import store
from keys import (
    opened,
    press,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


@pytest.mark.parametrize("key", range(-7, 8))
def test_diatonic_degrees_follow_the_major_scale(key: int) -> None:
    """
    Check all seven degrees against scale spelling, including the
    extreme signatures.

    Parameters
    ----------
    key : int
        The major key signature.
    """
    tonic = Note.parse(
        f"{MAJOR_KEYS[key].replace('♭', 'b').replace('♯', '#')}4",
    )
    notes = build(tonic, intervals=SCALES["Major (Ionian)"])
    assert [
        settings.spell(n, naming="degrees", key=key) for n in notes[:7]
    ] == [f"{i}̂" for i in range(1, 8)]
    for index, note in enumerate(notes[:7], start=1):
        lowered = Note(
            note.octave,
            letter=note.letter,
            accidental=note.accidental - 1,
        )
        raised = Note(
            note.octave,
            letter=note.letter,
            accidental=note.accidental + 1,
        )
        assert (
            settings.spell(lowered, naming="degrees", key=key) == f"♭{index}̂"
        )
        assert settings.spell(raised, naming="degrees", key=key) == f"♯{index}̂"


@pytest.mark.parametrize("accidentals", [False, True])
def test_identification_degree_answers_and_columns(accidentals: bool) -> None:
    """
    Check answers, key context and degree columns with multiple active
    signatures.

    Parameters
    ----------
    accidentals : bool
        Whether chromatic notes are included.
    """
    cfg = settings.note_names
    cfg.naming, cfg.accidentals, cfg.key_signatures = (
        "degrees",
        accidentals,
        {-7, -2, 0, 1, 7},
    )
    rng = random.Random(12)
    for _ in range(200):
        question = NoteNames().generate(rng)
        assert question.answer in question.choices
        assert question.check(question.answer)
        assert question.grid is not None
        assert len(set(question.choices)) == len(question.choices)
        assert question.caption == ""
        for label in question.choices:
            assert (
                question.grid[label][1] == int(label.replace("̂", "")[-1]) - 1
            )
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
    Check that keyboard answers remain reachable for every key and
    spelling.

    Parameters
    ----------
    signature : bool
        Whether to show a key signature.
    octave : bool
        Whether to require an octave. Keyword-only.
    """
    settings.keyboard.naming = "degrees"
    cfg = settings.keyboard
    cfg.key_signature, cfg.require_octave, cfg.keys = (
        signature,
        octave,
        {-7, -2, 0, 1, 7},
    )
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
            degree, _, number = (
                answer.partition(question.joiner)
                if octave
                else (answer, "", "")
            )
            assert degree in question.choices
            if octave:
                assert question.octaves is not None
                assert number in question.octaves
        assert question.prompt == ""
    if not signature:
        cfg.low = cfg.high = 61
        question = KeyboardNotes().generate(rng)
        suffix = " / 4" if octave else ""
        assert {question.answer, *question.accept} == {
            f"♯1̂{suffix}",
            f"♭2̂{suffix}",
        }


def test_construction_degree_prompt_and_accessible_caret() -> None:
    """
    Keep target labels, placement feedback and accessible names in the
    same key.
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
        assert question.answer == note_name(
            question.construct,
            key=question.key,
        )
        assert question.caption == question.prompt
        degree, octave = question.answer.split(" / ")
        subscript = octave.translate(
            str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋"),
        )
        assert question.prompt == f"GM {degree}{subscript}"
    note = Note.parse("F4")
    assert note_name(note, key=1) == "♭7̂ / 4"
    assert note_words(note, key=1) == "flat degree 7, octave 4"
    assert (
        note_name(note) == "F4"
    )  # scale construction has no degree reference


def test_degree_shortcuts_leave_octave_keys_available() -> None:
    """
    Ensure chromatic degree banks have unique shortcuts and a separate
    octave row.
    """
    labels = [
        f"{sign}{degree}"
        for sign in ("", "♯", "♭", "𝄪", "𝄫")
        for degree in range(1, 8)
    ]
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
    Check the settings control offers degrees and persists the
    selection.

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


def test_staff_and_keyboard_naming_stay_independent(app: QApplication) -> None:
    """
    Migrate the shared preference once, then change either exercise.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    store().setValue("noteNames/naming", "solfege")
    load_note_names()
    load_keyboard()
    staff = NoteNameSettingsPanel(settings.note_names)
    keyboard = KeyboardSettingsPanel(settings.keyboard)
    keyboard.names_row.click()
    motion.settle()
    assert keyboard.stack.currentIndex() == 3
    assert keyboard.naming_radios["solfege"].isChecked()
    exercise = KeyboardNotes()
    rng = random.Random(4)
    original = exercise.settings_signature()
    staff.naming_radios["degrees"].click()
    load_keyboard()
    assert settings.keyboard.naming == "solfege"
    assert exercise.settings_signature() == original
    assert "solfège" in exercise.card_prompt(exercise.generate(rng))
    keyboard.naming_radios["letters"].click()
    load_note_names()
    load_keyboard()
    assert settings.note_names.naming == "degrees"
    assert settings.keyboard.naming == "letters"
    assert keyboard.name_picture.naming == "letters"
    assert exercise.settings_signature() != original
    question = exercise.generate(rng)
    assert "C" in question.choices and "1̂" not in question.choices
    assert "letter" in exercise.card_prompt(question)
    keyboard.close()
    staff.close()


def test_chromatic_degree_and_octave_shortcuts_answer_the_question(
    app: QApplication,
) -> None:
    """
    Answer a black key with its altered degree and octave using the
    actual buttons' shortcuts.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.keyboard.naming = "degrees"
    settings.keyboard.low = settings.keyboard.high = 61
    settings.keyboard.require_octave = True
    view = opened(KeyboardNotes())
    press(view, "Shift+1")
    press(view, "A")
    assert view.session.answered and not view.session.missed
    view.close()


def test_construction_degree_caption_is_shown_on_the_staff(
    app: QApplication,
) -> None:
    """
    Show the key and octave context below the input staff rather than
    hiding the target prompt.

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
    assert view.question_view.note_input.caption == view.question.prompt
    assert view.question_view.note_input.caption == "B♭M 6̂₃"
    assert view.prompt.isHidden()
    preview = QuestionPreview("Note Construction", question=view.question)
    # noinspection PyProtectedMember
    assert preview._answer_text() == view.question.answer
    preview.close()
    view.close()


def test_note_name_labels_and_degree_group(app: QApplication) -> None:
    """
    Keep text visible beside every preview and both degree subtypes in
    one exclusive group.

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
    radios["degrees"].click()
    panel.scale_keys.minor_keys.boxes[1].click()
    panel.scale_keys.major_keys.boxes[0].click()
    settings.note_names.minor_keys.clear()
    load_note_names()
    assert settings.note_names.minor_keys == {1}
    assert not settings.note_names.key_signatures
    exercise = NoteNames()
    settings.note_names.clefs = {"treble"}
    position = Note.parse("E4").diatonic
    settings.note_names.ranges = {"treble": (position, position)}
    q = exercise.generate(random.Random(0))
    assert (
        q.minor
        and q.answer == "1̂"
        and "E natural minor" in exercise.card_prompt(q)
    )
    assert q.grid[q.answer] == (0, 0)
    panel.close()


@pytest.mark.parametrize("key", [-7, -2, 0, 1, 7])
def test_function_names_and_exercise_answers(key: int) -> None:
    """
    Check function names against each major scale and exercise answer
    banks.

    Parameters
    ----------
    key : int
        The major key signature.
    """
    functions = [
        "Tonic",
        "Supertonic",
        "Mediant",
        "Subdominant",
        "Dominant",
        "Submediant",
        "Leading tone",
    ]
    tonic = Note.parse(
        f"{MAJOR_KEYS[key].replace('♭', 'b').replace('♯', '#')}4",
    )
    notes = build(tonic, intervals=SCALES["Major (Ionian)"])
    assert [
        settings.spell(n, naming="functions", key=key) for n in notes[:7]
    ] == functions
    settings.note_names.naming = "functions"
    settings.note_names.key_signatures = {key}
    settings.note_names.accidentals = True
    settings.keyboard.naming = "functions"
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


def test_function_notation_uses_degree_shortcuts_and_accessible_names(
    app: QApplication,
) -> None:
    """
    Answer an altered function with the degree shortcut and announce the
    chosen function in words.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.note_names.naming = "functions"
    settings.keyboard.naming = "functions"
    settings.keyboard.low = settings.keyboard.high = 61
    settings.keyboard.require_octave = True
    view = opened(KeyboardNotes())
    press(view, "Shift+1")
    press(view, "A")
    assert view.session.answered and not view.session.missed
    assert (
        note_words(Note.parse("F4"), key=1) == "lowered leading tone, octave 4"
    )
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
    Spell altered functions in words while keeping caret accidentals
    unchanged.

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
    Give long altered function names enough width and keep their
    shortcuts unique.

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
    assert all(
        button.width() >= button.minimumSizeHint().width()
        for button in view.answer_controls.buttons
    )
    assert all(
        button.height() >= button.minimumSizeHint().height()
        for button in view.answer_controls.buttons
    )
    assert all(
        button.geometry().right() < view.answer_controls.choice_area.width()
        for button in view.answer_controls.buttons
    )
    assert any(
        "Lowered\n" in button.text() for button in view.answer_controls.buttons
    )
    keys = choice_keys(question.choices)
    assert len(set(keys)) == len(keys)
    view.close()


def test_minor_degree_selection_and_notes_only_preview(
    app: QApplication,
) -> None:
    """
    Practice only the seventh in A minor and read a Notes Only question
    independently of degree naming.

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
    assert (
        settings.spell(
            Note.parse("G#4"),
            naming="functions",
            key=0,
            minor=True,
        )
        == "Leading tone"
    )

    cfg.question_type, cfg.octave = "notes", False
    signature = exercise.settings_signature()
    cfg.keys, cfg.minor_keys, cfg.degrees = {3}, {-4}, {1}
    assert exercise.settings_signature() == signature
    q = exercise.generate(rng)
    assert q.construct is not None
    assert (
        QuestionPreview(exercise.name, question=q)._answer_text()
        == q.construct.name
        == q.answer
    )


def test_plain_degree_checkbox_uses_the_native_label(
    app: QApplication,
) -> None:
    """
    Render an ordinary checkbox label through the same native control as
    the settings pane.

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


def test_scale_answers_match_the_written_note_and_degree() -> None:
    """Check every degree and key spelling across the daily catalog."""
    cfg = settings.note_names
    cfg.scale_answer = cfg.accidentals = cfg.require_octave = True
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (28, 34)}
    exercise = NoteNames()
    assert "M means major" in exercise.instructions()
    catalog_signature = exercise.settings_signature()
    cards = list(exercise.daily_candidates(random.Random(4)))
    assert exercise.card_count() == len({q.item_key() for q in cards}) == 105
    for q in cards:
        note = q.staff[0][0]
        scale = build(
            Note.parse(MAJOR_KEYS[q.key] + "4"),
            intervals=SCALES["Major (Ionian)"],
        )
        degree = next(
            i for i, pitch in enumerate(scale, 1) if pitch.name == note.name
        )
        assert q.caption == f"{degree}̂ M"
        assert q.staff_signature == 0 and q.octaves is None
        assert q.check(f"{MAJOR_KEYS[q.key]} major")
        assert q.prompt == exercise.card_prompt(q)
    original = cards[0]
    cfg.scale_keys = {original.key}
    assert exercise.settings_signature() != catalog_signature
    refreshed = exercise.review_question(original, same_settings=False)
    assert refreshed is not None and refreshed.choices == [original.answer]
    cfg.scale_answer = False
    assert exercise.review_question(original, same_settings=False) is None


def test_scale_answer_setting_and_buttons(app: QApplication) -> None:
    """
    Select Scale, narrow its keys, reload it, and answer from the staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.note_names
    cfg.key_signatures = {-2}
    panel = NoteNameSettingsPanel(cfg)
    assert panel.names_row.accessibleName() == "Answer Type"
    assert (
        "scale" not in KeyboardSettingsPanel(settings.keyboard).naming_radios
    )
    panel.naming_radios["scale"].click()
    assert panel.names_row.value.text() == "Scale"
    assert panel.octave_row.isHidden() and panel.accidentals_row.isHidden()
    for count, box in panel.key_boxes.items():
        if count not in {-2, 2, 6}:
            box.click()
    cfg.scale_answer = False
    cfg.scale_keys.clear()
    load_note_names()
    assert cfg.scale_answer and cfg.scale_keys == {-2, 2, 6}
    assert cfg.key_signatures == {-2}
    view = opened(NoteNames())
    q = view.question
    assert q and set(q.choices) == {"B♭ major", "D major", "F♯ major"}
    assert (
        view.question_view.staff.key == 0
        and view.question_view.staff.caption == q.caption
    )
    assert {b.text() for b in view.answer_controls.buttons} == {
        "B♭",
        "D",
        "F♯",
    }
    assert all(
        button.icon().isNull() for button in view.answer_controls.buttons
    )
    view._place_midi(q.staff[0][0].midi)
    assert not view.session.answered
    next(
        b
        for b in view.answer_controls.buttons
        if b.text() == q.answer.split()[0]
    ).click()
    assert view.session.answered
    panel.naming_radios["letters"].click()
    assert cfg.active_keys() == [-2] and panel.key_boxes[-2].isChecked()
    view.close()
    panel.close()


def test_different_staff_and_question_keys_in_the_exercise(
    app: QApplication,
) -> None:
    """
    Identify F sharp on a two-sharp staff as degree 7 in G.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.note_names
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (31, 31)}
    cfg.staff_keys, cfg.key_signatures, cfg.naming = {2}, {1}, "degrees"
    view = opened(NoteNames())
    q = view.question
    assert q and q.answer == "7̂" and "in G major" in view.prompt.text()
    assert (
        view.question_view.staff.key == 2
        and view.question_view.staff.columns
        == [
            [Note.parse("F#4")],
        ]
    )
    assert all(
        button.icon().isNull() for button in view.answer_controls.buttons
    )
    view._place_midi(q.staff[0][0].midi)
    assert view.session.answered
    view.close()

    cfg.scale_answer, cfg.scale_keys = True, {1}
    view = opened(NoteNames())
    q = view.question
    assert (
        q and q.check("G major") and view.question_view.staff.caption == "7̂ M"
    )
    assert (
        view.question_view.staff.key == 2
        and view.question_view.staff.columns
        == [
            [Note.parse("F#4")],
        ]
    )
    assert view.answer_controls.buttons[0].icon().isNull()
    view.close()


def test_independent_key_selections_and_saved_cards(app: QApplication) -> None:
    """
    Keep each selected pair of keys through review.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.note_names
    store().setValue("noteNames/keys", "1")
    load_note_names()
    assert cfg.staff_keys == cfg.key_signatures == {1}
    panel = NoteNameSettingsPanel(cfg)
    assert panel.staff_key_row.accessibleName() == "Staff Key"
    assert panel.keys_row.accessibleName() == "Scale Key"
    panel.staff_keys.boxes[-1].click()
    panel.key_boxes[2].click()
    load_note_names()
    assert cfg.staff_keys == {-1, 1} and cfg.key_signatures == {1, 2}
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (28, 28)}
    cfg.naming = "functions"
    exercise = NoteNames()
    cards = list(exercise.daily_candidates(random.Random(12)))
    assert {(q.key, q.written_key) for q in cards} == {
        (1, -1),
        (1, 1),
        (2, -1),
        (2, 1),
    }
    assert len({q.item_key() for q in cards}) == exercise.card_count() == 4
    for q in cards:
        restored = type(q).from_dict(q.to_dict())
        assert exercise.review_question(restored, same_settings=False) == q
    original = next(q for q in cards if q.key == 1 and q.written_key == 1)
    legacy = original.to_dict()
    del legacy["staff_signature"], legacy["identify_scale"]
    assert type(original).from_dict(legacy).item_key() == original.item_key()
    cfg.staff_keys = {-1}
    assert exercise.review_question(original, same_settings=False) is None
    panel.naming_radios["scale"].click()
    assert cfg.staff_keys == {-1}
    catalog = exercise.settings_signature()
    cfg.staff_keys.add(1)
    assert exercise.settings_signature() != catalog
    q = exercise.generate(random.Random(1))
    legacy = q.to_dict()
    del legacy["identify_scale"]
    del legacy["minor_form"]
    legacy["answer"] = q.answer.split()[0]
    legacy["choices"] = [c.split()[0] for c in q.choices]
    digit = q.caption[0]
    for caption in (f"Scale degree {digit}", digit, f"{digit}̂"):
        legacy["caption"] = caption
        assert type(q).from_dict(legacy) == q
    panel.close()


def test_legacy_minor_reference_moves_to_minor_tab() -> None:
    """Migrate minor degree settings and keep the staff keys."""
    prefs = store()
    prefs.setValue("noteNames/keys", "1,2")
    prefs.setValue("noteNames/minorDegrees", "true")
    cfg = settings.note_names
    for _ in range(2):
        load_note_names()
        assert cfg.key_selections() == (set(), {1, 2})
        assert cfg.staff_keys == {1, 2}
        save_note_names()
    assert not prefs.contains("noteNames/minorDegrees")


def test_mixed_keys_and_minor_scale_buttons(app: QApplication) -> None:
    """
    Grade relative keys independently and keep minor-only Scale choices.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.note_names
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (30, 30)}
    cfg.naming = "degrees"
    exercise = NoteNames()
    panel = NoteNameSettingsPanel(cfg)
    picker = panel.scale_keys
    assert [picker.tabText(i) for i in range(2)] == ["Major", "Minor"]
    assert picker.major_keys.boxes[0].text() == "CM"
    assert picker.minor_keys.boxes[0].text() == "Am"
    picker.minor_keys.boxes[0].click()
    assert panel.keys_row.value.text() == "1 major · 1 minor"
    mixed_deck = exercise.settings_signature()
    cards = list(exercise.daily_candidates(random.Random(12)))
    assert exercise.card_count() == len({q.item_key() for q in cards}) == 2
    major, minor = sorted(cards, key=lambda q: q.minor)
    assert (major.answer, minor.answer) == ("3̂", "5̂")
    assert "C major" in exercise.card_prompt(major)
    assert "A natural minor" in exercise.card_prompt(minor)
    picker.major_keys.boxes[0].click()
    assert exercise.settings_signature() != mixed_deck
    assert not picker.minor_keys.boxes[0].isEnabled()
    assert exercise.review_question(major, same_settings=False) is None
    assert exercise.review_question(minor, same_settings=False) == minor

    panel.naming_radios["scale"].click()
    major_scale_deck = exercise.settings_signature()
    picker.minor_keys.boxes[0].click()
    assert exercise.settings_signature() != major_scale_deck
    picker.minor_keys.boxes[1].click()
    for box in picker.major_keys.boxes.values():
        box.click()
    assert panel.keys_row.value.text() == "0 major · 2 minor"
    cfg.scale_minor_keys.clear()
    load_note_names()
    assert cfg.key_selections() == (set(), {0, 1})
    assert NoteNameSettingsPanel(cfg).scale_keys.currentIndex() == 1
    cards = list(exercise.daily_candidates(random.Random(12)))
    for q in cards:
        assert q.minor and q.written_key == 0 and q.identify_scale
        degree = 5 if q.key == 0 else 1
        assert q.caption == f"{degree}̂ m {q.minor_form}"
        mode = q.minor_form.split()[0]
        assert set(q.choices) == {f"A {mode} minor", f"E {mode} minor"}
    assert {q.minor_form for q in cards} == {"natural", "harmonic"}
    assert exercise.card_count() == len({q.item_key() for q in cards}) == 4
    view = opened(exercise)
    q = view.question
    assert q and q.minor and view.question_view.staff.caption == q.caption
    assert view.prompt.isHidden()
    assert {b.text() for b in view.answer_controls.buttons} == {"A", "E"}
    assert all(b.icon().isNull() for b in view.answer_controls.buttons)
    view.answer_controls.buttons[q.choices.index(q.answer)].click()
    assert view.session.answered
    view.close()
    panel.close()


def test_minor_forms_spell_raised_degrees_and_survive_review() -> None:
    """Check minor scale spellings and both melodic directions."""
    cfg = settings.note_names
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (28, 34)}
    cfg.scale_answer, cfg.scale_keys = True, set()
    cfg.scale_minor_keys = set(range(-7, 8))
    exercise = NoteNames()
    rng = random.Random(7)
    cards = list(exercise.daily_candidates(rng))
    assert exercise.card_count() == len({q.item_key() for q in cards}) == 270
    forms = {
        "natural": "Natural minor (Aeolian)",
        "harmonic": "Harmonic minor",
        "melodic (asc.)": "Melodic minor",
        "melodic (desc.)": "Natural minor (Aeolian)",
    }
    for form in forms:
        expected = {6, 7} if form.startswith("melodic") else set(range(1, 8))
        for key in cfg.scale_minor_keys:
            assert {
                int(q.caption[0])
                for q in cards
                if q.minor_form == form and q.key == key
            } == expected
    for q in cards:
        tonic = Note.parse(q.answer.split()[0] + "4")
        pitches = build(tonic, intervals=SCALES[forms[q.minor_form]])
        degree = int(q.caption[0])
        assert q.staff[0][0].name == pitches[degree - 1].name
        assert q.caption == f"{degree}̂ m {q.minor_form}"
        assert q.check(q.answer)
        restored = type(q).from_dict(q.to_dict())
        refreshed = exercise.review_question(restored, same_settings=False)
        assert refreshed and refreshed.item_key() == q.item_key()
    # Older melodic cards could ask degrees shared by both directions.
    natural = next(
        q
        for q in cards
        if q.minor_form == "natural" and q.caption.startswith("1̂")
    )
    assert (
        exercise.review_question(
            replace(natural, staff=[]),
            same_settings=False,
        )
        is None
    )
    for form in ("melodic (asc.)", "melodic (desc.)"):
        old = replace(
            natural,
            minor_form=form,
            caption=f"1̂ m {form}",
            answer=natural.answer.replace("natural", "melodic"),
            prompt=natural.prompt.replace("natural", "melodic"),
        )
        for same in (True, False):
            assert exercise.review_question(old, same_settings=same) is None
    generated = [exercise.generate(rng) for _ in range(60)]
    assert {q.minor_form for q in generated} == set(forms)
    assert {q.item_key() for q in generated} <= {q.item_key() for q in cards}
