"""
Scale identification draws complete scales and keeps staff and scale signatures independent.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from PySide6.QtWidgets import QCheckBox, QRadioButton

from alto import settings
from alto.audio import sounds
from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import ScaleIdentification
from alto.theory.pitch import Note
from alto.theory.scales import (
    SCALES,
    build,
    mode_tonic,
)
from alto.ui import icons
from alto.ui.dropdown import FieldComboBox
from alto.ui.exercise_view import ExerciseView
from alto.ui.home import EXERCISE_ICONS
from alto.ui.main_window import MainWindow
from alto.ui.settings_panel import (
    KeySignatureSettingsPanel,
    load_scale_identification,
    settings_panel_for,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def test_every_clef_mode_and_scale_key_produces_the_written_scale() -> None:
    """
    Check exact note spelling, ascending octaves, distinct choices and serialization across every selectable scale.
    """
    cfg = settings.scale_identification
    rng = random.Random(31)
    for clef in settings.CLEFS:
        for mode in settings.KEY_MODES:
            for key in range(-7, 8):
                cfg.clefs, cfg.modes, cfg.keys, cfg.staff_keys = {clef}, {mode}, {key}, {-key}
                q = ScaleIdentification().generate(rng)
                notes = [chord[0] for chord in q.staff]
                assert len(notes) == 8 and all(len(chord) == 1 for chord in q.staff)
                assert q.clef == clef and q.key == -key
                assert notes[0].name == mode_tonic(key, mode=mode).name
                assert notes[:-1] == build(notes[0], intervals=SCALES[mode])
                assert notes[-1].diatonic - notes[0].diatonic == 7
                assert notes[-1].midi - notes[0].midi == 12
                assert notes[-1].accidental == notes[0].accidental
                assert q.answer.startswith(notes[0].name + " ")
                kind = "Major" if mode == "Major (Ionian)" else "minor" if mode == "Natural minor (Aeolian)" else mode
                assert all(choice.endswith(" " + kind) for choice in q.choices)
                assert len(q.choices) == len(set(q.choices)) == 6 and q.check(q.answer)
                assert not q.caption and q.answer not in q.prompt
                assert Question.from_dict(q.to_dict()) == q


def test_settings_are_saved_loaded_and_isolated_from_construction(app: QApplication) -> None:
    """
    Edit the requested options and ensure only identification settings and its scheduler signature change.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    exercise = ScaleIdentification()
    before = exercise.settings_signature()
    panel = settings_panel_for(exercise)
    assert isinstance(panel, KeySignatureSettingsPanel)
    assert panel.cfg is settings.scale_identification
    assert panel.staff_keys_row is not None and panel.staff_key_list is not None
    assert panel.octave_row is None and panel.steps_row is None
    motion = {button.text(): button for button in panel.findChildren(QRadioButton)}
    assert motion["Ascending"].isChecked()
    motion["Descending"].click()
    assert motion["Descending"].isChecked() and not motion["Ascending"].isChecked()
    panel.boxes["alto"].setChecked(True)
    panel.staff_key_list.boxes[-2].setChecked(True)
    panel.key_list.boxes[5].setChecked(False)
    assert exercise.settings_signature() != before
    settings.scale_identification.staff_keys = {0}
    settings.scale_identification.keys = set(range(-7, 8))
    settings.scale_identification.motion = "ascending"
    load_scale_identification()
    assert settings.scale_identification.motion == "descending" and settings.scale_construction.motion == "ascending"
    assert settings.scale_identification.staff_keys == {0, -2}
    assert "alto" in settings.scale_identification.clefs and 5 not in settings.scale_identification.keys
    assert settings.scale_construction.staff_keys == {0} and 5 in settings.scale_construction.keys
    window = MainWindow()
    assert settings.scale_identification.staff_keys == {0, -2}
    window.close()


def test_replacement_keeps_the_icon_and_shows_an_answerable_staff(app: QApplication) -> None:
    """
    Keep the existing scale icon and render an identification question with the normal answer controls.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert ScaleIdentification in REGISTRY
    assert all(cls.name != "Scale Spelling" for cls in REGISTRY)
    assert EXERCISE_ICONS["ScaleIdentification"] == icons.EXERCISE_SCALES
    view = ExerciseView(ScaleIdentification(), rng=random.Random(5))
    view.show()
    assert view.question is not None and view.staff.isVisible()
    view.buttons[view.question.choices.index(view.question.answer)].click()
    assert view.answered


def test_scale_button_settings_limit_choices_or_accept_a_tonic_and_mode(app: QApplication) -> None:
    """Switch answer modes through Settings and submit a two-part answer."""
    exercise = ScaleIdentification()
    panel = settings_panel_for(exercise)
    assert isinstance(panel, KeySignatureSettingsPanel)
    count = panel.findChild(FieldComboBox)
    assert count is not None
    count.setCurrentIndex(count.findData(4))
    assert len(exercise.generate(random.Random(3)).choices) == 4
    all_buttons = next(button for button in panel.findChildren(QRadioButton) if button.text() == "All")
    all_buttons.click()
    load_scale_identification()
    assert settings.scale_identification.button_mode == "all"
    assert settings.scale_identification.button_count == 4

    view = ExerciseView(exercise, rng=random.Random(3))
    assert view.question is not None
    assert len(view.question.choices) == 21 and len(view.question.octaves or []) == 7
    tonic, mode = view.question.answer.split(" ", 1)
    buttons = {button.text(): button for button in view.buttons}
    buttons[mode].click()
    assert not view.answered
    buttons[tonic].click()
    assert view.answered
    view.close()


@pytest.mark.parametrize(("label", "answer"), [("Mode", "Major"), ("Key", "C")])
def test_question_type_asks_for_one_part(app: QApplication, label: str, answer: str) -> None:
    """Save a question type and check that it accepts the requested part alone."""
    exercise = ScaleIdentification()
    panel = settings_panel_for(exercise)
    assert isinstance(panel, KeySignatureSettingsPanel)
    boxes = {box.text(): box for box in panel.findChildren(QCheckBox) if box.text() in {"Key", "Mode"}}
    assert all(box.isChecked() for box in boxes.values())
    boxes["Key" if label == "Mode" else "Mode"].click()
    assert boxes[label].isChecked() and not boxes[label].isEnabled()
    load_scale_identification()
    cfg = settings.scale_identification
    cfg.keys, cfg.modes = {0}, {"Major (Ionian)"}
    for button_mode in ("limited", "all"):
        cfg.button_mode = button_mode
        question = exercise.generate(random.Random(4))
        assert question.answer == answer and answer in question.choices
        assert question.octaves is None and question.check(answer)


def test_empty_selections_have_usable_defaults() -> None:
    """
    Generate a valid major scale in treble clef without a signature when nothing is selected.
    """
    cfg = settings.scale_identification
    cfg.clefs, cfg.modes, cfg.keys, cfg.staff_keys = set(), set(), set(), set()
    q = ScaleIdentification().generate(random.Random(2))
    assert q.clef == "treble" and q.key == 0 and q.answer == "C Major"
    assert all(choice.endswith(" Major") for choice in q.choices)


def test_answer_buttons_use_only_selected_scale_types() -> None:
    """
    Keep all answer choices within the selected scale types across repeated questions.
    """
    settings.scale_identification.modes = {"Dorian", "Mixolydian"}
    rng = random.Random(5)
    for _ in range(50):
        q = ScaleIdentification().generate(rng)
        assert all(choice.split(" ", 1)[1] in {"Dorian", "Mixolydian"} for choice in q.choices)
        assert q.answer in q.choices


def test_correct_answer_tracks_playback_and_waits_for_completion(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Highlight only the sounding note and keep the question until the audio completion callback.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Captures the playback callback instead of using audio hardware.
    """
    callbacks: list[Callable[[int | None], object]] = []
    played: list[int] = []

    def play(
        midis: list[list[Note]],
        *,
        gap_ms: int,
        warmup: bool,
        on_step: Callable[[int | None], object],
    ) -> None:
        """
        Capture the melody and visual clock callback.

        Parameters
        ----------
        warmup : bool
            Silently initialize audio streams before starting playback.
        midis : list of int
            Notes to play.
        gap_ms : int
            The note spacing.
        on_step : callable
            The visual callback.

        """
        assert warmup
        assert gap_ms == 280
        played.extend(note.midi for column in midis for note in column)
        callbacks.append(on_step)

    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(sounds, "play_notes", play)
    view = ExerciseView(ScaleIdentification(), rng=random.Random(2))
    view.show()
    question = view.question
    assert question is not None
    view.buttons[question.choices.index(question.answer)].click()
    assert played == [column[0].midi for column in question.staff]
    assert view.answered and not view._advance.isActive()
    assert not view.staff.column_colors and view.staff.note_color is None
    for index in range(8):
        callbacks[0](index)
        assert list(view.staff.column_colors) == [index]
        assert view.staff.note_color is None and not view._advance.isActive()
        assert view.question is question
    callbacks[0](None)
    assert view._advance.isActive() and view.staff.note_color is not None
    view.next_question()
    callbacks[0](3)
    assert not view.staff.column_colors and view.staff.note_color is None
