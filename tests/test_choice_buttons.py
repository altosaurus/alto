"""The shared Buttons option across exercise types, required answers and stored preferences."""

import random

import pytest
from PySide6.QtWidgets import QApplication, QRadioButton

from alto import settings
from alto.exercises import REGISTRY
from alto.exercises.base import ChoiceExercise, Exercise
from alto.exercises.library import ChordQualities, ClefBasics, KeyboardNotes, NotationIdentification
from alto.ui import motion
from alto.ui.dropdown import FieldComboBox
from alto.ui.exercise_settings import load_choice_buttons
from alto.ui.exercise_view import ExerciseView
from alto.ui.store import store


@pytest.mark.parametrize("cls", REGISTRY, ids=lambda cls: cls.__name__)
def test_each_button_answer_has_a_buttons_submenu(app: QApplication, cls: type[Exercise]) -> None:
    """
    Check every registered exercise at its normal entry point, including the construction exceptions.

    Parameters
    ----------
    app : QApplication
        The shared application.
    cls : type of Exercise
        The registered exercise.
    """
    settings.clef_basics.question_type = "identification"
    view = ExerciseView(cls(), rng=random.Random(22))
    panel = view.settings_panel
    assert panel.next_question_row.value.text() == "After Animation"
    page_titles = [b.text() for b in panel.stack.findChildren(QRadioButton)]
    assert ("Limited" in page_titles and "All" in page_titles) == bool(view.question.choices)
    if isinstance(view.exercise, ChoiceExercise):
        row = panel.choice_buttons_row
        assert row is not None and not row.isHidden()
        row.click()
        motion.settle()
        page = panel.stack.currentWidget()
        assert page is not None
        modes = {b.text(): b for b in page.findChildren(QRadioButton)}
        modes["Limited"].click()
        count = page.findChild(FieldComboBox)
        assert count is not None
        count.setCurrentIndex(count.findData(2))
        assert len(view.question.choices) <= 2
        modes["All"].click()
        assert len(view.question.choices) >= 2
        if cls in (ClefBasics, NotationIdentification):
            settings.clef_basics.question_type = "construction"
            settings.notation.question_type = "staff"
            view.next_question()
            assert not view.question.choices and row.isHidden()
            original_signature = view.exercise.settings_signature()
            view.exercise.button_settings().button_mode = "limited"
            assert view.exercise.settings_signature() == original_signature
    view.close()


@pytest.mark.parametrize("cls", [cls for cls in REGISTRY if issubclass(cls, ChoiceExercise)])
def test_limited_choices_keep_every_correct_answer(cls: type[ChoiceExercise]) -> None:
    """
    Check two-part, required and interchangeable answers while sampling distractors.

    Parameters
    ----------
    cls : type of ChoiceExercise
        A standard button exercise.
    """
    settings.clef_basics.question_type = "identification"
    settings.note_names.clefs = {"treble"}
    settings.note_names.ranges = {"treble": (28, 34)}  # every pitch is in octave four
    settings.note_names.require_octave = settings.keyboard.require_octave = True
    settings.keyboard.black_keys = True
    settings.keyboard.low, settings.keyboard.high = settings.KEYBOARD_FULL
    ex = cls()
    cfg = ex.button_settings()
    cfg.button_mode, cfg.button_count = "limited", 2
    rng = random.Random(10)
    for _ in range(80):
        q = ex.generate(rng)
        assert len(q.choices) <= 2 and len(q.octaves or ()) <= 2
        offered = {a + q.joiner + b for a in q.choices for b in q.octaves} if q.octaves else set(q.choices)
        assert {q.answer, *q.required, *q.accept} <= offered
        replay = ex.refresh(q)
        assert replay.answer == q.answer and len(replay.choices) <= 2


def test_saved_button_modes_are_independent_and_resilient() -> None:
    """Load valid and invalid values without mixing preferences between exercises."""
    saved = store()
    saved.setValue("answerButtons/ChordQualities/mode", "all")
    saved.setValue("answerButtons/ChordQualities/count", "broken")
    saved.setValue("answerButtons/KeyboardNotes/mode", "limited")
    saved.setValue("answerButtons/KeyboardNotes/count", 9)
    load_choice_buttons()
    chord, keyboard = ChordQualities(), KeyboardNotes()
    assert isinstance(chord, ChoiceExercise) and isinstance(keyboard, ChoiceExercise)
    assert (chord.button_settings().button_mode, chord.button_settings().button_count) == ("all", 5)
    assert (keyboard.button_settings().button_mode, keyboard.button_settings().button_count) == ("limited", 9)
    assert chord.settings_signature() != chord.practice_signature()
    assert len(chord.generate(random.Random(4)).choices) > 5
