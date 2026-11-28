"""
Keyboard interval generation, stored questions, simultaneous highlights,
and answer playback.
"""

from __future__ import annotations

import random
from dataclasses import replace

import pytest
from PySide6.QtCore import (
    QPoint,
    Qt,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QScrollArea,
    QWidget,
)

from alto import settings
from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import KeyboardIntervals
from alto.learning.stats import describe
from alto.theory.pitch import (
    Interval,
    Note,
)
from alto.ui import exercise_feedback as exercise_view
from alto.ui.exercise_page import ExercisePage
from alto.ui.exercise_settings import (
    load_keyboard_intervals,
    save_keyboard_intervals,
)
from alto.ui.home import EXERCISE_ICONS
from alto.ui.keyboard import KeyboardWidget
from alto.ui.question_preview import QuestionPreview
from alto.ui.settings_panel import KeyboardIntervalSettingsPanel
from alto.ui.store import store
from alto.ui.style import app_style


def test_keyboard_intervals_cover_distances_with_one_unambiguous_answer() -> (
    None
):
    """
    Cover every distance, including black keys and the octave, without
    enharmonically duplicate answers.
    """
    exercise = KeyboardIntervals()
    rng = random.Random(71)
    answers = {
        1: "m2",
        2: "M2",
        3: "m3",
        4: "M3",
        5: "P4",
        6: "A4 / d5",
        7: "P5",
        8: "m6",
        9: "M6",
        10: "m7",
        11: "M7",
        12: "P8",
    }
    distances = set()
    black_keys = set()
    for _ in range(600):
        question = exercise.generate(rng)
        lower, higher = question.keyboard_notes
        distance = higher.midi - lower.midi
        distances.add(distance)
        black_keys.update(
            note.midi % 12
            for note in question.keyboard_notes
            if note.accidental
        )
        assert question.answer == answers[distance]
        assert question.check(question.answer)
        assert len(question.choices) == len(set(question.choices)) == 6
        assert set(question.choices) <= set(answers.values())
        assert all(
            not question.check(choice)
            for choice in question.choices
            if choice != question.answer
        )
        assert question.keyboard_range == (48, 72)
        assert 48 <= lower.midi < higher.midi <= 72
        assert not question.staff and question.keyboard is None
    assert distances == set(range(1, 13))
    assert black_keys == {1, 3, 6, 8, 10}
    assert (
        exercise.__class__ in REGISTRY
        and "KeyboardIntervals" in EXERCISE_ICONS
    )


def test_both_keys_survive_storage_and_identify_the_review_question() -> None:
    """
    Preserve both pitches in backups and distinguish questions that
    differ only in one endpoint.
    """
    question = KeyboardIntervals().generate(random.Random(5))
    restored = Question.from_dict(question.to_dict())
    assert restored == question and restored.item_key() == question.item_key()
    changed = replace(
        question,
        keyboard_notes=[question.keyboard_notes[0], Note.parse("C6")],
    )
    assert changed.item_key() != question.item_key()
    assert "Keys " in describe(restored)
    assert all(
        f"{note.name}{note.octave}" in describe(restored)
        for note in question.keyboard_notes
    )
    legacy = {
        "prompt": "",
        "choices": ["C"],
        "answer": "C",
        "keyboard": {"octave": 4, "letter": 0, "accidental": 0},
    }
    single = Question.from_dict(legacy)
    assert single.keyboard == Note.parse("C4") and single.keyboard_notes == []
    assert single.item_key() == "678072d45a46fe34e567"


def test_keyboard_paints_both_white_and_black_highlights_and_clears_them(
    app: QApplication,
) -> None:
    """
    Paint both keys together and remove the extra highlight when showing
    a single-key question.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    keyboard = KeyboardWidget()
    app.processEvents()
    keyboard.show_keys([60, 61], span=(60, 72))
    together = keyboard.grab().toImage()
    assert keyboard.highlight == 60 and keyboard.additional_highlights == {61}
    keyboard.show_key(60)
    assert together != keyboard.grab().toImage()
    assert not keyboard.additional_highlights
    keyboard.show_key(61)
    assert together != keyboard.grab().toImage()
    keyboard.show_keys([])
    assert keyboard.highlight is None and not keyboard.additional_highlights


def test_exercise_and_saved_preview_show_and_play_both_notes(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Answer through the real buttons and preserve the two highlights in
    the database preview.

    Parameters
    ----------
    app : QApplication
        The shared application.
    monkeypatch : pytest.MonkeyPatch
        Replaces audio playback to capture both notes.
    """
    played: list[list[list[Note]]] = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(
        exercise_view.sounds,
        "play_notes",
        lambda notes, **_: played.append(notes),
    )
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(9))
    view.show()
    app.processEvents()
    question = view.question
    assert question is not None
    expected = {note.midi for note in question.keyboard_notes}
    assert (
        view.question_view.keyboard.isVisible()
        and view.question_view.staff is None
    )
    assert {
        view.question_view.keyboard.highlight,
    } | view.question_view.keyboard.additional_highlights == expected
    preview = QuestionPreview(
        view.controller.exercise.name,
        question=Question.from_dict(question.to_dict()),
    )
    keyboard = preview.findChild(KeyboardWidget)
    assert keyboard is not None
    assert {keyboard.highlight} | keyboard.additional_highlights == expected
    right = next(
        button
        for button in view.control_area.answers.buttons
        if button.text() == question.answer
    )
    right.click()
    assert view.session.answered and played == [[question.keyboard_notes]]
    view.controller._advance.stop()
    view.close()
    preview.close()


def test_range_and_interval_options_control_generation_and() -> None:
    """
    Restrict both pitches and answer choices, and separate reviews
    whenever either option changes.
    """
    cfg = settings.keyboard_intervals
    cfg.low, cfg.high, cfg.intervals = 60, 67, {3, 4, 7}
    exercise = KeyboardIntervals()
    before = exercise.settings_signature()
    questions = [exercise.generate(random.Random(seed)) for seed in range(120)]
    assert {q.answer for q in questions} == {"m3", "M3", "P5"}
    for question in questions:
        assert question.keyboard_range == (60, 67)
        assert all(60 <= note.midi <= 67 for note in question.keyboard_notes)
        assert set(question.choices) == {"m3", "M3", "P5"}
        assert (
            question.keyboard_notes[1].midi - question.keyboard_notes[0].midi
            in cfg.intervals
        )
    cfg.intervals = {7}
    assert exercise.settings_signature() != before
    before = exercise.settings_signature()
    cfg.high = 72
    assert exercise.settings_signature() != before
    assert exercise.generate(random.Random(0)).choices == ["P5"]


def test_single_key_and_impossible_interval_settings_always() -> None:
    """
    Recover safely from unusable imported settings, including a single
    key at either piano endpoint.
    """
    cfg = settings.keyboard_intervals
    for low, high in ((60, 60), (108, 108), (-100, -100), (72, 60)):
        cfg.low, cfg.high, cfg.intervals = low, high, {0, 12, 99}
        question = KeyboardIntervals().generate(random.Random(6))
        lower, higher = question.keyboard_notes
        assert 21 <= lower.midi < higher.midi <= 108
        assert question.keyboard_range == cfg.bounds()
        assert higher.midi - lower.midi in cfg.active_intervals()


def test_options_persist_and_ignore_invalid_saved_values() -> None:
    """
    Reload range and interval choices without changing the other
    keyboard exercise.
    """
    cfg = settings.keyboard_intervals
    original = settings.KeyboardSettings(**settings.keyboard.__dict__)
    cfg.low, cfg.high, cfg.intervals = 55, 78, {3, 7, 12}
    save_keyboard_intervals(cfg)
    cfg.low, cfg.high, cfg.intervals = 60, 61, {1}
    load_keyboard_intervals()
    assert (cfg.low, cfg.high, cfg.intervals) == (55, 78, {3, 7, 12})
    assert settings.keyboard == original
    store().setValue("keyboardIntervals/low", "invalid")
    store().setValue("keyboardIntervals/high", 999)
    store().setValue("keyboardIntervals/intervals", "bad,0,88,²,3")
    load_keyboard_intervals()
    assert cfg.bounds() == settings.KEYBOARD_DEFAULT and cfg.intervals == {3}
    store().setValue("keyboardIntervals/low", 60)
    store().setValue("keyboardIntervals/high", 61)
    store().setValue("keyboardIntervals/intervals", "12")
    load_keyboard_intervals()
    assert cfg.bounds() == (60, 61) and cfg.intervals == {1}


def test_settings_panel_applies_live_edits_and_allows_clearing_intervals(
    app: QApplication,
) -> None:
    """
    Apply range, checkbox, and reset controls through the exercise's
    actual settings panel.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(6))
    panel = view.settings_panel
    assert isinstance(panel, KeyboardIntervalSettingsPanel)
    assert view.toolbar.gear is not None
    panel.span.dragged.emit(60, 64)
    app.processEvents()
    assert panel.cfg.intervals == {1, 2, 3, 4}
    assert panel.low_label.text() == "C4" and panel.high_label.text() == "E4"
    assert view.question is not None and view.question.keyboard_range == (
        60,
        64,
    )
    assert all(
        not panel.interval_page.boxes[n].isEnabled() for n in range(5, 13)
    )
    for distance in (1, 2, 4):
        panel.interval_page.boxes[distance].click()
    assert panel.cfg.intervals == {3}
    assert panel.interval_page.boxes[3].isEnabled()
    assert (
        view.question is not None
        and view.question.answer == "m3"
        and view.question.choices == ["m3"]
    )
    panel._set_range(60, 60)
    assert panel.cfg.bounds() == (60, 61) and panel.cfg.intervals == {1}
    assert (
        not panel.arrows["low"][1].isEnabled()
        and not panel.arrows["high"][0].isEnabled()
    )
    panel.entire.click()
    assert (
        panel.cfg.bounds() == settings.KEYBOARD_FULL
        and panel.interval_page.boxes[12].isEnabled()
    )
    panel.default.click()
    assert panel.cfg.bounds() == settings.KEYBOARD_DEFAULT
    assert (
        int(store().value("keyboardIntervals/low"))
        == settings.KEYBOARD_DEFAULT[0]
    )
    view.close()


def test_generation_and_review_signature_follow_range_and() -> None:
    """
    Keep generated notes and answer choices inside the selected options,
    with a new review signature for each edit.
    """
    cfg = settings.keyboard_intervals
    exercise = KeyboardIntervals()
    initial = exercise.settings_signature()
    cfg.low, cfg.high = 55, 70
    narrowed = exercise.settings_signature()
    assert narrowed != initial
    cfg.intervals = {3, 7}
    assert exercise.settings_signature() != narrowed
    rng = random.Random(42)
    found = set()
    for _ in range(150):
        question = exercise.generate(rng)
        lower, upper = question.keyboard_notes
        gap = upper.midi - lower.midi
        found.add(gap)
        assert 55 <= lower.midi < upper.midi <= 70
        assert gap in {3, 7}
        assert set(question.choices) == {"m3", "P5"}
        assert question.answer == {3: "m3", 7: "P5"}[gap]
    assert found == {3, 7}
    cfg.low, cfg.high = 60, 61
    cfg.intervals = {12}
    question = exercise.generate(rng)
    assert question.answer == "m2" and question.choices == ["m2"]
    assert [note.midi for note in question.keyboard_notes] == [60, 61]


# Qt signal callbacks change the slider bounds between assertions.
# noinspection PyUnreachableCode
def test_interval_options_list_every_distance_that_fits_the_selected_range(
    app: QApplication,
) -> None:
    """
    Show only intervals within the selected range, including compound
    intervals through the full piano span.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    panel = KeyboardIntervalSettingsPanel(settings.keyboard_intervals)
    app.processEvents()
    visible = {
        distance
        for distance, box in panel.interval_page.boxes.items()
        if not box.isHidden()
    }
    assert visible == set(range(1, 25))
    assert panel.interval_page.boxes[24].text() == "P15"
    assert panel.interval_page.boxes[12].text() == "P8"
    assert panel.interval_page.boxes[13].text() == "m9"
    headings = [
        label.text() for label in panel.interval_page.findChildren(QLabel)
    ]
    assert headings == ["Simple intervals", "Compound intervals"]
    assert all(
        panel.interval_page.boxes[distance].text()
        == settings.keyboard_interval_name(distance)
        for distance in range(1, len(settings.KEYBOARD_INTERVAL_NAMES) + 1)
    )
    parent = panel.interval_range.parentWidget()
    assert parent is not None
    layout = parent.layout()
    assert layout is not None
    assert (
        layout.indexOf(panel.interval_range)
        == layout.indexOf(panel.select_all) + 1
    )
    panel.span.dragged.emit(60, 67)
    assert panel.interval_slider.maximum == 7
    visible = {
        distance
        for distance, box in panel.interval_page.boxes.items()
        if not box.isHidden()
    }
    assert visible == set(range(1, 8))
    panel.span.dragged.emit(60, 74)
    assert panel.interval_slider.maximum == 14
    panel.entire.click()
    assert panel.interval_slider.maximum == 87
    visible = {
        distance
        for distance, box in panel.interval_page.boxes.items()
        if not box.isHidden()
    }
    assert visible == set(range(1, 88))
    assert "m52" in panel.interval_page.boxes[87].text()
    panel.interval_page.boxes[87].click()
    assert 87 in panel.cfg.intervals
    panel.close()


def test_compound_intervals_generate_and_reload_through_entire() -> None:
    """
    Preserve selected compound intervals in storage and generate their
    correct distances and names.
    """
    expected = {
        13: "m9",
        14: "M9",
        18: "A11 / d12",
        24: "P15",
        36: "P22",
        87: "m52",
    }
    cfg = settings.keyboard_intervals
    cfg.low, cfg.high = settings.KEYBOARD_FULL
    cfg.intervals = set(expected)
    save_keyboard_intervals(cfg)
    cfg.intervals = {1}
    load_keyboard_intervals()
    assert cfg.intervals == set(expected)
    rng = random.Random(87)
    found = set()
    for _ in range(240):
        question = KeyboardIntervals().generate(rng)
        lower, higher = question.keyboard_notes
        gap = higher.midi - lower.midi
        found.add(gap)
        assert 21 <= lower.midi < higher.midi <= 108
        assert question.answer == expected[gap]
        assert set(question.choices) == set(expected.values())
        assert Question.from_dict(question.to_dict()) == question
    assert found == set(expected)
    for distance in range(1, 88):
        name = settings.keyboard_interval_name(distance).split(" / ")[0]
        interval = Interval(int(name[1:]), quality=name[0])
        assert interval.semitones == distance


def test_select_all_toggle_restores_and_saves_the_previous_selection(
    app: QApplication,
) -> None:
    """
    Restore the custom selection after temporarily selecting all
    intervals, with one update per toggle.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    settings.keyboard_intervals.intervals = {3, 7, 12}
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(8))
    panel = view.settings_panel
    assert isinstance(panel, KeyboardIntervalSettingsPanel)
    panel._set_range(60, 74)
    changes = []
    panel.changed.connect(lambda: changes.append(1))
    panel.select_all.click()
    assert panel.cfg.intervals == set(range(1, 15))
    assert panel.select_all.isOn() and len(changes) == 1
    assert all(panel.interval_page.boxes[n].isChecked() for n in range(1, 15))
    assert not panel.interval_page.boxes[15].isChecked()
    panel.select_all.click()
    app.processEvents()
    assert panel.cfg.intervals == {3, 7, 12}
    assert not panel.select_all.isOn() and len(changes) == 2
    assert panel.interval_page.selected() == {3, 7, 12}
    assert view.question is not None and view.question.answer in {
        "m3",
        "P5",
        "P8",
    }
    settings.keyboard_intervals.intervals = {1}
    load_keyboard_intervals()
    assert settings.keyboard_intervals.intervals == {3, 7, 12}
    panel.interval_page.boxes[4].click()
    panel.select_all.click()
    panel.select_all.click()
    assert panel.cfg.intervals == {3, 4, 7, 12}
    assert not any(
        "Choose the intervals to practice" in label.text()
        for label in panel.findChildren(QLabel)
    )
    view.close()


def test_select_all_restoration_follows_range_changes_and_manual_edits(
    app: QApplication,
) -> None:
    """
    Keep the bulk selection complete as the range changes and restore
    only intervals that still fit.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    panel = KeyboardIntervalSettingsPanel(
        settings.KeyboardIntervalSettings(intervals={3, 7, 12}),
    )
    app.processEvents()
    panel.select_all.click()
    panel.entire.click()
    assert panel.cfg.intervals == set(range(1, 88)) and panel.select_all.isOn()
    panel._set_range(60, 67)
    assert panel.cfg.intervals == set(range(1, 8))
    panel.select_all.click()
    assert panel.cfg.intervals == {3, 7} and not panel.select_all.isOn()
    panel.select_all.click()
    panel.interval_page.boxes[5].click()
    assert not panel.select_all.isOn()
    custom = set(panel.cfg.intervals)
    panel.select_all.click()
    panel.select_all.click()
    assert panel.cfg.intervals == custom
    panel.close()


def test_select_all_can_restore_an_initial_all_or_empty_selection(
    app: QApplication,
) -> None:
    """
    Turn the override off even when its saved selection already contains
    every interval or contains none.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    for selected in (set(), {1, 2, 3, 4}):
        panel = KeyboardIntervalSettingsPanel(
            settings.KeyboardIntervalSettings(
                low=60,
                high=64,
                intervals=selected,
            ),
        )
        app.processEvents()
        assert not panel.select_all.isOn()
        panel.select_all.click()
        panel.select_all.click()
        assert panel.cfg.intervals == selected and not panel.select_all.isOn()
        panel.close()


def test_interval_range_selects_intervals_without_changing_keyboard_bounds(
    app: QApplication,
) -> None:
    """
    Select simple and compound intervals with the slider and buttons
    while preserving the keyboard range.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(4))
    panel = view.settings_panel
    assert isinstance(panel, KeyboardIntervalSettingsPanel)
    app.processEvents()
    original = panel.cfg.bounds()
    panel.interval_arrows["low"][1].click()
    panel.interval_arrows["low"][1].click()
    assert panel.cfg.intervals == set(range(3, 13))
    assert (
        panel.interval_low_label.currentText() == "m3"
        and panel.interval_high_label.currentText() == "P8"
    )
    panel.interval_slider.move_endpoint("high", delta=12)
    assert panel.cfg.intervals == set(range(3, 25))
    assert panel.interval_high_label.currentText() == "P15"
    assert (
        view.question is not None and view.question.keyboard_range == original
    )
    assert (
        panel.cfg.bounds() == original
        and (panel.span.lo, panel.span.hi) == original
    )
    panel.select_all.click()
    panel.select_all.click()
    assert panel.cfg.intervals == set(range(3, 25))
    panel.interval_slider.move_endpoint("high", delta=-99)
    assert panel.cfg.intervals == {3}
    assert not panel.interval_arrows["high"][0].isEnabled()
    assert not panel.interval_arrows["low"][1].isEnabled()
    panel.interval_page.boxes[3].click()
    assert not panel.interval_slider.active
    assert (
        panel.interval_low_label.currentIndex()
        == panel.interval_high_label.currentIndex()
        == -1
    )
    panel.interval_arrows["high"][1].click()
    assert panel.cfg.intervals == {2}
    assert panel.cfg.bounds() == original
    view.close()


def open_interval_options(
    app: QApplication,
    *,
    seed: int,
) -> tuple[ExercisePage, KeyboardIntervalSettingsPanel]:
    """
    Open the interval options at the exercise pane's actual width.

    Parameters
    ----------
    app : QApplication
        The shared application.
    seed : int
        The exercise random seed. Keyword-only.

    Returns
    -------
    tuple of (ExercisePage, KeyboardIntervalSettingsPanel)
        The visible exercise and its interval settings panel.
    """
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(seed))
    view.setStyleSheet(app_style(view.palette()))
    view.resize(1000, 750)
    view.show()
    panel = view.settings_panel
    assert (
        isinstance(panel, KeyboardIntervalSettingsPanel)
        and view.toolbar.gear is not None
    )
    view.toolbar.gear.setChecked(True)
    # noinspection PyProtectedMember
    view.settings_pane.animation.setCurrentTime(
        view.settings_pane.animation.duration(),
    )
    panel.stack.setCurrentIndex(2)
    app.processEvents()
    return view, panel


def test_interval_endpoint_controls_fit_the_actual_settings_pane(
    app: QApplication,
) -> None:
    """
    Keep both endpoint rows fully visible at the exercise pane's fixed
    width, including long compound notation.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    cfg = settings.keyboard_intervals
    cfg.low, cfg.high = settings.KEYBOARD_FULL
    cfg.intervals = {78, 87}
    view, panel = open_interval_options(app, seed=5)
    scroll = panel.stack.currentWidget().findChild(QScrollArea)
    assert scroll is not None
    viewport = scroll.viewport()
    controls: list[QWidget] = [
        panel.interval_low_label,
        panel.interval_high_label,
    ]
    controls.extend(
        button for pair in panel.interval_arrows.values() for button in pair
    )
    for control in controls:
        assert control.isVisible()
        assert viewport.rect().contains(control.mapTo(viewport, QPoint(0, 0)))
        assert viewport.rect().contains(
            control.mapTo(
                viewport,
                QPoint(control.width() - 1, control.height() - 1),
            ),
        )
    for label in (panel.interval_low_label, panel.interval_high_label):
        assert label.width() >= label.fontMetrics().horizontalAdvance(
            label.currentText(),
        )
    assert panel.interval_low_label.y() < panel.interval_high_label.y()
    view.close()


def test_clicking_endpoint_notation_opens_scrollable_interval_dropdowns(
    app: QApplication,
) -> None:
    """
    Choose both endpoints through real scrollable popups and synchronize
    the slider without changing piano keys.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    cfg = settings.keyboard_intervals
    cfg.low, cfg.high = settings.KEYBOARD_FULL
    view, panel = open_interval_options(app, seed=11)
    for picker, index in (
        (panel.interval_low_label, 12),
        (panel.interval_high_label, 86),
    ):
        QTest.mouseClick(
            picker,
            Qt.MouseButton.LeftButton,
            pos=picker.rect().center(),
        )
        app.processEvents()
        popup = picker.view()
        assert popup.isVisible() and picker.count() == 87
        assert popup.verticalScrollBar().maximum() > 0
        assert popup.verticalScrollBar().isVisible()
        item = picker.model().index(index, 0)
        popup.scrollTo(item)
        app.processEvents()
        QTest.mouseMove(popup.viewport(), popup.visualRect(item).center())
        QTest.mouseClick(
            popup.viewport(),
            Qt.MouseButton.LeftButton,
            pos=popup.visualRect(item).center(),
        )
        app.processEvents()
    assert panel.cfg.intervals == set(range(13, 88))
    assert (
        panel.interval_low_label.currentText() == "m9"
        and panel.interval_high_label.currentText() == "m52"
    )
    assert (panel.interval_slider.low, panel.interval_slider.high) == (13, 87)
    assert panel.cfg.bounds() == settings.KEYBOARD_FULL
    panel.interval_low_label.setCurrentIndex(1)
    panel.interval_low_label.activated.emit(1)
    assert min(panel.cfg.intervals) == 2 and panel.interval_slider.low == 2
    panel._set_range(60, 67)
    assert (
        panel.interval_low_label.count()
        == panel.interval_high_label.count()
        == 7
    )
    panel.interval_high_label.setCurrentIndex(0)
    panel.interval_high_label.activated.emit(0)
    assert panel.cfg.intervals == {1}
    assert (
        panel.interval_low_label.currentText()
        == panel.interval_high_label.currentText()
        == "m2"
    )
    view.close()


def test_all_interval_buttons_option_saved_and_keeps_answer(
    app: QApplication,
) -> None:
    """
    Switch between six choices and every selected interval without
    shuffling the full answer bank.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(21))
    panel = view.settings_panel
    assert isinstance(panel, KeyboardIntervalSettingsPanel)
    assert len(view.control_area.answers.buttons) == 6
    signature = view.controller.exercise.settings_signature()
    panel.button_modes["all"].click()
    app.processEvents()
    expected = list(settings.KEYBOARD_INTERVAL_NAMES[:12])
    assert (
        panel.cfg.all_interval_buttons
        and view.controller.exercise.settings_signature() != signature
    )
    assert [
        button.text() for button in view.control_area.answers.buttons
    ] == expected
    view.next_question()
    assert [
        button.text() for button in view.control_area.answers.buttons
    ] == expected
    panel.cfg.all_interval_buttons = False
    load_keyboard_intervals()
    assert panel.cfg.all_interval_buttons
    panel.button_modes["limited"].click()
    assert (
        not panel.cfg.all_interval_buttons
        and len(view.control_area.answers.buttons) == 6
    )
    view.close()


def test_full_interval_answer_bank_scrolls_wraps_and_accepts_answers(
    app: QApplication,
) -> None:
    """
    Keep every interval accessible on a small window and allow correct
    answers after scrolling through the bank.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    cfg = settings.keyboard_intervals
    cfg.low, cfg.high = settings.KEYBOARD_FULL
    cfg.intervals = set(range(1, 88))
    cfg.all_interval_buttons = True
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(42))
    view.setStyleSheet(app_style(view.palette()))
    view.resize(600, 650)
    view.show()
    app.processEvents()
    bank = view.control_area.answers.interval_answers
    assert len(view.control_area.answers.buttons) == 87 and [
        button.text() for button in view.control_area.answers.buttons
    ] == list(settings.KEYBOARD_INTERVAL_NAMES)
    assert bank.isVisible() and bank.height() <= 240
    assert bank.verticalScrollBar().maximum() > 0
    view.resize(430, 650)
    app.processEvents()
    assert bank.content.width() <= bank.viewport().width()
    assert bank.horizontalScrollBar().maximum() == 0
    assert view.question is not None
    right = next(
        button
        for button in view.control_area.answers.buttons
        if button.text() == view.question.answer
    )
    bank.ensureWidgetVisible(right)
    app.processEvents()
    assert (
        bank.viewport()
        .rect()
        .contains(right.mapTo(bank.viewport(), right.rect().center()))
    )
    right.click()
    assert view.session.answered
    view.controller._advance.stop()
    panel = view.settings_panel
    assert isinstance(panel, KeyboardIntervalSettingsPanel)
    panel.button_modes["limited"].click()
    app.processEvents()
    assert len(view.control_area.answers.buttons) == 6 and not bank.isVisible()
    view.close()


@pytest.mark.parametrize("count", [1, 4, 6, 9, 20, 87, 0, 999])
def test_limited_mode_uses_the_requested_total_button_count(
    count: int,
) -> None:
    """
    Include the correct answer within the requested number of distinct
    choices and bound invalid counts safely.

    Parameters
    ----------
    count : int
        The requested maximum number of answer buttons.
    """
    cfg = settings.keyboard_intervals
    cfg.low, cfg.high = settings.KEYBOARD_FULL
    cfg.intervals = set(range(1, 88))
    cfg.button_count = count
    exercise = KeyboardIntervals()
    for seed in range(12):
        question = exercise.generate(random.Random(seed))
        assert (
            len(question.choices)
            == len(set(question.choices))
            == max(1, min(87, count))
        )
        assert question.answer in question.choices
    cfg.intervals = {3, 7}
    cfg.button_count = 20
    assert set(exercise.generate(random.Random(1)).choices) == {"m3", "P5"}
    cfg.all_interval_buttons = True
    cfg.button_count = 1
    assert set(exercise.generate(random.Random(1)).choices) == {"m3", "P5"}


def test_button_count_is_editable_saved_and_preserved_across_all_buttons_mode(
    app: QApplication,
) -> None:
    """
    Edit the count through typing and arrows, preserve it when switching
    modes, and reload saved or invalid values.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(6))
    panel = view.settings_panel
    assert isinstance(panel, KeyboardIntervalSettingsPanel)
    assert (
        panel.button_count.text() == "6"
        and len(view.control_area.answers.buttons) == 6
    )
    before = view.controller.exercise.settings_signature()
    panel.button_count.setFocus()
    panel.button_count.selectAll()
    QTest.keyClicks(panel.button_count, "9")
    QTest.keyClick(panel.button_count, Qt.Key.Key_Return)
    app.processEvents()
    assert (
        panel.cfg.button_count == 9
        and len(view.control_area.answers.buttons) == 9
    )
    assert view.controller.exercise.settings_signature() != before
    assert view.control_area.answers.interval_answers.isVisibleTo(view)
    panel.button_count_down.click()
    assert (
        panel.cfg.button_count == 8
        and len(view.control_area.answers.buttons) == 8
    )
    panel.button_modes["all"].click()
    assert (
        not panel.button_count.isEnabled()
        and len(view.control_area.answers.buttons) == 12
    )
    panel.button_modes["limited"].click()
    assert (
        panel.button_count.isEnabled()
        and panel.button_count.text() == "8"
        and len(view.control_area.answers.buttons) == 8
    )
    panel.cfg.button_count = 2
    load_keyboard_intervals()
    assert panel.cfg.answer_button_limit() == 8
    store().setValue("keyboardIntervals/buttonCount", "invalid")
    load_keyboard_intervals()
    assert panel.cfg.answer_button_limit() == 6
    store().setValue("keyboardIntervals/buttonCount", 999)
    load_keyboard_intervals()
    assert panel.cfg.answer_button_limit() == 87
    panel._refresh()
    assert not panel.button_count_up.isEnabled()
    view.close()


@pytest.mark.parametrize("distance", [3, 6, 18, 87])
@pytest.mark.parametrize("number_first", [False, True])
def test_compact_interval_answers_accept_two_clicks(
    app: QApplication,
    distance: int,
    number_first: bool,
) -> None:
    """
    Accept either click order, including both tritone spellings and
    compound numbers.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    distance : int
        The interval distance in half steps.
    number_first : bool
        Whether to select the interval number before its quality.
    """
    cfg = settings.keyboard_intervals
    cfg.low, cfg.high = settings.KEYBOARD_FULL
    cfg.intervals = {distance}
    cfg.compact_buttons = True
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(2))
    assert view.question is not None
    for spelling in view.question.answer.split(" / "):
        view.next_question()
        buttons = {
            button.text(): button
            for button in view.control_area.answers.buttons
        }
        quality, number = buttons[spelling[0]], buttons[spelling[1:]]
        first, second = (
            (number, quality) if number_first else (quality, number)
        )
        first.click()
        assert not view.session.answered
        second.click()
        assert view.session.answered
        view.controller._advance.stop()
    view.close()


def test_compact_mode_is_saved_and_replaces_full_answer_buttons(
    app: QApplication,
) -> None:
    """
    Persist the compact option and restore limited answers when
    selected.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExercisePage(KeyboardIntervals(), rng=random.Random(4))
    panel = view.settings_panel
    assert isinstance(panel, KeyboardIntervalSettingsPanel)
    assert panel.stack.count() == 5
    panel.buttons_row.click()
    panel.stack.setCurrentIndex(3)
    assert panel.button_modes["limited"].isChecked()
    assert all(
        panel.stack.widget(3).isAncestorOf(radio)
        for radio in panel.button_modes.values()
    )
    panel.button_modes["compact"].click()
    assert sum(radio.isChecked() for radio in panel.button_modes.values()) == 1
    assert panel.buttons_row.value.text() == "Compact"
    assert panel.cfg.compact_buttons
    assert view.question is not None and view.question.octaves
    assert (
        not panel.button_count.isEnabled()
        and panel.button_modes["compact"].isChecked()
    )
    panel.cfg.compact_buttons = False
    load_keyboard_intervals()
    assert panel.cfg.compact_buttons
    panel.button_modes["limited"].click()
    assert view.question is not None and not view.question.octaves
    assert len(view.control_area.answers.buttons) == 6
    view.close()


def test_keyboard_interval_name_requires_distinct_keys_in_range() -> None:
    """Reject unisons and intervals wider than the keyboard."""
    for distance in (
        0,
        settings.KEYBOARD_FULL[1] - settings.KEYBOARD_FULL[0] + 1,
    ):
        with pytest.raises(ValueError, match="two distinct piano keys"):
            settings.keyboard_interval_name(distance)
