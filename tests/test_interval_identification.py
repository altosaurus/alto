"""
Staff interval selection, presentation, grading, and settings
persistence.
"""

import random
from itertools import pairwise
from unittest.mock import patch

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QToolButton,
)

from alto import settings
from alto.audio import sounds
from alto.exercises.base import Question
from alto.exercises.library import IntervalNames
from alto.theory.pitch import QUALITY_NAMES, Interval, key_accidental
from alto.ui import motion
from alto.ui.dropdown import FieldComboBox
from alto.ui.exercise_page import ExercisePage
from alto.ui.exercise_settings import load_intervals
from alto.ui.question_preview import QuestionPreview
from alto.ui.settings_panel import IntervalSettingsPanel
from alto.ui.staff import StaffWidget
from alto.ui.store import store
from alto.ui.style import app_style


@pytest.mark.parametrize("display", settings.INTERVAL_DISPLAYS)
@pytest.mark.parametrize("direction", ["ascending", "descending"])
def test_each_written_interval_matches_the_display_and_answer(
    display: str,
    direction: str,
) -> None:
    """
    Read back every question from its written notes in all three answer
    formats.

    Parameters
    ----------
    display : str
        The selected staff presentation.
    direction : str
        The selected melodic direction.
    """
    cfg = settings.intervals
    cfg.clefs = {"alto"}
    cfg.ranges = {"alto": (22, 36)}
    cfg.staff_keys = {-4}
    cfg.accidentals = set(settings.INTERVAL_ACCIDENTALS)
    cfg.displays = {display}
    cfg.directions = {direction}
    exercise = IntervalNames()
    rng = random.Random(22)
    for name, iv in settings.WRITTEN_INTERVALS.items():
        cfg.intervals = {name}
        labels = {
            "combined": name,
            "interval": str(iv.number),
            "quality": QUALITY_NAMES[iv.quality],
        }
        for mode, label in labels.items():
            cfg.quality_mode = mode
            q = exercise.generate(rng)
            assert (q.key, q.clef) == (-4, "alto")
            assert [len(chord) for chord in q.staff] == (
                [2] if display == "Harmonic" else [1, 1]
            )
            notes = [note for chord in q.staff for note in chord]
            low, high = (
                reversed(notes)
                if display == "Melodic" and direction == "descending"
                else notes
            )
            assert q.explanation.startswith(f"{notes[0]} to {notes[1]}:")
            assert 22 <= low.diatonic <= high.diatonic <= 36
            assert Interval.between(low, high=high) == iv
            assert q.choices == [q.answer] == [label]
            assert all(
                q.check(candidate) == (candidate == label)
                for candidate in labels.values()
            )


def test_only_possible_intervals_are_asked() -> None:
    """
    Check empty selections, nonoverlapping ranges, and distinct
    number-only answer choices.
    """
    cfg = settings.intervals
    cfg.clefs = {"bass", "treble"}
    cfg.ranges = {"treble": (28, 30), "bass": (21, 21)}
    cfg.intervals = {"M3", "m3", "M2", "P5"}
    cfg.quality_mode = "interval"
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
    cfg.clefs = {"bass"}
    assert "Range" in exercise.generate(rng).prompt


@pytest.mark.parametrize(
    ("display", "direction"),
    [
        ("Harmonic", "ascending"),
        ("Melodic", "ascending"),
        ("Melodic", "descending"),
    ],
)
def test_inverted_answers_follow_the_written_spelling(
    display: str,
    direction: str,
) -> None:
    """
    Grade the inversion while keeping the selected interval on the
    staff.

    Parameters
    ----------
    display : str
        Simultaneous or successive notes.
    direction : str
        Order for melodic notes.
    """
    cfg = settings.intervals
    cfg.inversions, cfg.button_mode = True, "all"
    cfg.displays, cfg.directions = {display}, {direction}
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (28, 42)}
    cfg.accidentals = set(settings.INTERVAL_ACCIDENTALS)
    spellings = {
        "M3": "m6",
        "m3": "M6",
        "A4": "d5",
        "d5": "A4",
        "P8": "P1",
        "M10": "m6",
        "P15": "P1",
    }
    cfg.intervals = set(spellings)
    exercise = IntervalNames()
    rng = random.Random(4)
    for mode in ("combined", "interval", "quality"):
        cfg.quality_mode = mode
        seen = set()
        for _ in range(90):
            q = exercise.generate(rng)
            low, high = sorted(
                (note for chord in q.staff for note in chord),
                key=lambda note: note.diatonic,
            )
            written = Interval.between(low, high=high).short
            seen.add(written)
            inverse = spellings[written]
            expected = {
                "combined": inverse,
                "interval": inverse[1:],
                "quality": QUALITY_NAMES[inverse[0]],
            }[mode]
            assert q.check(expected) and (
                "invert" in q.prompt or "inversion" in q.prompt
            )
            assert q.explanation.endswith(
                f"The inversion of {written} is {inverse}.",
            )
            assert (
                len(q.choices) == len(set(q.choices)) and expected in q.choices
            )
        assert seen == cfg.intervals


def test_inversions_switch_and_saved_reviews(app: QApplication) -> None:
    """
    Toggle the setting from the gear, answer the new question, and
    restore the original review pool.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.intervals
    cfg.intervals = {"M3", "P5", "A4"}
    cfg.button_count = 2
    view = ExercisePage(IntervalNames(), rng=random.Random(3))
    view.setStyleSheet(app_style(view.palette()))
    view.show()
    panel = view.settings_panel
    assert (
        isinstance(panel, IntervalSettingsPanel)
        and view.toolbar.gear is not None
    )
    view.toolbar.gear.click()
    view.settings_pane.animation.setCurrentTime(
        view.settings_pane.animation.duration(),
    )
    row = panel.inversions_row
    assert not row.isOn()
    for width, height in ((900, 480), (1300, 900)):
        view.resize(width, height)
        app.processEvents()
        assert (
            row.isVisible()
            and row.switch.isVisibleTo(panel)
            and row.width() >= row.minimumSizeHint().width()
        )
    original = view.controller.exercise.settings_signature()
    assert "inversions" not in original
    row.click()
    assert (
        cfg.inversions
        and view.controller.exercise.settings_signature() != original
    )
    q = view.question
    assert (
        q is not None
        and len(q.choices) == 2
        and set(q.choices) <= {"m6", "P4", "d5"}
    )
    assert view.question_view.prompt.text() == q.prompt
    view.control_area.answers.buttons[q.choices.index(q.answer)].click()
    assert view.session.answered
    cfg.inversions = False
    load_intervals()
    assert cfg.inversions and Question.from_dict(q.to_dict()).check(q.answer)
    row.click()
    assert (
        not cfg.inversions
        and view.controller.exercise.settings_signature() == original
    )
    assert set(view.question.choices) <= cfg.intervals
    view.close()


@pytest.mark.parametrize("inversions", [False, True])
@pytest.mark.parametrize(
    ("display", "gap_ms"),
    [("Melodic", 500), ("Harmonic", 450)],
)
def test_interval_playback_spacing(
    app: QApplication,
    display: str,
    gap_ms: int,
    inversions: bool,
) -> None:
    """
    Check note onsets for the correct answer and the saved question's
    Play button.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    display : str
        The selected interval presentation.
    gap_ms : int
        Expected spacing between successive staff columns.
    inversions : bool
        Whether a correct answer reveals and plays the inversion.
    """
    settings.intervals.inversions = inversions
    settings.intervals.intervals = {"M3"}
    settings.intervals.displays = {display}
    settings.intervals.directions = {"descending"}
    view = ExercisePage(IntervalNames())
    q = view.question
    assert q is not None
    feedback = q.staff
    if inversions:
        high = max(
            (note for column in q.staff for note in column),
            key=lambda note: note.midi,
        )
        raised = high.transpose(Interval.parse("m6"))
        feedback = (
            [[high, raised]] if display == "Harmonic" else [[raised], [high]]
        )
    assert view.question_view.staff.columns == q.staff
    preview = QuestionPreview(
        IntervalNames.name,
        question=Question.from_dict(q.to_dict()),
    )
    with patch.object(sounds, "_play_sequence") as play:
        next(
            button
            for button in view.control_area.answers.buttons
            if button.text() == q.answer
        ).click()
        on_step = play.call_args.kwargs["on_step"]
        assert (
            not view.question_view.staff.column_colors
            and not view.controller._advance.isActive()
        )
        for index, notes in enumerate(feedback):
            on_step(index)
            assert (
                view.question_view.staff.column_colors
                == {index: QColor("#2e7d32")}
                and view.question_view.staff.columns[index] == notes
            )
            assert (
                view.question_view.staff.note_color is None
                and not view.controller._advance.isActive()
            )
        on_step(None)
        assert (
            not view.question_view.staff.column_colors
            and view.controller._advance.isActive()
        )
        next(
            button
            for button in preview.findChildren(QPushButton)
            if button.text() == "Play"
        ).click()
    assert play.call_count == 2
    for call, columns in zip(
        play.call_args_list,
        (feedback, q.staff),
        strict=True,
    ):
        assert call.kwargs["gap_ms"] == gap_ms
        assert [midis for midis, _ in call.kwargs["steps"]] == [
            [note.midi for note in column] for column in columns
        ]
    view.close()
    preview.close()


def test_new_interval_question_stops_previous_highlight(
    app: QApplication,
) -> None:
    """
    End active interval playback when the learner changes the exercise
    settings.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExercisePage(IntervalNames())
    q = view.question
    assert q is not None
    with patch.object(sounds, "_play_sequence") as play:
        next(
            button
            for button in view.control_area.answers.buttons
            if button.text() == q.answer
        ).click()
        play.call_args.kwargs["on_step"](0)
        assert view.question_view.staff.column_colors == {0: QColor("#2e7d32")}
        panel = view.settings_panel
        assert isinstance(panel, IntervalSettingsPanel)
        panel.quality_modes["interval"].click()
    assert (
        view.question is not q and not view.question_view.staff.column_colors
    )
    assert (
        not view.controller._advance.isActive() and not view.session.answered
    )
    view.close()


def test_display_choices_stay_together_as_the_exercise_grows(
    app: QApplication,
) -> None:
    """
    Open Display Mode and verify its rows stay at the top of the pane
    after resizing.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExercisePage(IntervalNames())
    view.setStyleSheet(app_style(view.palette()))
    view.resize(900, 480)
    view.show()
    panel = view.settings_panel
    assert (
        isinstance(panel, IntervalSettingsPanel)
        and view.toolbar.gear is not None
    )
    view.toolbar.gear.click()
    view.settings_pane.animation.setCurrentTime(
        view.settings_pane.animation.duration(),
    )
    panel.display_row.click()
    assert panel.stack._slide is not None
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    scroll = panel.display.parentWidget()
    assert scroll is not None
    melodic, harmonic = (
        panel.display.boxes[name] for name in ("Melodic", "Harmonic")
    )
    assert (
        harmonic.isChecked()
        and not melodic.isChecked()
        and panel.direction_choices.isHidden()
    )
    melodic.click()
    assert panel.display_row.value.text() == "Harmonic, Melodic"
    for width, height in ((900, 480), (1300, 900), (900, 480)):
        view.resize(width, height)
        app.processEvents()
        assert melodic.isVisible() and harmonic.isVisible()
        assert harmonic.mapTo(scroll, harmonic.rect().topLeft()).y() == 0
        spacing = panel.display.layout().spacing()
        direction = panel.direction_choices
        assert melodic.y() - harmonic.y() - harmonic.height() == spacing
        assert direction.y() - melodic.y() - melodic.height() == spacing

    # A longer list in the same panel must still scroll to its final
    # choice.
    page = panel.stack.currentWidget()
    assert page is not None
    next(
        button
        for button in page.findChildren(QToolButton)
        if "Back" in button.text()
    ).click()
    assert panel.stack._slide is not None
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    panel.intervals_row.click()
    assert panel.stack._slide is not None
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    # lay out the page that slid in, so its scroll bar knows how far the
    # list goes
    app.processEvents()
    page = panel.stack.currentWidget()
    assert page is not None
    area = page.findChild(QScrollArea)
    assert area is not None and area.verticalScrollBar().maximum() > 0
    boxes = panel.interval_list.boxes
    assert set(boxes) == set(settings.WRITTEN_INTERVALS)
    columns = [boxes[name].x() for name in ("A2", "M2", "m2", "d2")]
    assert columns == sorted(set(columns)) and len(columns) == 4
    for name, iv in settings.WRITTEN_INTERVALS.items():
        box = boxes[name]
        assert box.y() == boxes[f"A{iv.number}"].y()
        assert (
            box.x()
            == columns[{"A": 0, "P": 1, "M": 1, "m": 2, "d": 3}[iv.quality]]
        )
        assert box.width() >= box.minimumSizeHint().width()
    assert area.horizontalScrollBar().maximum() == 0
    last = boxes["d15"]
    area.ensureWidgetVisible(last)
    assert (
        area.viewport()
        .rect()
        .contains(last.mapTo(area.viewport(), last.rect().center()))
    )


@pytest.mark.parametrize("sign", settings.INTERVAL_ACCIDENTALS)
def test_written_accidentals_on_both_notes(sign: int) -> None:
    """
    Draw only the selected marking, taking the staff signature into
    account.

    Parameters
    ----------
    sign : int
        A written accidental, or zero for an unmarked note.
    """
    cfg = settings.intervals
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (31, 38)}  # F4 through F5
    cfg.staff_keys = {0, 1}
    cfg.intervals, cfg.accidentals = {"P8"}, {sign}
    exercise, rng = IntervalNames(), random.Random(5)
    keys = set()
    for _ in range(20):
        q = exercise.generate(rng)
        assert q.answer == "P8"
        keys.add(q.key)
        for note in q.staff[0]:
            implied = key_accidental(note.letter, count=q.key)
            if sign == 0:
                assert note.accidental == implied
            else:
                assert note.accidental == sign and note.accidental != implied
    assert keys == ({0} if sign == 1 else {0, 1})


def test_accidental_picker_persistence_and_impossible_interval(
    app: QApplication,
) -> None:
    """
    Toggle markings in the submenu and recover when no selected spelling
    fits.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.intervals
    cfg.clefs, cfg.ranges = {"treble"}, {"treble": (28, 30)}  # C4 through E4
    cfg.intervals, cfg.button_mode = {"m3", "M3"}, "all"
    view = ExercisePage(IntervalNames())
    view.setStyleSheet(app_style(view.palette()))
    view.show()
    view.toolbar.gear.click()
    view.settings_pane.animation.setCurrentTime(
        view.settings_pane.animation.duration(),
    )
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    panel.accidentals_row.click()
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    boxes = panel.accidental_list.boxes
    assert [box.text() for box in boxes.values()] == ["♮", "♭", "♯", "𝄫", "𝄪"]
    for sign, name in settings.INTERVAL_ACCIDENTALS.items():
        assert boxes[sign].accessibleName() == boxes[sign].toolTip() == name
    for width, height in ((900, 480), (1300, 900)):
        view.resize(width, height)
        app.processEvents()
        assert (
            boxes[0].y()
            < boxes[-1].y()
            == boxes[1].y()
            < boxes[-2].y()
            == boxes[2].y()
        )
        assert (
            boxes[0].x()
            == boxes[-1].x()
            == boxes[-2].x()
            < boxes[1].x()
            == boxes[2].x()
        )
        for box in boxes.values():
            assert box.font().pointSizeF() == 22
            assert box.size().expandedTo(box.minimumSizeHint()) == box.size()
    assert panel.accidental_list.selected() == {-1, 0, 1}
    boxes[-1].click()
    boxes[1].click()
    assert not boxes[0].isEnabled() and view.question.choices == ["M3"]
    panel.interval_list.boxes["M3"].click()
    assert not view.question.choices and "Accidentals" in view.question.prompt
    boxes[-2].click()
    boxes[-1].click()
    assert view.question.answer == "m3" and view.question.choices == ["m3"]
    assert panel.accidentals_row.value.text() == "♮ ♭ 𝄫"
    cfg.accidentals.clear()
    load_intervals()
    assert (
        cfg.accidentals == {0, -1, -2}
        and "accidentals" in view.controller.exercise.settings_signature()
    )
    page = panel.stack.currentWidget()
    next(
        b for b in page.findChildren(QToolButton) if "Back" in b.text()
    ).click()
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    assert panel.stack.currentIndex() == 0
    view.close()


def test_inline_melodic_direction_and_review_history(
    app: QApplication,
) -> None:
    """
    Choose a direction on Display Mode and retain it while practicing
    harmonic intervals.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExercisePage(IntervalNames())
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    panel.display_row.click()
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    display_page = panel.stack.currentWidget()
    assert display_page is not None
    ascending = panel.direction_choices.boxes["ascending"]
    descending = panel.direction_choices.boxes["descending"]
    panel.display.boxes["Melodic"].click()
    panel.display.boxes["Harmonic"].click()
    assert (
        ascending.isChecked()
        and not ascending.isEnabled()
        and view.controller.exercise.settings_signature() == ""
    )
    descending.click()
    mixed = view.controller.exercise.settings_signature()
    assert ascending.isChecked() and descending.isChecked() and mixed
    load_intervals()
    assert settings.intervals.directions == {"ascending", "descending"}
    rng = random.Random(8)
    questions = [view.controller.exercise.generate(rng) for _ in range(20)]
    assert {
        q.staff[0][0].diatonic < q.staff[1][0].diatonic for q in questions
    } == {False, True}
    ascending.click()
    assert (
        not ascending.isChecked()
        and descending.isChecked()
        and not descending.isEnabled()
    )
    descending_history = view.controller.exercise.settings_signature()
    assert (
        '"motion": "descending"' in descending_history
        and descending_history != mixed
    )
    assert panel.stack.currentWidget() is display_page
    panel.display.boxes["Harmonic"].click()
    panel.display.boxes["Melodic"].click()
    assert not descending.isVisibleTo(display_page)
    harmonic_history = view.controller.exercise.settings_signature()
    settings.intervals.directions = {"ascending"}
    assert view.controller.exercise.settings_signature() == harmonic_history
    load_intervals()
    assert settings.intervals.directions == {"descending"}
    panel.display.boxes["Melodic"].click()
    assert descending.isVisibleTo(display_page) and descending.isChecked()
    view.close()


def test_settings_menu_and_saved_interval_question(app: QApplication) -> None:
    """
    Edit the exercise settings through the exercise, reload them, and
    reset the edited range.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    exercise = IntervalNames()
    view = ExercisePage(exercise, rng=random.Random(4))
    view.show()
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    assert view.toolbar.gear is not None
    view.toolbar.gear.click()
    motion.settle()
    rows = (
        panel.clefs_row,
        panel.range_row,
        panel.staff_key_row,
        panel.display_row,
        panel.quality_row,
        panel.intervals_row,
        panel.accidentals_row,
        panel.values_row,
        panel.buttons_row,
    )
    assert [r.title.text() for r in rows] == [
        f"<b>{s}</b>"
        for s in (
            "Clefs",
            "Range",
            "Staff Key",
            "Display Mode",
            "Quality",
            "Intervals",
            "Accidentals",
            "Note Value",
            "Buttons",
        )
    ]
    assert [r.y() for r in rows] == sorted(r.y() for r in rows)
    question = view.question
    original = exercise.settings_signature()
    panel.clefs_row.click()
    motion.settle()
    assert view.question is question
    panel.boxes["treble"].click()
    assert view.question.clef == "bass" and not panel.boxes["bass"].isEnabled()
    page = panel.stack.currentWidget()
    assert page is not None
    next(
        b for b in page.findChildren(QToolButton) if "Back" in b.text()
    ).click()
    motion.settle()
    panel.range_row.click()
    motion.settle()
    editor = panel.range_editors["bass"]
    editor.low_up.click()
    panel.staff_keys.boxes[-2].click()
    panel.staff_keys.boxes[0].click()
    assert set(panel.display.boxes) == {"Melodic", "Harmonic"}
    panel.display.boxes["Melodic"].click()
    mixed = [exercise.generate(random.Random(seed)) for seed in range(30)]
    assert {len(q.staff) for q in mixed} == {1, 2}
    panel.display.boxes["Melodic"].click()
    panel.quality_modes["interval"].click()
    assert "P1" not in panel.interval_list.boxes
    panel.slider.move_endpoint("low", delta=-1)
    assert panel.slider.low == 2
    previous_selection = panel.interval_list.selected()
    panel.select_all.click()
    assert panel.interval_list.selected() == set(settings.WRITTEN_INTERVALS)
    panel.select_all.click()
    assert panel.interval_list.selected() == previous_selection
    panel.slider.move_endpoint("low", delta=1)
    assert panel.interval_list.selected() == {
        name
        for name, iv in settings.WRITTEN_INTERVALS.items()
        if 3 <= iv.number <= 8
    }
    panel.interval_list.boxes["M9"].click()
    cfg = settings.intervals
    assert cfg.quality_mode == "interval" and cfg.ranges["bass"] == (
        editor.low,
        editor.high,
    )
    assert (
        cfg.displays == {"Harmonic"}
        and cfg.staff_keys == {-2}
        and "M9" in cfg.intervals
    )
    assert view.question.key == -2 and view.question.answer.isdigit()
    assert panel.display_row.value.text() == "Harmonic"
    customized = exercise.settings_signature()
    assert customized != original
    assert (
        settings.note_names.clefs == {"treble", "bass"}
        and not settings.note_names.ranges
    )
    cfg.__init__()
    load_intervals()
    assert exercise.settings_signature() == customized
    panel._reset_ranges()
    load_intervals()
    assert not cfg.ranges
    view.close()


def test_quality_submenu_and_saved_switch(app: QApplication) -> None:
    """
    Restore old Quality switch settings and grade quality-only answers
    from the submenu.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    saved = store()
    for value, mode in (("true", "combined"), ("false", "interval")):
        saved.setValue("intervals/quality", value)
        load_intervals()
        assert settings.intervals.quality_mode == mode
        assert f'"quality": {value}' in IntervalNames().settings_signature()
    cfg = settings.intervals
    cfg.button_mode = "all"
    cfg.intervals = {"A4", "M3", "P5", "d5", "m3", "m6"}
    view = ExercisePage(IntervalNames())
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    original = view.question
    panel.quality_row.click()
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    page = panel.stack.currentWidget()
    radios = page.findChildren(QRadioButton)
    assert [radio.text() for radio in radios] == [
        "Interval Only",
        "Interval and Quality",
        "Quality Only",
    ]
    assert radios[0].isChecked() and view.question is original
    radios[2].click()
    assert [radio.isChecked() for radio in radios] == [False, False, True]
    assert view.question.prompt == "What is the interval quality?"
    assert [b.text() for b in view.control_area.answers.buttons] == [
        "A",
        "M",
        "P",
        "m",
        "d",
    ]
    assert all(
        b.accessibleName() == QUALITY_NAMES[b.text()]
        for b in view.control_area.answers.buttons
    )
    next(
        b
        for b in view.control_area.answers.buttons
        if QUALITY_NAMES[b.text()] == view.question.answer
    ).click()
    assert view.session.answered
    next(
        b for b in page.findChildren(QToolButton) if "Back" in b.text()
    ).click()
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    assert (
        panel.stack.currentIndex() == 0
        and panel.quality_row.value.text() == "Quality Only"
    )
    cfg.quality_mode = "combined"
    load_intervals()
    assert (
        cfg.quality_mode == "quality"
        and '"quality_mode": "quality"'
        in view.controller.exercise.settings_signature()
    )
    cfg.button_mode, cfg.button_count = "limited", 2
    view.next_question()
    assert len(view.control_area.answers.buttons) == 2
    assert [
        QUALITY_NAMES[b.text()] for b in view.control_area.answers.buttons
    ] == view.question.choices
    next(
        b
        for b in view.control_area.answers.buttons
        if QUALITY_NAMES[b.text()] == view.question.answer
    ).click()
    assert view.session.answered
    view.close()


def test_saved_empty_selection_and_invalid_range() -> None:
    """
    Keep an intentional empty interval checklist and ignore malformed or
    out-of-bounds ranges.
    """
    saved = store()
    saved.setValue("intervals/buttonCount", "invalid")
    saved.setValue("intervals/intervals", "")
    saved.setValue("intervals/range/bass", "7,60")
    saved.setValue("intervals/range/treble", "typo")
    load_intervals()
    assert not settings.intervals.intervals and not settings.intervals.ranges
    saved.setValue("intervals/intervals", "P1,M3")
    load_intervals()
    assert settings.intervals.intervals == {"M3"}
    assert settings.intervals.button_count == 6


def test_display_defaults_to_harmonic_and_restores_saved_modes() -> None:
    """
    Start with simultaneous notes and honor an existing display
    preference on reload.
    """
    saved = store()
    load_intervals()
    assert settings.intervals.displays == {"Harmonic"}
    question = IntervalNames().generate(random.Random(1))
    assert [len(chord) for chord in question.staff] == [2]
    for modes in ({"Melodic"}, {"Melodic", "Harmonic"}):
        saved.setValue("intervals/display", ",".join(sorted(modes)))
        load_intervals()
        assert settings.intervals.displays == modes


def test_interval_picker_tracks_active_staff_ranges(app: QApplication) -> None:
    """
    Keep the picker, bulk controls, and question choices within the
    selected clefs' ranges.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.intervals
    cfg.clefs = {"treble", "bass"}
    cfg.ranges = {"treble": (28, 30), "bass": (21, 29)}
    cfg.intervals = {"M3", "M9", "P15"}
    cfg.button_mode = "all"
    view = ExercisePage(IntervalNames())
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    boxes = panel.interval_list.boxes
    assert (
        panel.slider.maximum == 9
        and not boxes["M9"].isHidden()
        and boxes["M10"].isHidden()
    )
    panel.boxes["bass"].click()
    assert panel.slider.maximum == panel.slider.high == 3
    assert panel.intervals_row.value.text() == "1 selected"
    assert panel.interval_list.headings["Compound intervals"].isHidden()
    assert {name for name, box in boxes.items() if box.isEnabled()} == {
        name
        for name, iv in settings.WRITTEN_INTERVALS.items()
        if iv.number <= 3
    }
    assert view.question.choices == ["M3"]
    panel.select_all.click()
    assert set(view.question.choices) == {
        name for name, box in boxes.items() if not box.isHidden()
    }
    assert cfg.intervals == set(view.question.choices) | {"M9", "P15"}
    panel.select_all.click()
    panel.slider.move_endpoint("low", delta=-1)
    assert "M9" in cfg.intervals and "M10" not in cfg.intervals
    panel._range_edited("treble", 28, 28)
    assert all(box.isHidden() for box in boxes.values())
    assert panel.slider.isHidden() and not panel.select_all.isEnabled()
    assert (
        panel.intervals_row.value.text() == "None"
        and not view.question.choices
    )
    panel._range_edited("treble", 28, 29)
    assert panel.slider.maximum == 2 and not panel.slider.isHidden()
    assert all(
        settings.WRITTEN_INTERVALS[name].number == 2
        for name in view.question.choices
    )
    load_intervals()
    assert {"M9", "P15"} <= cfg.intervals
    panel._reset_ranges()
    assert not boxes["P15"].isHidden() and boxes["P15"].isChecked()
    view.close()


def test_limited_interval_buttons_use_quality_rows(app: QApplication) -> None:
    """
    Place spellings of the same interval number in one column of the
    limited grid.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.intervals.intervals = {"A3", "M3", "m3", "d3", "P4"}
    view = ExercisePage(IntervalNames(), rng=random.Random(6))
    view.show()
    app.processEvents()
    positions = {
        button.text(): (button.y(), button.x())
        for button in view.control_area.answers.buttons
    }
    assert list(positions) == ["A3", "M3", "P4", "m3", "d3"]
    assert list(positions.values()) == sorted(positions.values())
    assert positions["M3"][0] == positions["P4"][0]
    assert len({positions[name][1] for name in ("A3", "M3", "m3", "d3")}) == 1
    view.close()


def test_buttons_switch_between_a_limit_and_all_eligible_answers(
    app: QApplication,
) -> None:
    """
    Change the answer layout through the submenu and restore the limited
    count.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.intervals
    cfg.clefs = {"treble"}
    cfg.ranges = {"treble": (28, 35)}
    cfg.intervals = set(settings.WRITTEN_INTERVALS)
    view = ExercisePage(IntervalNames(), rng=random.Random(15))
    view.show()
    panel = view.settings_panel
    assert (
        isinstance(panel, IntervalSettingsPanel)
        and view.toolbar.gear is not None
    )
    view.toolbar.gear.click()
    motion.settle()
    original = view.question
    panel.buttons_row.click()
    motion.settle()
    assert (
        view.question is original
        and len(view.control_area.answers.buttons) == 6
    )
    page = panel.stack.currentWidget()
    assert page is not None
    modes = {b.text(): b for b in page.findChildren(QRadioButton)}
    count = page.findChild(FieldComboBox)
    assert (
        count is not None
        and count.isVisible()
        and modes["Limited"].isChecked()
    )
    count.setCurrentIndex(count.findData(3))
    assert (
        len(view.control_area.answers.buttons) == 3
        and view.question.answer in view.question.choices
    )
    modes["All"].click()
    assert panel.buttons_row.value.text() == "All" and not count.isVisible()
    groups = [
        ["A2", "A3", "A4", "A5", "A6", "A7", "A8"],
        ["M2", "M3", "P4", "P5", "M6", "M7", "P8"],
        ["m2", "m3", "m6", "m7"],
        ["d2", "d3", "d4", "d5", "d6", "d7", "d8"],
    ]
    bank = view.control_area.answers.interval_answers
    assert bank.isVisible() and [b.text() for b in bank.buttons] == [
        name for group in groups for name in group
    ]
    for width in (1250, 520):
        view.resize(width, 650)
        app.processEvents()
        positions = {b.text(): (b.y(), b.x()) for b in bank.buttons}
        assert list(positions.values()) == sorted(positions.values())
        assert all(
            positions[upper[-1]][0] < positions[lower[0]][0]
            for upper, lower in pairwise(groups)
        )
        assert bank.horizontalScrollBar().maximum() == 0
    view.control_area.answers.buttons[
        view.question.choices.index(view.question.answer)
    ].click()
    assert view.session.answered
    cfg.__init__()
    load_intervals()
    assert (cfg.button_mode, cfg.button_count) == ("all", 3)
    all_signature = view.controller.exercise.settings_signature()
    panel.quality_modes["interval"].click()
    assert view.question.choices == [str(n) for n in range(2, 9)]
    modes["Limited"].click()
    assert (
        count.isVisible()
        and count.currentData() == 3
        and len(view.control_area.answers.buttons) == 3
    )
    assert view.controller.exercise.settings_signature() != all_signature
    view.close()


@pytest.mark.parametrize("display", settings.INTERVAL_DISPLAYS)
def test_note_value_picker_and_saved_interval_staff(
    app: QApplication,
    display: str,
) -> None:
    """
    Apply the same selected note value in practice and on the saved
    question's staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    display : str
        Melodic or harmonic written intervals.
    """
    cfg = settings.intervals
    cfg.displays = {display}
    view = ExercisePage(IntervalNames(), rng=random.Random(4))
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    panel.values_row.click()
    assert panel.stack._slide is not None
    panel.stack._slide.setCurrentTime(panel.stack._slide.duration())
    boxes = panel.value_boxes
    assert list(boxes) == list(settings.NOTE_VALUES)
    assert boxes["whole"].isChecked() and not boxes["whole"].isEnabled()
    boxes["eighth"].click()
    assert cfg.active_values() == ["whole", "eighth"]
    assert panel.value_pictures.values == cfg.active_values()
    rng = random.Random(3)
    assert {
        view.controller.exercise.generate(rng).value for _ in range(24)
    } == {
        "whole",
        "eighth",
    }
    boxes["whole"].click()
    assert not boxes["eighth"].isEnabled() and cfg.active_values() == [
        "eighth",
    ]
    q = view.question
    assert (
        q is not None and q.value == view.question_view.staff.value == "eighth"
    )
    saved = Question.from_dict(q.to_dict())
    preview = QuestionPreview(IntervalNames.name, question=saved)
    staff = preview.findChild(StaffWidget)
    assert staff is not None
    staff.resize(view.question_view.staff.size())
    expected = view.question_view.staff.grab().toImage()
    assert staff.grab().toImage() == expected
    staff.show_notes(
        saved.staff,
        clef=saved.clef,
        key=saved.key,
        value="whole",
    )
    assert staff.grab().toImage() != expected
    cfg.note_values.clear()
    load_intervals()
    assert cfg.note_values == {
        "eighth",
    } and settings.note_names.note_values == {"whole"}


def test_consonance_switch_grades_both_choices_and_saves(
    app: QApplication,
) -> None:
    """
    Classify written intervals with the Consonance switch and restore
    the mode from storage.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.intervals
    cfg.intervals = {"M3", "A4"}
    view = ExercisePage(IntervalNames(), rng=random.Random(1))
    panel = view.settings_panel
    assert isinstance(panel, IntervalSettingsPanel)
    signature = view.controller.exercise.settings_signature()
    panel.consonance_row.click()
    assert cfg.consonance and not panel.quality_row.isEnabled()
    assert view.controller.exercise.settings_signature() != signature
    rng = random.Random(5)
    seen = set()
    for _ in range(20):
        q = view.controller.exercise.generate(rng)
        low, high = q.staff[0]
        expected = (
            "Consonant"
            if Interval.between(low, high=high).short == "M3"
            else "Dissonant"
        )
        assert q.choices == ["Consonant", "Dissonant"] and q.check(expected)
        seen.add(expected)
    assert seen == {"Consonant", "Dissonant"}
    cfg.consonance = False
    load_intervals()
    assert cfg.consonance
    panel.consonance_row.click()
    assert not cfg.consonance and panel.quality_row.isEnabled()
    assert view.controller.exercise.settings_signature() == signature
    view.close()
