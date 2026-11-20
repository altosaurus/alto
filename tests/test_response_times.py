"""Speed-based grading, rolling exercise samples, and their Practice settings."""

import random
import time
from unittest.mock import Mock

import pytest
from fsrs import Rating
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication

from alto import settings as exercise_settings
from alto.exercises.library import KeyboardIntervals, KeyboardNotes, NoteNames
from alto.learning import Database, Learner
from alto.learning.response_times import ResponseTimes
from alto.ui.app_settings import AppSettingsDialog
from alto.ui.exercise_view import ExerciseView
from alto.ui.response_times import ResponseTimeDialog
from alto.ui.stats_dialog import StatsPage


def seed_times(learner: Learner, count: int, *, exercise: str = "NoteNames") -> None:
    """
    Add chronological correct first answers from one to count seconds.

    Parameters
    ----------
    learner : Learner
        Profile that practiced the exercise.
    count : int
        Number of answers to add.
    exercise : str
        Registered class name of the exercise.
    """
    for i in range(1, count + 1):
        learner.db.add_attempt(
            learner.profile.id,
            exercise=exercise,
            item_key="seed",
            attempt_no=1,
            answer="A",
            correct=True,
            duration_ms=i * 1000,
            answered_at=i,
        )


@pytest.mark.parametrize("mode", ["SM-2", "FSRS"])
def test_grades_use_previous_exercise_history(mode: str) -> None:
    """
    Assign all three grades to the actual schedule and keep misses and self-grading independent.

    Parameters
    ----------
    mode : str
        Calendar scheduler under test.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode(mode)
    seed_times(learner, 39)
    ex = NoteNames()
    rng = random.Random(1)
    q = learner.pick(ex, rng=rng)
    assert learner.record(ex, question=q, correct=True, answer=q.answer, attempt_no=1, seconds=40) is None
    now = time.time()
    for seconds, valid, expected in (
        (2, True, Rating.Easy),
        (20, True, Rating.Good),
        (90, True, Rating.Hard),
        (1000, False, Rating.Good),
    ):
        q = learner.pick(ex, rng=rng)
        assigned = learner.record(
            ex,
            question=q,
            correct=True,
            answer=q.answer,
            attempt_no=1,
            seconds=seconds,
            timing_valid=valid,
            now=now,
        )
        assert assigned is not None and assigned.rating == expected
        due, rating = db.conn.execute(
            "SELECT due, last_rating FROM review_schedules WHERE item_key=?",
            (q.item_key(),),
        ).fetchone()
        assert rating == expected and due == now + assigned.seconds
    q = learner.pick(ex, rng=rng)
    learner.record(ex, question=q, correct=False, answer="wrong", attempt_no=1, seconds=123)
    learner.record(ex, question=q, correct=True, answer=q.answer, attempt_no=2, seconds=111)
    assert (
        db.conn.execute("SELECT last_rating FROM review_schedules WHERE item_key=?", (q.item_key(),)).fetchone()[0]
        == Rating.Again
    )
    assert len(learner.response_times("NoteNames").times) == 43
    assert learner.response_times("NoteNames").times[-1] == 90000
    assert not learner.response_times("KeyboardNotes").times
    other = Learner(db, profile=db.add_profile("Ben"))
    assert not other.response_times("NoteNames").times
    q = learner.pick(ex, rng=rng)
    learner.record(ex, question=q, correct=True, answer=q.answer, attempt_no=1, seconds=1, self_grading=True)
    assert not db.conn.execute("SELECT 1 FROM review_schedules WHERE item_key=?", (q.item_key(),)).fetchone()


def test_rolling_window_and_adjustable_cutoffs() -> None:
    """Keep the most recent observations and use inclusive percentile interpolation with neutral ties."""
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    seed_times(learner, 110)
    sample = learner.response_times("NoteNames")
    assert sample.times == tuple(range(11000, 110001, 1000))
    assert sample.percentile(15) == 25850
    assert sample.grade(25850) == sample.grade(95150) == Rating.Good
    assert sample.grade(25849) == Rating.Easy and sample.grade(95151) == Rating.Hard
    learner.set_speed_thresholds(easy=5, hard=25)
    sample = learner.response_times("NoteNames")
    assert sample.grade(20000) == Rating.Good and sample.grade(90000) == Rating.Hard
    with pytest.raises(ValueError, match="percentages"):
        learner.set_speed_thresholds(easy=80, hard=30)
    assert ResponseTimes((1000,) * 40, 0, 0).grade(1) == Rating.Good


def test_distribution_tool_and_timed_feedback(app: QApplication) -> None:
    """
    Edit the bands, inspect two exercises, and see the assigned interval on a graded question.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    seed_times(learner, 100)
    learner.set_mode("SM-2")
    settings = AppSettingsDialog(learner=learner)
    settings.categories.setCurrentItem(settings.categories.findItems("Practice", Qt.MatchFlag.MatchExactly)[0])
    settings.response_times_button.click()
    tool = settings.findChild(ResponseTimeDialog)
    assert tool is not None
    tool.exercise.setCurrentText(NoteNames.name)
    assert sum(int(row[2]) for row in tool.chart.rows) == 100
    tool.easy.setValue(25)
    tool.hard.setValue(5)
    assert tool.good.text() == "70%" and "25.750 s" in tool.summary.text()
    assert "95.050 s" in tool.summary.text() and tool.easy.maximum() == 95
    tool.easy.setValue(0)
    tool.hard.setValue(0)
    assert "All correct answers earn Good" in tool.summary.text()
    tool.exercise.setCurrentText(KeyboardNotes.name)
    assert not tool.chart.rows and "40 more needed" in tool.summary.text()
    # One very fast and one slow answer fall outside the tightly clustered central bins.
    for i, ms in enumerate([100, *([10000] * 40), 80000]):
        db.add_attempt(
            learner.profile.id,
            exercise="KeyboardNotes",
            item_key="C",
            attempt_no=1,
            answer="C",
            correct=True,
            duration_ms=ms,
            answered_at=i,
        )
    tool.exercise.setCurrentText(NoteNames.name)
    tool.exercise.setCurrentText(KeyboardNotes.name)
    assert [row[2] for row in tool.chart.rows] == ["1", "40", "1"]
    tool.close()
    settings.close()
    assert Learner(db, profile=learner.profile).response_times("NoteNames").easy_percent == 0
    stats = StatsPage(learner)
    stats.exercise.setCurrentText(KeyboardNotes.name)
    stats.response_times_button.click()
    chart = stats.findChild(ResponseTimeDialog)
    assert chart is not None and chart.exercise.currentText() == KeyboardNotes.name
    chart.close()
    stats.close()
    learner.set_speed_thresholds(easy=15, hard=15)
    view = ExerciseView(NoteNames(), learner=learner)
    view.show()
    app.processEvents()
    view.settings_panel.next_question_mode = "Wait"
    assert view.review_interval.isVisible() and view.review_interval.text().startswith("Easy:")
    assert view.question is not None
    view._clock = time.monotonic() - 1
    view.submit(view.question.answer, button=None)
    assert "Easy" in view.review_interval.text() and view.review_interval.isVisible()
    view.next_question()
    view._application_state_changed(Qt.ApplicationState.ApplicationInactive)
    assert view.question is not None
    view.submit(view.question.answer, button=None)
    assert "Good" in view.review_interval.text()
    assert db.conn.execute("SELECT timing_valid FROM attempts ORDER BY id DESC LIMIT 1").fetchone()[0] == 0
    view.close()


@pytest.mark.parametrize(
    ("exercise", "mode", "buttons"),
    [
        (NoteNames, "SM-2", "limited"),
        (KeyboardNotes, "SM-2", "limited"),
        (KeyboardNotes, "FSRS", "limited"),
        (KeyboardIntervals, "SM-2", "limited"),
        (KeyboardIntervals, "SM-2", "compact"),
        (KeyboardIntervals, "FSRS", "all"),
    ],
)
@pytest.mark.parametrize(("seconds", "grade"), [(1, Rating.Easy), (50, Rating.Good), (100, Rating.Hard)])
def test_passing_intervals_on_the_question(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    exercise: type,
    mode: str,
    buttons: str,
    seconds: int,
    grade: Rating,
) -> None:
    """
    Show the available intervals where the card is drawn and schedule the displayed outcome.

    Parameters
    ----------
    app : QApplication
        Runs the layout before its geometry is inspected.
    monkeypatch : pytest.MonkeyPatch
        Fix the review timestamp and detect a second draw of the intervals.
    exercise : type
        Staff or keyboard exercise.
    mode : str
        Calendar scheduler.
    buttons : str
        Answer layout for keyboard interval questions.
    seconds : int
        Time taken to answer.
    grade : Rating
        Expected rating in this exercise's distribution.
    """
    now = 1800000000
    monkeypatch.setattr(time, "time", lambda: now)
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode(mode)
    if exercise is KeyboardNotes:
        monkeypatch.setattr(exercise_settings.keyboard, "low", 60)
        monkeypatch.setattr(exercise_settings.keyboard, "high", 64)
        monkeypatch.setattr(exercise_settings.keyboard, "key_signature", mode == "SM-2")
    elif exercise is KeyboardIntervals:
        monkeypatch.setattr(exercise_settings.keyboard_intervals, "compact_buttons", buttons == "compact")
        monkeypatch.setattr(exercise_settings.keyboard_intervals, "all_interval_buttons", buttons == "all")
    seed_times(learner, 100, exercise=exercise.__name__)
    view = ExerciseView(exercise(), learner=learner)
    view.settings_panel.next_question_mode = "Wait"
    view.show()
    previews = view._speed_previews
    assert previews is not None and list(previews) == [Rating.Hard, Rating.Good, Rating.Easy]
    labels = [f"{rating.name}: {interval.duration}" for rating, interval in previews.items()]
    label = view.review_interval
    for width in (700, 1300, 700):
        view.resize(width, 700)
        app.processEvents()
        assert label.isVisible() and label.width() >= label.sizeHint().width()
        top = label.mapTo(view, QPoint())
        if exercise in (KeyboardNotes, KeyboardIntervals):
            assert label.text() == "    ".join(labels)
            keyboard = view.keyboard
            bottom = keyboard.mapTo(view, keyboard.rect().bottomLeft())
            assert top.y() > bottom.y()
            right = bottom.x() + (keyboard.width() + min(keyboard.full_width(), keyboard.width())) / 2
            assert abs(top.x() + label.width() - right) <= 1
        else:
            assert label.text().splitlines() == list(reversed(labels))
            assert label.accessibleName() == f"Next intervals: {', '.join(reversed(labels))}"
            corner = view.staff.mapTo(view, view.staff.rect().bottomRight())
            assert 0 < top.x() - corner.x() <= 16 and top.y() + label.height() - 1 == corner.y()
    assert view.question is not None
    key = view.question.item_key()
    now += seconds
    view._clock = time.monotonic() - seconds
    with monkeypatch.context() as check:
        check.setattr("alto.learning.calendar.review_options", Mock(side_effect=AssertionError("Intervals recalculated")))
        view.submit(view.question.answer, button=None)
    assert tuple(db.conn.execute("SELECT last_rating, due FROM review_schedules WHERE item_key=?", (key,)).fetchone()) == (
        grade,
        now + previews[grade].seconds,
    )
    assert label.text().endswith(f"{grade.name} · {previews[grade].duration}")
    updated = learner.calendar.passing_intervals(
        exercise.__name__,
        profile=learner.profile.id,
        key=key,
        mode=mode,
        now=now,
        displayed=previews,
    )
    assert updated[grade].previous_state != previews[grade].previous_state
    view.close()
