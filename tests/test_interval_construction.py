"""
Staff interval placement, review rendering, and independent exercise
options.
"""

import random
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from alto import settings
from alto.audio import sounds
from alto.exercises.base import Question
from alto.exercises.library import IntervalConstruction, IntervalNames
from alto.theory.pitch import Interval, Note
from alto.ui import motion
from alto.ui.anki_exporter import card_fields
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.exercise_settings import load_exercise_settings
from alto.ui.exercise_view import ExerciseView
from alto.ui.question_preview import QuestionPreview
from alto.ui.settings_panel import IntervalSettingsPanel
from alto.ui.staff import BOTTOM_LINE


@pytest.mark.parametrize(
    ("display", "direction"),
    [
        ("Harmonic", "ascending"),
        ("Melodic", "ascending"),
        ("Melodic", "descending"),
    ],
)
def test_placement_and_sounding_notes(
    app: QApplication,
    display: str,
    direction: str,
) -> None:
    """
    Submit a correctly spelled endpoint by clicking its staff position
    and follow the sounding pitches.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    display, direction : str
        Interval presentation to exercise.
    """
    cfg = settings.interval_construction
    cfg.clefs, cfg.staff_keys, cfg.note_values = {"alto"}, {-3}, {"quarter"}
    cfg.displays, cfg.directions, cfg.intervals = (
        {display},
        {direction},
        {"M3"},
    )
    cfg.ranges = {"alto": (28, 30)}
    cfg.accidentals = {-2, 2}
    view = ExerciseView(IntervalConstruction(), rng=random.Random(2))
    view.settings_panel.next_question_mode = "Wait"
    view.show()
    app.processEvents()
    q, staff = view.question, view.input_staff
    assert q is not None and q.construct is not None
    first, target = q.staff[0][0], q.construct
    assert (
        first.transpose(
            Interval.parse("M3"),
            descending=direction == "descending",
        )
        == target
    )
    assert q.prompt == (
        "Place a major third "
        f"{('below' if direction == 'descending' else 'above')}"
        " the given note."
    )
    assert staff.isVisible() and (staff.clef, staff.key, staff.value) == (
        "alto",
        -3,
        "quarter",
    )
    assert staff.columns == (
        [[first]] if display == "Harmonic" else [[first], []]
    )
    view._cycle_accidental()
    view.accidental_buttons[target.accidental].click()
    y = (
        staff.staff_bottoms()["alto"]
        - (target.diatonic - BOTTOM_LINE["alto"]) * staff.GAP / 2
    )
    point = QPoint(staff.width() // 2, round(y))
    QTest.mouseMove(staff, point)
    with patch.object(sounds, "_play_sequence") as play:
        QTest.mouseClick(staff, Qt.MouseButton.LeftButton, pos=point)
        assert (
            view.answered
            and view.correct == 1
            and view.next_button.isVisible()
        )
        assert staff.columns == q.staff
        steps = play.call_args.kwargs
        assert [pitches for pitches, _ in steps["steps"]] == [
            [note.midi for note in col] for col in q.staff
        ]
        for i in range(len(q.staff)):
            steps["on_step"](i)
            assert staff.column_colors == {i: QColor(CORRECT_ANSWER_COLOR)}
        steps["on_step"](None)
        assert not staff.column_colors


@pytest.mark.parametrize("mode", ["interval", "quality"])
def test_partial_prompt_accepts_all_selected_endpoints(mode: str) -> None:
    """
    Check the whole set of accepted pitches against the enabled sizes,
    spellings, direction, and range.

    Parameters
    ----------
    mode : str
        Ask only for the number or only for the quality.
    """
    cfg = settings.interval_construction
    cfg.clefs, cfg.staff_keys, cfg.displays = {"treble"}, {0}, {"Melodic"}
    cfg.ranges, cfg.intervals = {"treble": (28, 32)}, {"m3", "M3", "M2"}
    cfg.quality_mode, cfg.directions = mode, {"ascending", "descending"}
    ex, rng = IntervalConstruction(), random.Random(71)
    pitches = [
        Note.from_diatonic(i, accidental=a)
        for i in range(27, 34)
        for a in range(-2, 3)
    ]
    saw_alternative = False
    for _ in range(60):
        q = ex.generate(rng)
        assert Question.from_dict(q.to_dict()) == q
        first, target = q.staff[0][0], q.staff[1][0]
        descending = first.diatonic > target.diatonic
        low, high = (target, first) if descending else (first, target)
        exemplar = Interval.between(low, high=high)
        expected = set()
        for name in cfg.intervals:
            iv = Interval.parse(name)
            end = first.transpose(iv, descending=descending)
            matches = (
                iv.number == exemplar.number
                if mode == "interval"
                else iv.quality == exemplar.quality
            )
            if (
                matches
                and end.accidental in cfg.accidentals
                and 28 <= end.diatonic <= 32
            ):
                expected.add(end)
        assert {n for n in pitches if q.check_placed(n)} == expected
        saw_alternative |= len(expected) > 1
    assert saw_alternative


def test_settings_retries_and_export(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Persist construction options separately, retain the starting note on
    a miss, and conceal the solution on export.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        Destination for the two exported music images.
    """
    cfg = settings.interval_construction
    cfg.clefs, cfg.ranges, cfg.intervals = (
        {"treble"},
        {"treble": (28, 30)},
        {"M3", "m3"},
    )
    view = ExerciseView(IntervalConstruction(), rng=random.Random(4))
    panel = view.settings_panel
    assert (
        isinstance(panel, IntervalSettingsPanel)
        and panel.buttons_row.isHidden()
    )
    original = IntervalNames().settings_signature()
    panel.quality_modes["interval"].click()
    cfg.quality_mode = "combined"
    load_exercise_settings()
    assert (
        cfg.quality_mode == "interval"
        and IntervalNames().settings_signature() == original
    )
    view.next_question()
    q = view.question
    assert q is not None and q.construct is not None and q.accept
    first, target = q.staff[0][0], q.construct
    for wrong, hint in (
        (first, "staff position"),
        (Note.from_diatonic(target.diatonic, accidental=2), "accidental"),
    ):
        view._place(wrong)
        assert (
            hint in view.place_status.text()
            and view.input_staff.columns[0][0] == first
        )
        motion.settle()
        assert not view.input_staff.locked and view.input_staff.columns == [
            [first],
        ]
    alternate = next(
        Note.from_diatonic(target.diatonic, accidental=a)
        for a in (-1, 0, 1)
        if str(Note.from_diatonic(target.diatonic, accidental=a)) in q.accept
    )
    view._place(alternate)
    assert view.answered and view.input_staff.columns == [[first, alternate]]
    preview = QuestionPreview(view.exercise.name, question=q)
    assert all(
        name in preview._answer_text() for name in (q.answer, *q.accept)
    )
    prompt, front, back, _ = card_fields(
        q,
        folder=tmp_path,
        exercise=view.exercise,
    )
    assert (
        prompt == q.prompt
        and "<img" in front
        and "<img" in back
        and len(list(tmp_path.glob("*.png"))) == 2
    )
    assert all(name in back for name in (q.answer, *q.accept))
