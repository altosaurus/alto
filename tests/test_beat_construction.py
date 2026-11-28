"""Beat Construction generation, input, grading, and export."""

from __future__ import annotations

import random
from dataclasses import replace
from fractions import Fraction
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from alto import settings
from alto.audio import sounds
from alto.exercises.base import Question
from alto.exercises.library import (
    BEAT_METERS,
    BeatConstruction,
    beat_positions,
)
from alto.settings import RHYTHM_DURATIONS
from alto.theory.beat_placement import (
    grade_beat_marks,
    number_beats,
    toggle_beat,
)
from alto.theory.pitch import Note
from alto.ui.anki_exporter import card_fields
from alto.ui.exercise_page import ExercisePage
from alto.ui.meter_staff import BeatPlacementStaff, MeterStaff
from alto.ui.staff import StaffWidget

if TYPE_CHECKING:
    from pathlib import Path

    from PySide6.QtWidgets import QApplication


@pytest.mark.parametrize(
    ("meter", "expected"),
    [
        ((2, 4), {0, 2, 4, 6}),
        ((3, 4), {0, 2, 4, 6, 8, 10}),
        ((4, 4), set(range(0, 16, 2))),
        ((6, 8), {0, 3, 6, 9}),
        ((9, 8), set(range(0, 18, 3))),
        ((12, 8), set(range(0, 24, 3))),
    ],
)
def test_beat_positions_follow_main_pulse(
    meter: tuple[int, int],
    expected: set[int],
) -> None:
    """
    Check the beat boundaries in simple and compound meters.

    Parameters
    ----------
    meter : tuple of int
        A supported time signature.
    expected : set of int
        The eighth-note slots starting a main beat.
    """
    assert beat_positions(meter) == expected


def test_reselecting_beats_preserves_prior_selections() -> None:
    """Keep undo order independent of score order."""
    original = [9, 0, 6, 3]
    removed = toggle_beat(original, slot=0)
    restored = toggle_beat(removed, slot=0)
    expected = beat_positions((6, 8))

    assert number_beats(restored, slots_per_bar=6) == {0: 1, 3: 2, 6: 1, 9: 2}
    assert grade_beat_marks(removed, expected=expected) == (False, "3 6 9")
    assert grade_beat_marks(restored, expected=expected) == (True, "0 3 6 9")
    assert original == [9, 0, 6, 3]
    assert removed == [9, 6, 3]
    assert restored == [9, 6, 3, 0]


def test_generated_rhythm_has_rests_and_spans_two_bars() -> None:
    """Mix notes and rests and hold across a beat in every meter."""
    exercise = BeatConstruction()
    rng = random.Random(3)
    seen = set()
    for _ in range(60):
        question = exercise.generate(rng)
        seen.add(question.answer)
        numerator, denominator = BEAT_METERS[question.answer]
        capacity = numerator * RHYTHM_DURATIONS["whole"] / denominator
        assert not question.choices
        assert any(value.endswith("-rest") for value in question.rhythm)
        assert any(not value.endswith("-rest") for value in question.rhythm)
        offset = 0.0
        first_value_in_bar_two = ""
        for value in question.rhythm:
            if offset == capacity:
                first_value_in_bar_two = value
            offset += settings.beat_note(value)[2]
        assert offset == 2 * capacity
        assert first_value_in_bar_two.removesuffix("-rest") == (
            "half" if denominator == 4 else "dotted-half"
        )
    assert seen == set(BEAT_METERS)


@pytest.mark.parametrize(("seed", "count"), [(7, 3), (5, 2)])
@pytest.mark.parametrize("note_type", ["eighth", "sixteenth"])
def test_tuplets_share_exact_beats_in_notation_and_playback(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    seed: int,
    count: int,
    note_type: str,
) -> None:
    """
    Engrave full tuplet groups, align their markers, and time every tap.

    Parameters
    ----------
    app : QApplication
        Application for the interactive score.
    monkeypatch : pytest.MonkeyPatch
        Capture the playback timing and painted brackets.
    seed : int
        Selects a simple or compound meter.
    count : int
        Expected tuplet number for the meter.
    note_type : str
        Eighths fill a beat in one group. Sixteenths take two groups.
    """
    settings.beat_tuplets["beatConstruction"] = True
    settings.beat_note_types["beatConstruction"] = {note_type}
    exercise = BeatConstruction()
    assert "A bracket marked 2" in exercise.instructions()
    view = ExercisePage(exercise, rng=random.Random(seed))
    view.show()
    app.processEvents()
    q = view.question
    assert q is not None and exercise.settings_signature() != ""
    assert Question.from_dict(q.to_dict()).item_key() == q.item_key()
    score = view.question_view.beat_placement
    kind = "triplet" if count == 3 else "duplet"
    assert kind in score.accessibleDescription()
    bracket = Mock(wraps=score._draw_tuplet)
    monkeypatch.setattr(score, "_draw_tuplet", bracket)
    assert not score.grab().isNull()
    assert bracket.call_count > 0
    assert all(
        call.kwargs["number"] == len(call.kwargs["heads"]) == count
        for call in bracket.call_args_list
    )
    top, bottom = score.meter
    assert len(score._measures) == 2
    for bar, measure in enumerate(score._measures):
        assert sum(
            settings.beat_note(v)[2]
            for v in q.rhythm[measure[0].onset : measure[-1].onset + 1]
        ) == Fraction(16 * top, bottom)
        for slot in range(score.slots_per_bar):
            if slot * 2 % score._beat_length == 0:
                symbol = next(s for s in measure if s.offset == slot * 2)
                assert score.position(
                    bar * score.slots_per_bar + slot,
                ).x() == score._measure_geometry(bar).x(symbol.space)
    play = Mock()
    monkeypatch.setattr(sounds, "play_rhythm", play)
    view.feedback.playback.play_rhythm(q.rhythm, quarter_ms=601)
    end = Fraction(0)
    ms = 0
    for token, duration in zip(q.rhythm, play.call_args.args[0], strict=True):
        value, tuplet, length = settings.beat_note(token)
        assert value.removesuffix("-rest") == note_type
        assert tuplet in (0, count)
        end += 601 * length / 4
        ms += duration
        assert ms == round(end)
    view.close()


def test_tuplet_and_dotted_rests_keep_their_written_durations(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Keep a rest under its tuplet bracket and time a dotted rest.

    Parameters
    ----------
    app : QApplication
        Application for drawing the exercise.
    monkeypatch : pytest.MonkeyPatch
        Capture the bracket and timed playback.
    """
    view = ExercisePage(BeatConstruction(), rng=random.Random(1))
    score = view.question_view.beat_placement
    rhythm = (
        "triplet-eighth",
        "triplet-eighth-rest",
        "triplet-eighth",
        "half",
        "dotted-quarter-rest",
        "dotted-quarter",
    )
    score.reset(rhythm, meter=(3, 4))
    bracket = Mock(wraps=score._draw_tuplet)
    monkeypatch.setattr(score, "_draw_tuplet", bracket)
    assert not score.grab().isNull()
    bracket.assert_called_once()
    assert len(bracket.call_args.kwargs["heads"]) == 3
    assert "Dotted quarter rest" in score.accessibleDescription()
    playback = Mock()
    monkeypatch.setattr(sounds, "play_rhythm", playback)
    view.feedback.playback.play_rhythm(rhythm, quarter_ms=600)
    assert playback.call_args.args[0] == (200, 200, 200, 1200, 900, 900)
    assert playback.call_args.kwargs["levels"] == (1, 0, 1, 1, 0, 1)
    view.close()


def test_staffless_notes_use_staff_spacing(app: QApplication) -> None:
    """
    Compare mixed note and rest advances with engraved staff notes.

    Parameters
    ----------
    app : QApplication
        Qt application for measuring the notation.
    """
    rhythm = MeterStaff()
    rhythm.show_score(
        ("eighth", "eighth", "quarter-rest", "half") + ("eighth",) * 8,
    )
    rhythm.resize(rhythm.sizeHint())
    bar = rhythm._measure_geometry(0)
    measure = rhythm._measures[0]
    centers = [bar.x(symbol.space) for symbol in measure]
    staff = StaffWidget(lesson_layout=True, gap=10)
    for index, symbol in enumerate(measure[:-1]):
        staff.show_notes(
            [[Note.parse("E4")]] * 2,
            value=symbol.value.removesuffix("-rest"),
        )
        first, second = staff.lesson_systems(800)[0].centers
        assert centers[index + 1] - centers[index] == pytest.approx(
            second - first,
        )
    assert bar.width < rhythm._measure_geometry(1).width


def test_beat_slots_follow_the_engraved_notes(app: QApplication) -> None:
    """
    Align blanks with noteheads and subdivide held notes after wrapping.

    Parameters
    ----------
    app : QApplication
        Qt event loop for the score's layout.
    """
    score = BeatPlacementStaff()
    score.reset(
        ("eighth", "eighth", "quarter-rest", "half") + ("eighth",) * 8,
        meter=(4, 4),
    )
    score.show()
    for width, bars_per_row in ((score.sizeHint().width(), 2), (230, 1)):
        score.resize(width, score.height())
        app.processEvents()
        assert score._bars_per_row == bars_per_row
        for bar_index, measure in enumerate(score._measures):
            bar = score._measure_geometry(bar_index)
            for symbol in measure:
                slot = bar_index * 8 + int(symbol.offset / 2)
                assert score.position(slot).x() == bar.x(symbol.space)
        half = score._measures[0][-1]
        bar = score._measure_geometry(0)
        assert score.position(6).x() == bar.x(half.space + half.advance / 2)


def test_placement_accepts_mouse_and_keyboard_after_wrapping(
    app: QApplication,
) -> None:
    """
    Mark a position within a held note in the second, wrapped measure.

    Parameters
    ----------
    app : QApplication
        Qt event loop used by the score.
    """
    score = BeatPlacementStaff()
    score.reset(("dotted-quarter",) * 4 + ("dotted-half",) * 2, meter=(12, 8))
    score.resize(320, score.height())
    score.show()
    app.processEvents()
    assert score._bars_per_row == 1
    QTest.mouseClick(
        score,
        Qt.MouseButton.RightButton,
        pos=score.position(15).toPoint(),
    )
    assert not score.marks
    QTest.keyClick(score, Qt.Key.Key_A)
    QTest.mouseClick(
        score,
        Qt.MouseButton.LeftButton,
        pos=score.position(15).toPoint(),
    )
    assert score.marks == [15]
    QTest.keyClick(score, Qt.Key.Key_Up)
    QTest.keyClick(score, Qt.Key.Key_Space)
    assert score.marks == [15, 3]
    QTest.keyClick(score, Qt.Key.Key_Right)
    QTest.keyClick(score, Qt.Key.Key_Left)
    QTest.keyClick(score, Qt.Key.Key_Down)
    QTest.keyClick(score, Qt.Key.Key_Space)
    assert score.beat_numbers() == {3: 1}
    for slot in (21, 18, 0):
        QTest.mouseClick(
            score,
            Qt.MouseButton.LeftButton,
            pos=score.position(slot).toPoint(),
        )
    assert score.beat_numbers() == {0: 1, 3: 2, 18: 1, 21: 2}
    assert "Beat 1" in score.accessibleName()
    score.undo()
    assert score.beat_numbers() == {3: 1, 18: 1, 21: 2}
    score.undo()
    assert score.beat_numbers() == {3: 1, 21: 1}
    score.undo()
    assert score.marks == [3]
    score.undo()
    assert not score.marks
    score.close()


def test_view_rejects_extra_marks_and_grades_a_correct_set(
    app: QApplication,
) -> None:
    """
    Require exactly the beat starts, with no extra subdivision marks.

    Parameters
    ----------
    app : QApplication
        Qt event loop used by the exercise.
    """
    view = ExercisePage(BeatConstruction(), rng=random.Random(19))
    view.show()
    app.processEvents()
    question = view.question
    assert question is not None
    score = view.question_view.beat_placement
    assert score._signature_visible
    assert len(score._measures) == 2
    controls = view.control_area.answers.placement
    assert controls.answer_button.parentWidget() is controls
    assert not controls.answer_button.isEnabled()
    assert (
        not view.control_area.answers.buttons
        and view.control_area.answers.placement.place_button.isHidden()
    )
    for slot in sorted(beat_positions(BEAT_METERS[question.answer]) | {1}):
        QTest.mouseClick(
            score,
            Qt.MouseButton.LeftButton,
            pos=score.position(slot).toPoint(),
        )
    view.control_area.answers.placement.answer_button.click()
    assert view.session.missed and score.feedback is False
    assert not score.grab().isNull()
    assert not view.control_area.answers.placement.answer_button.isEnabled()
    view.next_question()
    question = view.question
    assert question is not None
    assert not score.marks
    for slot in sorted(beat_positions(BEAT_METERS[question.answer])):
        QTest.mouseClick(
            score,
            Qt.MouseButton.LeftButton,
            pos=score.position(slot).toPoint(),
        )
    view.control_area.answers.placement.undo_button.click()
    last = max(beat_positions(BEAT_METERS[question.answer]))
    assert last not in score.marks
    QTest.mouseClick(
        score,
        Qt.MouseButton.LeftButton,
        pos=score.position(last).toPoint(),
    )
    score.setFocus()
    QTest.keyClick(score, Qt.Key.Key_Return)
    assert view.session.answered and score.feedback is True
    assert not score.isEnabled()
    assert not score.grab().isNull()
    view.close()


def test_anki_shows_unmarked_and_marked_rhythm(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Provide separate images for the prompt and solution.

    Parameters
    ----------
    app : QApplication
        Qt application for rendering images.
    tmp_path : Path
        Directory receiving media.
    """
    exercise = BeatConstruction()
    _, front, answer, _ = card_fields(
        exercise.generate(random.Random(5)),
        folder=tmp_path,
        exercise=exercise,
    )
    assert "Rhythm to mark" in front
    assert "Marked beat positions" in answer
    assert len(list(tmp_path.glob("*.png"))) == 2


@pytest.mark.parametrize(
    ("seed", "answer", "mode", "quarter_ms"),
    [
        (1, "3/4", "After Animation", 600),
        (7, "4/4", "Wait", 600),
        (19, "12/8", "Immediately", 400),
    ],
)
def test_correct_answer_taps_the_written_rhythm(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    seed: int,
    answer: str,
    mode: str,
    quarter_ms: int,
) -> None:
    """
    Verify the written rhythm and the Next Question policy.

    Parameters
    ----------
    app : QApplication
        Qt event loop used by the exercise.
    monkeypatch : pytest.MonkeyPatch
        Captures the playback request and its visual callback.
    seed : int
        Determines the exercise's time signature.
    answer : str
        The seeded question's time signature.
    mode : str
        The exercise's Next Question setting.
    quarter_ms : int
        Expected duration of a quarter note.
    """
    playback = Mock()
    monkeypatch.setattr(sounds, "play_rhythm", playback)
    view = ExercisePage(BeatConstruction(), rng=random.Random(seed))
    view.show()
    app.processEvents()
    assert view.settings_panel is not None
    view.settings_panel.next_question_mode = mode
    assert view.question is not None and view.question.answer == answer
    score = view.question_view.beat_placement
    QTest.mouseClick(
        score,
        Qt.MouseButton.LeftButton,
        pos=score.position(1).toPoint(),
    )
    view.control_area.answers.placement.answer_button.click()
    playback.assert_not_called()
    view.next_question()
    # Restore the seeded question before grading.
    view.controller.rng.seed(seed)
    view.next_question()
    assert view.question is not None and view.question.answer == answer
    strong = beat_positions(BEAT_METERS[answer])
    score.marks = sorted(strong)
    score.changed.emit()
    view.control_area.answers.placement.answer_button.click()
    playback.assert_called_once()
    durations = playback.call_args.args[0]
    levels = playback.call_args.kwargs["levels"]
    step = playback.call_args.kwargs["on_step"]
    rhythm = view.question.rhythm
    quarter = RHYTHM_DURATIONS["quarter"]
    assert durations == tuple(
        round(quarter_ms * settings.beat_note(value)[2] / quarter)
        for value in rhythm
    )
    assert levels == tuple(
        0.0 if value.endswith("-rest") else 1.0 for value in rhythm
    )
    assert not playback.call_args.kwargs.get("force")
    for index, value in enumerate(rhythm):
        step(index)
        audible = mode != "Immediately" and not value.endswith("-rest")
        assert score.playback_column == (index if audible else None)
    if mode == "After Animation":
        assert not view.controller._advance.isActive()
    step(None)
    assert score.playback_column is None
    assert view.control_area.next_button.isVisible() == (mode == "Wait")
    assert view.controller._advance.isActive() == (mode != "Wait")
    view.close()


def test_note_highlights_skip_rests_and_cross_the_barline(
    app: QApplication,
) -> None:
    """
    Follow note durations rather than counting notes and clicks alike.

    Parameters
    ----------
    app : QApplication
        Qt application used by rhythm notation.
    """
    view = ExercisePage(BeatConstruction(), rng=random.Random(1))
    assert view.question is not None
    rhythm = ("quarter", "half", "half", "eighth-rest", "eighth")
    view.controller.question = replace(
        view.question,
        answer="3/4",
        rhythm=rhythm,
    )
    view.show_question(view.controller.question)
    score = view.question_view.beat_placement
    score.marks = sorted(beat_positions(BEAT_METERS["3/4"]))
    score.changed.emit()
    view.control_area.answers.placement.answer_button.click()
    assert view.session.answered
    columns = []
    for index in range(len(rhythm)):
        view.question_view.light_answer_notes(index)
        columns.append(score.playback_column)
    assert columns == [0, 1, 2, None, 4]
    view.question_view.light_answer_notes(None)
    assert score.playback_column is None
    view.close()


def test_muted_rhythm_still_highlights_and_clears_on_exit(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check the real timed feedback path without playing audio.

    Parameters
    ----------
    app : QApplication
        Qt event loop used by the exercise and audio clock.
    monkeypatch : pytest.MonkeyPatch
        Temporarily mute exercise sounds.
    """
    monkeypatch.setattr(sounds, "enabled", False)
    view = ExercisePage(BeatConstruction(), rng=random.Random(19))
    view.show()
    app.processEvents()
    assert view.question is not None
    score = view.question_view.beat_placement
    score.marks = sorted(beat_positions(BEAT_METERS[view.question.answer]))
    score.changed.emit()
    view.control_area.answers.placement.answer_button.click()
    assert score.playback_column == 0
    view.hide()
    assert score.playback_column is None
    assert sounds._sample_step is None
