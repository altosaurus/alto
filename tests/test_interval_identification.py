"""Staff interval selection, presentation, grading, and settings persistence."""

import random

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QRadioButton, QToolButton

from alto import settings
from alto.exercises.library import IntervalNames
from alto.theory.pitch import Interval
from alto.ui.dropdown import FieldComboBox
from alto.ui.exercise_view import ExerciseView
from alto.ui.settings_panel import IntervalSettingsPanel, load_intervals
from alto.ui.store import store


@pytest.mark.parametrize("display", settings.INTERVAL_DISPLAYS)
def test_each_written_interval_matches_the_display_and_answer(display: str) -> None:
    """
    Read back every question from its written notes in both answer formats.

    Parameters
    ----------
    display : str
        The selected staff presentation.
    """
    cfg = settings.intervals
    cfg.clefs = {"alto"}
    cfg.ranges = {"alto": (22, 36)}
    cfg.staff_keys = {-4}
    cfg.displays = {display}
    exercise = IntervalNames()
    rng = random.Random(22)
    for name, iv in settings.WRITTEN_INTERVALS.items():
        cfg.intervals = {name}
        for quality in (True, False):
            cfg.quality = quality
            q = exercise.generate(rng)
            assert (q.key, q.clef) == (-4, "alto")
            assert [len(chord) for chord in q.staff] == ([2] if display == "Harmonic" else [1, 1])
            notes = [note for chord in q.staff for note in chord]
            low, high = notes
            assert 22 <= low.diatonic <= high.diatonic <= 36
            assert Interval.between(low, high=high) == iv
            assert q.choices == [q.answer] == [name if quality else str(iv.number)]
            assert q.check(name) == quality and q.check(str(iv.number)) != quality


def test_only_possible_intervals_are_asked() -> None:
    """Check empty selections, nonoverlapping ranges, and distinct number-only answer choices."""
    cfg = settings.intervals
    cfg.clefs = {"bass", "treble"}
    cfg.ranges = {"treble": (28, 30), "bass": (21, 21)}
    cfg.intervals = {"M3", "m3", "M2", "P5"}
    cfg.quality = False
    exercise = IntervalNames()
    rng = random.Random(0)
    questions = [exercise.generate(rng) for _ in range(45)]
    assert {q.clef for q in questions} == {"treble"}
    assert {q.answer for q in questions} == {"2", "3"}
    assert all(sorted(q.choices) == ["2", "3"] for q in questions)
    cfg.intervals = {"P5"}
    q = exercise.generate(rng)
    assert "Range" in q.prompt and not q.choices
    cfg.intervals.clear()
    assert "Select an interval" in exercise.generate(rng).prompt


def test_settings_menu_and_saved_interval_question(app: QApplication) -> None:
    """
    Edit the exercise settings through the exercise, reload them, and reset the edited range.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    exercise = IntervalNames()
    view = ExerciseView(exercise, rng=random.Random(4))
    view.show()
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    assert view.gear is not None
    view.gear.click()
    QTest.qWait(300)
    rows = (
        panel.clefs_row,
        panel.range_row,
        panel.staff_key_row,
        panel.display_row,
        panel.quality_row,
        panel.intervals_row,
        panel.buttons_row,
    )
    assert [r.title.text() for r in rows] == [
        f"<b>{s}</b>" for s in ("Clefs", "Range", "Staff Key", "Display", "Quality", "Intervals", "Buttons")
    ]
    assert [r.y() for r in rows] == sorted(r.y() for r in rows)
    question = view.question
    original = exercise.settings_signature()
    panel.clefs_row.click()
    QTest.qWait(300)
    assert view.question is question
    panel.boxes["treble"].click()
    assert view.question.clef == "bass" and not panel.boxes["bass"].isEnabled()
    page = panel.stack.currentWidget()
    assert page is not None
    next(b for b in page.findChildren(QToolButton) if "Back" in b.text()).click()
    QTest.qWait(300)
    panel.range_row.click()
    QTest.qWait(300)
    editor = panel.range_editors["bass"]
    editor.low_up.click()
    panel.staff_keys.boxes[-2].click()
    panel.staff_keys.boxes[0].click()
    assert set(panel.display.boxes) == {"Melodic", "Harmonic"}
    panel.display.boxes["Harmonic"].click()
    mixed = [exercise.generate(random.Random(seed)) for seed in range(30)]
    assert {len(q.staff) for q in mixed} == {1, 2}
    panel.display.boxes["Melodic"].click()
    panel.quality_row.click()
    previous_selection = panel.interval_list.selected()
    panel.select_all.click()
    assert panel.interval_list.selected() == set(settings.WRITTEN_INTERVALS)
    panel.select_all.click()
    assert panel.interval_list.selected() == previous_selection
    panel.slider.move_endpoint("low", delta=1)
    assert panel.interval_list.selected() == {name for name, iv in settings.WRITTEN_INTERVALS.items() if 3 <= iv.number <= 8}
    panel.interval_list.boxes["M9"].click()
    cfg = settings.intervals
    assert not cfg.quality and cfg.ranges["bass"] == (editor.low, editor.high)
    assert cfg.displays == {"Harmonic"} and cfg.staff_keys == {-2} and "M9" in cfg.intervals
    assert view.question.key == -2 and view.question.answer.isdigit()
    assert panel.display_row.value.text() == "Harmonic"
    customized = exercise.settings_signature()
    assert customized != original
    assert settings.note_names.clefs == {"treble", "bass"} and not settings.note_names.ranges
    cfg.__init__()
    load_intervals()
    assert exercise.settings_signature() == customized
    panel._reset_ranges()
    load_intervals()
    assert not cfg.ranges
    view.close()


def test_saved_empty_selection_and_invalid_range() -> None:
    """Keep an intentional empty interval checklist and ignore malformed or out-of-bounds ranges."""
    saved = store()
    saved.setValue("intervals/buttonCount", "invalid")
    saved.setValue("intervals/intervals", "")
    saved.setValue("intervals/range/bass", "7,60")
    saved.setValue("intervals/range/treble", "typo")
    load_intervals()
    assert not settings.intervals.intervals and not settings.intervals.ranges
    assert settings.intervals.button_count == 6


def test_buttons_switch_between_a_limit_and_all_eligible_answers(app: QApplication) -> None:
    """
    Change the answer layout through the submenu and restore the limited count.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.intervals
    cfg.clefs = {"treble"}
    cfg.ranges = {"treble": (28, 35)}
    cfg.intervals = set(settings.WRITTEN_INTERVALS)
    view = ExerciseView(IntervalNames(), rng=random.Random(15))
    view.show()
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel) and view.gear is not None
    view.gear.click()
    QTest.qWait(300)
    original = view.question
    panel.buttons_row.click()
    QTest.qWait(300)
    assert view.question is original and len(view.buttons) == 6
    page = panel.stack.currentWidget()
    assert page is not None
    modes = {b.text(): b for b in page.findChildren(QRadioButton)}
    count = page.findChild(FieldComboBox)
    assert count is not None and count.isVisible() and modes["Limited"].isChecked()
    count.setCurrentIndex(count.findData(3))
    assert len(view.buttons) == 3 and view.question.answer in view.question.choices
    modes["All"].click()
    assert panel.buttons_row.value.text() == "All" and not count.isVisible()
    available = [name for name, iv in settings.WRITTEN_INTERVALS.items() if iv.number <= 8]
    assert [b.text() for b in view.interval_answers.buttons] == available and view.interval_answers.isVisible()
    view.buttons[view.question.choices.index(view.question.answer)].click()
    assert view.answered
    cfg.__init__()
    load_intervals()
    assert (cfg.button_mode, cfg.button_count) == ("all", 3)
    all_signature = view.exercise.settings_signature()
    panel.quality_row.click()
    assert view.question.choices == [str(n) for n in range(1, 9)]
    modes["Limited"].click()
    assert count.isVisible() and count.currentData() == 3 and len(view.buttons) == 3
    assert view.exercise.settings_signature() != all_signature
    view.close()
