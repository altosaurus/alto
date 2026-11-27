"""Generation, notation, and scoring for Beat Identification."""

from __future__ import annotations

import json
import random
from fractions import Fraction
from itertools import combinations
from typing import TYPE_CHECKING
from unittest.mock import Mock

import numpy as np
import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QCheckBox, QRadioButton, QScrollArea, QToolButton

from alto import settings
from alto.exercises.base import ChoiceExercise, Exercise, Question
from alto.exercises.library import (
    BEAT_METERS,
    BeatConstruction,
    BeatIdentification,
    beat_meter,
)
from alto.settings import RHYTHM_DURATIONS
from alto.ui import engraving, motion
from alto.ui.anki_exporter import card_fields
from alto.ui.exercise_page import ExercisePage
from alto.ui.exercise_settings import load_exercise_settings
from alto.ui.meter_staff import MeterButton, MeterStaff
from alto.ui.settings_menu import MenuRow, ToggleRow
from alto.ui.settings_panel import settings_panel_for
from alto.ui.style import app_style

if TYPE_CHECKING:
    from pathlib import Path

    from PySide6.QtWidgets import QApplication


@pytest.mark.parametrize("component", ["Time signature", "Beat and meter"])
def test_questions_fill_two_measures_and_survive_storage(
    component: str,
) -> None:
    """
    Check all six answers against the written rhythm in both modes.

    Parameters
    ----------
    component : str
        The selected Rhythm Component.
    """
    settings.beat_rhythm_component = component
    meters = (
        BEAT_METERS
        if component == "Time signature"
        else {
            "Simple duple": (2, 4),
            "Simple triple": (3, 4),
            "Simple quadruple": (4, 4),
            "Compound duple": (6, 8),
            "Compound triple": (9, 8),
            "Compound quadruple": (12, 8),
        }
    )
    exercise = BeatIdentification()
    rng = random.Random(1)
    seen = set()
    keys = set()
    for _ in range(100):
        question = exercise.generate(rng)
        seen.add(question.answer)
        keys.add(question.item_key())
        assert question.choices == list(meters)
        numerator, denominator = meters[question.answer]
        assert beat_meter(question.answer) == (numerator, denominator)
        capacity = numerator * RHYTHM_DURATIONS["whole"] / denominator
        completed = 0
        running = 0.0
        for value in question.rhythm:
            running += RHYTHM_DURATIONS[value]
            assert running <= capacity
            if running == capacity:
                completed += 1
                running = 0.0
        assert (completed, running) == (2, 0.0)
        assert question.rhythm[: 2 if denominator == 4 else 3] == (
            ("eighth",) * (2 if denominator == 4 else 3)
        )
        assert question.check(question.answer)
        assert all(
            not question.check(wrong)
            for wrong in question.choices
            if wrong != question.answer
        )
        restored = Question.from_dict(
            json.loads(json.dumps(question.to_dict())),
        )
        assert restored == question
        assert restored.item_key() == question.item_key()
    assert seen == set(meters)
    assert len(keys) > len(seen)


@pytest.mark.parametrize(
    ("prefix", "component"),
    [
        ("beatConstruction", "Time signature"),
        ("beatIdentification", "Time signature"),
        ("beatIdentification", "Beat and meter"),
    ],
)
def test_note_type_selections_fill_both_measures(
    prefix: str,
    component: str,
) -> None:
    """
    Every nonempty selection produces complete, gradable measures.

    Parameters
    ----------
    prefix : str
        Exercise setting under test.
    component : str
        Identification answer mode.
    """
    exercise = (
        BeatConstruction()
        if prefix == "beatConstruction"
        else BeatIdentification()
    )
    settings.beat_rhythm_component = component
    rng = random.Random(0)
    for size in range(1, len(settings.BEAT_NOTE_TYPES) + 1):
        for selection in combinations(settings.BEAT_NOTE_TYPES, size):
            settings.beat_note_types[prefix] = set(selection)
            q = exercise.generate(rng)
            top, bottom = beat_meter(q.answer)
            bar = top * RHYTHM_DURATIONS["whole"] / bottom
            total = 0.0
            if prefix == "beatConstruction":
                assert any(value.endswith("-rest") for value in q.rhythm)
                assert any(not value.endswith("-rest") for value in q.rhythm)
            for value in q.rhythm:
                assert value.removesuffix("-rest") in selection
                duration = settings.beat_note(value)[2]
                assert total % bar + duration <= bar
                total += duration
            assert total == 2 * bar
            if selection == ("whole",):
                assert (top, bottom) == (4, 4)
                if prefix == "beatIdentification":
                    assert q.rhythm == ("whole", "whole")
                else:
                    assert sorted(q.rhythm) == ["whole", "whole-rest"]
            if prefix == "beatIdentification" and q.answer in ("3/4", "6/8"):
                first = q.rhythm[0]
                assert first in settings.RHYTHM_BEAM_COUNTS
                divisions = int(
                    (4 if bottom == 4 else 6) / RHYTHM_DURATIONS[first],
                )
                assert q.rhythm[:divisions] == (first,) * divisions


def test_note_type_picker_saves_each_exercise(app: QApplication) -> None:
    """
    Edit note types through the gear, then reload both saved selections.

    Parameters
    ----------
    app : QApplication
        Application for the settings panes.
    """
    app.setStyleSheet(app_style(app.palette()))
    for exercise, label in (
        (BeatIdentification(), "Whole note"),
        (BeatConstruction(), "Half note"),
    ):
        view = ExercisePage(exercise, rng=random.Random(7))
        view.show()
        view.toolbar.gear.click()
        panel = view.settings_panel
        assert panel is not None
        row = next(
            r
            for r in panel.findChildren(MenuRow)
            if r.accessibleName() == "Note Type"
        )
        original = view.question
        assert exercise.settings_signature() == ""
        row.click()
        motion.settle()
        page = panel.stack.currentWidget()
        assert page is not None and original is view.question
        boxes = page.findChildren(QCheckBox)
        assert all(not box.icon().isNull() for box in boxes)
        wanted = next(box for box in boxes if box.text() == label)
        wanted.setChecked(True)
        for box in boxes:
            if box is not wanted:
                box.setChecked(False)
        assert exercise.settings_signature() != ""
        assert wanted.isChecked() and not wanted.isEnabled()
        assert view.question is not None
        expected = label.split()[0].lower()
        assert set(view.question.rhythm) == (
            {expected, f"{expected}-rest"}
            if isinstance(exercise, BeatConstruction)
            else {expected}
        )
        assert row.value.text() == "1 selected"
        gaps = []
        for height in (420, 820):
            view.resize(800, height)
            app.processEvents()
            gaps.append(boxes[1].y() - boxes[0].geometry().bottom())
            scroll = page.findChild(QScrollArea)
            assert scroll is not None
            scroll.ensureWidgetVisible(boxes[-1])
            assert (
                scroll.verticalScrollBar().value()
                == scroll.verticalScrollBar().maximum()
            )
        assert gaps[0] == gaps[1] and gaps[0] > 0
        current = view.question
        page.findChildren(QToolButton)[0].click()
        motion.settle()
        assert panel.stack.currentIndex() == 0 and view.question is current
        view.close()
    settings.beat_note_types.clear()
    load_exercise_settings()
    assert settings.beat_note_types == {
        "beatIdentification": {"whole"},
        "beatConstruction": {"half"},
    }


@pytest.mark.parametrize(
    ("value", "beams"),
    [("sixteenth", 2), ("thirty_second", 3)],
)
def test_short_notes_show_beams_and_fit_a_narrow_pane(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    value: str,
    beams: int,
) -> None:
    """
    Draw one group per beat and keep a dense bar readable by scrolling.

    Parameters
    ----------
    app : QApplication
        Application for layout and painting.
    monkeypatch : pytest.MonkeyPatch
        Captures beam counts while rendering.
    value : str
        Short note type selected for the rhythm.
    beams : int
        Expected number of beams on each group.
    """
    settings.beat_note_types["beatIdentification"] = {value}
    settings.beat_rhythm_component = "Beat and meter"
    view = ExercisePage(BeatIdentification(), rng=random.Random(19))
    view.resize(430, 480)
    view.show()
    view.toolbar.gear.click()
    motion.settle()
    app.processEvents()
    score = view.question_view.beat_staff
    draw = Mock(wraps=engraving.draw_beamed_notes)
    monkeypatch.setattr(engraving, "draw_beamed_notes", draw)
    assert not score.grab().isNull()
    assert score.meter == (12, 8)
    assert len(draw.call_args_list) == 8
    assert all(call.kwargs["beams"] == beams for call in draw.call_args_list)
    assert view.question_view.rhythm_scroll.horizontalScrollBar().maximum() > 0
    assert score.width() >= score.minimumSizeHint().width()
    view.close()


def test_tuplet_switch_persists_independently(app: QApplication) -> None:
    """
    Toggle live practice, restore its settings, and reopen both menus.

    Parameters
    ----------
    app : QApplication
        Application for constructing the exercise menus.
    """
    exercise = BeatIdentification()
    view = ExercisePage(exercise, rng=random.Random(5))
    view.show()
    view.toolbar.gear.click()
    panel = view.settings_panel
    assert panel is not None
    switch = next(
        s
        for s in panel.findChildren(ToggleRow)
        if s.accessibleName() == "Tuplets"
    )
    assert not switch.isOn() and exercise.settings_signature() == ""
    original = view.question
    switch.click()
    assert view.question is not None and view.question is not original
    assert settings.beat_tuplets["beatIdentification"]
    assert "three triplet eighths" in exercise.instructions()
    assert exercise.settings_signature() != ""
    settings.beat_tuplets["beatIdentification"] = False
    load_exercise_settings()
    for ex, enabled in ((exercise, True), (BeatConstruction(), False)):
        reopened = settings_panel_for(ex)
        restored = next(
            s
            for s in reopened.findChildren(ToggleRow)
            if s.accessibleName() == "Tuplets"
        )
        assert restored.isOn() == enabled
    switch.click()
    assert exercise.settings_signature() == ""
    assert "three triplet eighths" not in exercise.instructions()
    assert view.question is not None
    assert all(settings.beat_note(v)[1] == 0 for v in view.question.rhythm)
    view.close()


@pytest.mark.parametrize(
    ("kind", "count", "ordinary"),
    [
        ("triplet", 3, 2),
        ("quadruplet", 4, 3),
        ("quintuplet", 5, 4),
        ("sextuplet", 6, 4),
        ("septuplet", 7, 4),
        ("nonuplet", 9, 8),
    ],
)
def test_identification_tuplet_choices(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    count: int,
    ordinary: int,
) -> None:
    """
    Check the study weights, full bars, and spoken group names.

    Parameters
    ----------
    app : QApplication
        Application for engraving the selected group.
    monkeypatch : pytest.MonkeyPatch
        Controls the probability draw on either side of the threshold.
    kind : str
        Tuplet name to generate.
    count : int
        Number of notes under the bracket.
    ordinary : int
        Ordinary eighth notes occupying the same span.
    """
    settings.beat_tuplets["beatIdentification"] = True
    settings.beat_note_types["beatIdentification"] = {"eighth"}
    rng = random.Random(7)
    # Seed 7 chooses 4/4, which can fit every studied group of eighths.
    monkeypatch.setattr(rng, "random", lambda: 0.0067)
    draw = Mock(return_value=[kind])
    monkeypatch.setattr(rng, "choices", draw)
    question = BeatIdentification().generate(rng)
    assert question.answer == "4/4"
    call = draw.call_args
    assert dict(zip(call.args[0], call.kwargs["weights"], strict=True)) == {
        "triplet": 611,
        "quadruplet": 2,
        "quintuplet": 11,
        "sextuplet": 40,
        "septuplet": 5,
        "nonuplet": 2,
    }
    assert settings.beat_note(f"{kind}-eighth") == (
        "eighth",
        count,
        Fraction(2 * ordinary, count),
    )
    staff = MeterStaff()
    staff.show_score(question.rhythm, meter=(4, 4), show_signature=False)
    assert kind in staff.accessibleDescription()
    assert len(staff._measures) == 2
    for measure in staff._measures:
        assert (
            sum(
                settings.beat_note(question.rhythm[s.onset])[2]
                for s in measure
            )
            == 16
        )
        for group in staff._groups(measure):
            if group[0].tuplet:
                assert group[0].tuplet == len(group) == count

    monkeypatch.setattr(rng, "random", lambda: 0.0068)
    ordinary_question = BeatIdentification().generate(rng)
    assert all(settings.beat_note(v)[1] == 0 for v in ordinary_question.rhythm)


def test_hidden_signature_and_wrapping(app: QApplication) -> None:
    """
    Fit two measures without engraving or announcing their signature.

    Parameters
    ----------
    app : QApplication
        Qt application used to lay out and paint the notation.
    """
    score = MeterStaff()
    score.show_score(("eighth",) * 24, meter=(12, 8), show_signature=False)
    score.resize(score.sizeHint())
    score.show()
    app.processEvents()
    assert len(score._measures) == 2
    assert score._bars_per_row == 2
    assert score.accessibleName() == "Written rhythm"
    assert "12/8" not in score.accessibleDescription()
    assert "beamed group" in score.accessibleDescription()
    assert "Measure 2" in score.accessibleDescription()
    assert not score.grab().isNull()
    tall = score.height()
    score.resize(score.width() // 2 + 10, score.height())
    app.processEvents()
    assert score._bars_per_row == 1 and score.height() == 2 * tall
    assert not score.grab().isNull()
    score.show_score(("quarter",) * 8)
    assert score.accessibleName() == "4/4 rhythm"
    assert score._signature_visible


@pytest.mark.parametrize(
    "exercise_type",
    [BeatIdentification, BeatConstruction],
)
def test_nine_eight_stays_centered_after_a_question_change(
    app: QApplication,
    exercise_type: type[Exercise],
) -> None:
    """
    Center the printed rows as a short question gives way to 9/8.

    Parameters
    ----------
    app : QApplication
        Event loop for score and viewport layout.
    exercise_type : type of Exercise
        Beat exercise to open at narrow and wide sizes.
    """
    settings.beat_rhythm_component = "Beat and meter"
    view = ExercisePage(exercise_type(), rng=random.Random(2))
    view.resize(820, 520)
    view.show()
    app.processEvents()
    score = view.question_view.beat_staff
    assert score.meter == (2, 4)
    view.controller.rng.seed(5)
    view.next_question()
    for width, rows in ((820, 1), (360, 2), (820, 1)):
        view.resize(width, 520)
        app.processEvents()
        assert score.meter == (9, 8)
        assert score.height() == rows * score._row_height()
        assert score.minimumHeight() == score.maximumHeight() == score.height()
        assert (
            view.question_view.rhythm_scroll.viewport().height()
            == score.height()
        )

        image = (
            score.grab()
            .toImage()
            .convertToFormat(QImage.Format.Format_Grayscale8)
        )
        pixels = np.frombuffer(image.constBits(), dtype=np.uint8).reshape(
            image.height(),
            image.bytesPerLine(),
        )
        for row in np.vsplit(pixels[:, 8 : image.width() - 8], rows):
            ink = np.flatnonzero((row < 225).any(axis=1))
            top, bottom = ink[0], len(row) - 1 - ink[-1]
            assert abs(top - bottom) <= 3 * image.devicePixelRatio()
    view.close()


def test_exercise_view_scores_the_time_signature(app: QApplication) -> None:
    """
    Show the prompt and exactly two measures alongside standard choices.

    Parameters
    ----------
    app : QApplication
        Qt application used to build and open the exercise.
    """
    exercise = BeatIdentification()
    view = ExercisePage(exercise, rng=random.Random(5))
    view.show()
    app.processEvents()
    question = view.question
    assert question is not None
    prompt = view.question_view.prompt
    assert prompt.parentWidget() is view.question_view
    assert (
        prompt.isVisible() and prompt.text() == "What is the time signature?"
    )
    assert prompt.geometry().bottom() < view.question_view.rhythm_scroll.y()
    assert view.question_view.beat_staff.isVisible()
    assert not view.question_view.beat_staff._signature_visible
    assert len(view.question_view.beat_staff._measures) == 2
    assert view.question_view.staff is None
    assert view.settings_panel is not None
    assert view.settings_panel.choice_buttons_row is not None
    assert {
        button.text() for button in view.control_area.answers.buttons
    } == set(
        question.choices,
    )
    assert all(
        isinstance(button, MeterButton)
        for button in view.control_area.answers.buttons
    )
    assert all(
        button.accessibleName() == button.text()
        for button in view.control_area.answers.buttons
    )
    assert all(
        not button.shortcut().isEmpty()
        for button in view.control_area.answers.buttons
    )
    correct = next(
        button
        for button in view.control_area.answers.buttons
        if button.text() == question.answer
    )
    correct.click()
    assert view.session.answered
    view.close()


def test_rhythm_component_menu_and_review(app: QApplication) -> None:
    """
    Switch components, score a classification, and restore the choice.

    Parameters
    ----------
    app : QApplication
        Application for the settings menu and practice view.
    """
    app.setStyleSheet(app_style(app.palette()))
    exercise = BeatIdentification()
    view = ExercisePage(exercise, rng=random.Random(1))
    view.show()
    view.toolbar.gear.click()
    panel = view.settings_panel
    assert panel is not None
    row = next(
        r
        for r in panel.findChildren(MenuRow)
        if r.accessibleName() == "Rhythm Component"
    )
    original = view.question
    assert original is not None and exercise.settings_signature() == ""
    assert row.value.text() == "Time signature"
    row.click()
    motion.settle()
    page = panel.stack.currentWidget()
    assert page is not None and view.question is original
    default, classify = page.findChildren(QRadioButton)
    assert default.isChecked() and classify.text() == "Beat and meter"
    gaps = []
    for height in (520, 900):
        view.resize(820, height)
        app.processEvents()
        assert default.isVisible() and classify.isVisible()
        gaps.append(classify.y() - default.geometry().bottom())
    assert gaps[0] == gaps[1] and gaps[0] > 0

    classify.click()
    assert row.value.text() == "Beat and meter"
    assert exercise.settings_signature() != ""
    assert exercise.review_question(original, same_settings=False) is None
    question = view.question
    assert (
        question is not None
        and question.prompt == view.question_view.prompt.text()
    )
    assert question.prompt == "What are the beat and meter?"
    top, bottom = beat_meter(question.answer)
    assert view.question_view.beat_staff.meter == (top, bottom)
    assert view.question_view.beat_staff._signature_visible
    assert (
        view.question_view.beat_staff.accessibleName()
        == f"{top}/{bottom} rhythm"
    )
    assert "duple" in exercise.instructions()
    page.findChildren(QToolButton)[0].click()
    motion.settle()
    assert panel.stack.currentIndex() == 0 and view.question is question
    view.toolbar.gear.click()
    motion.settle()
    assert view.control_area.answers.interval_answers.isVisible()
    assert all(
        button.isVisible()
        and not isinstance(button, MeterButton)
        and not button.shortcut().isEmpty()
        for button in view.control_area.answers.buttons
    )
    next(
        b
        for b in view.control_area.answers.buttons
        if b.text() == question.answer
    ).click()
    assert view.session.answered

    settings.beat_rhythm_component = "Time signature"
    load_exercise_settings()
    restored = settings_panel_for(exercise)
    assert any(
        r.accessibleName() == "Rhythm Component"
        and r.value.text() == "Beat and meter"
        for r in restored.findChildren(MenuRow)
    )
    assert exercise.review_question(question, same_settings=True) == question
    assert isinstance(exercise, ChoiceExercise)
    cfg = exercise.button_settings()
    cfg.button_mode, cfg.button_count = "limited", 3
    limited = exercise.generate(random.Random(8))
    assert len(limited.choices) == 3 and limited.answer in limited.choices


@pytest.mark.parametrize("component", ["Time signature", "Beat and meter"])
def test_anki_card_renders_the_question_without_the_answer(
    app: QApplication,
    tmp_path: Path,
    component: str,
) -> None:
    """
    Include the signature on the front only for meter classification.

    Parameters
    ----------
    app : QApplication
        Qt application used by the score renderer.
    tmp_path : Path
        Temporary directory for rendered media.
    component : str
        The answer format to export.
    """
    settings.beat_rhythm_component = component
    exercise = BeatIdentification()
    question = exercise.generate(random.Random(0))
    settings.beat_rhythm_component = "Time signature"
    front, illustration, answer, _ = card_fields(
        question,
        folder=tmp_path,
        exercise=exercise,
    )
    assert question.answer not in front + illustration
    top, bottom = beat_meter(question.answer)
    label = f"{top}/{bottom}" if component == "Beat and meter" else "written"
    assert f"Two measures of {label} rhythm" in illustration
    assert answer == question.answer
    assert len(list(tmp_path.glob("*.png"))) == 1
