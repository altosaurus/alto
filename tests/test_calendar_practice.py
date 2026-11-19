"""Calendar scheduling, persistent card identity, and the corresponding desktop controls."""

from __future__ import annotations

import json
import random
import sqlite3
import time
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fsrs import Card, Rating, State
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QApplication

from alto import settings
from alto.exercises.base import Exercise, Question
from alto.exercises.library import ChordQualities, NotationIdentification, NoteConstruction, NoteNames
from alto.learning import Database, Learner
from alto.learning.calendar import DAILY_NEW
from alto.learning.database import _CALENDAR_SCHEMA, _SCHEMA, check_snapshot
from alto.learning.grading import DAY, MAX_DAYS, _fuzz, inherited_state, review_options
from alto.learning.learner import PracticeComplete
from alto.theory.pitch import Note
from alto.ui.exercise_view import ExerciseView
from alto.ui.main_window import MainWindow
from alto.ui.settings_panel import NotationSettingsPanel, NoteConstructionSettingsPanel, NoteNameSettingsPanel

NOW = 1_700_000_000.0


@pytest.mark.parametrize("mode", ["SM-2", "FSRS"])
def test_answer_buttons_through_learning_review_and_lapse(mode: str) -> None:
    """
    Check each learning step, ordered review grades and relearning after a lapse.

    Parameters
    ----------
    mode : str
        Calendar scheduler.
    """
    now = NOW
    previous = None
    for grade, expected_hard in [
        (Rating.Hard, 330),
        (Rating.Good, 330),
        (Rating.Good, 600),
        (Rating.Again, None),
        (Rating.Again, 900),
        (Rating.Hard, 900),
        (Rating.Easy, 900),
    ]:
        outcomes = review_options("abc", mode=mode, previous=previous, due=now, now=now)
        again, hard, good, easy = [outcomes[r][0] for r in Rating]
        if expected_hard is None:
            assert again == 600 and DAY <= hard < good < easy
        else:
            assert hard == expected_hard
            if hard == 330:
                assert (again, good) == (60, 600) and easy >= DAY
            elif hard == 600:
                assert again == 60 and DAY <= good < easy
            else:
                assert again == 600 and DAY <= good < easy
                if mode == "SM-2":
                    assert (good, easy) == (DAY, 2 * DAY)
        seconds, previous = outcomes[grade]
        now += seconds


def test_sm2_existing_reviews_and_late_grades() -> None:
    """Keep legacy ease, apply lateness to Good and Easy, and cap very long reviews."""
    old = "[3, 15, 2.5]"
    for grade, delta in [(Rating.Again, -0.2), (Rating.Hard, -0.15), (Rating.Good, 0), (Rating.Easy, 0.15)]:
        on_time = review_options("abc", mode="SM-2", previous=old, due=NOW, now=NOW)[grade]
        late = review_options("abc", mode="SM-2", previous=old, due=NOW, now=NOW + 20 * DAY)[grade]
        assert json.loads(on_time[1])["ease"] == 2.5 + delta
        assert late[0] > on_time[0] if grade in (Rating.Good, Rating.Easy) else late[0] == on_time[0]
    assert _fuzz(MAX_DAYS * 2, minimum=MAX_DAYS + 1, factor=0.9) == MAX_DAYS


def test_fsrs_review_fuzz_preserves_previous_interval() -> None:
    """Keep a five-day review at least five days when the new estimate is close to five."""
    when = datetime.fromtimestamp(NOW, UTC)
    card = Card(card_id=123, state=State.Review, stability=2, difficulty=8, last_review=when - timedelta(days=5), due=when)
    for key in ("a", "b", "c"):
        choices = review_options(key, mode="FSRS", previous=card.to_json(), due=NOW, now=NOW)
        hard, good, easy = (choices[r][0] for r in (Rating.Hard, Rating.Good, Rating.Easy))
        assert 5 * DAY <= hard < good < easy


@pytest.mark.parametrize(
    "phase,step,seconds,grade",
    [
        ("learning", 1, 600, Rating.Good),
        ("learning", 0, 330, Rating.Hard),
        ("relearning", 0, 600, Rating.Again),
    ],
)
def test_inherited_learning_steps(phase: str, step: int, seconds: int, grade: Rating) -> None:
    """
    Preserve the step, phase, delay and review time across both calendar representations.

    Parameters
    ----------
    phase : str
        SM-2 learning phase.
    step : int
        Current learning step.
    seconds : int
        Original delay until review.
    grade : Rating
        Source grade for this step.
    """
    state = json.dumps(dict(phase=phase, step=step, delay=seconds, interval=0, repetitions=0, ease=2.5))
    fsrs = inherited_state("abc", source="SM-2", state=state, due=NOW + seconds, rating=grade)
    card = Card.from_json(fsrs)
    assert card.state.name.lower() == phase and card.step == step and card.last_review == datetime.fromtimestamp(NOW, UTC)
    sm2 = inherited_state("abc", source="FSRS", state=fsrs, due=NOW + seconds, rating=grade)
    assert json.loads(sm2) == json.loads(state)


@pytest.mark.parametrize("mode", ["SM-2", "FSRS"])
def test_schedule_and_retries(mode: str) -> None:
    """
    Only the first submission advances a scheduler. Misses return for another review.

    Parameters
    ----------
    mode : str
        Calendar scheduler under test.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode(mode)
    rng = random.Random(4)
    ex = ChordQualities()
    q = learner.pick(ex, rng=rng, now=NOW)
    learner.record(ex, question=q, answer="?", correct=False, attempt_no=1, seconds=1, now=NOW)
    state = db.conn.execute("SELECT due, state FROM review_schedules").fetchone()
    learner.record(ex, question=q, answer=q.answer, correct=True, attempt_no=2, seconds=1, now=NOW + 1)
    assert db.conn.execute("SELECT due, state FROM review_schedules").fetchone() == state
    assert db.count_attempts(learner.profile.id) == 2
    assert state[0] == NOW + 60
    assert learner.pick(ex, rng=rng, now=state[0]).item_key() == q.item_key()
    learner.record(ex, question=q, answer=q.answer, correct=True, attempt_no=1, seconds=1, now=state[0])
    assert db.conn.execute("SELECT due FROM review_schedules").fetchone()[0] > state[0]


def test_daily_limit_and_profile_history() -> None:
    """Check shared introductions and independent schedules across restarts and mode changes."""
    db = Database()
    ada = db.add_profile("Ada")
    learner = Learner(db, profile=ada)
    learner.set_mode("SM-2")
    ex = EndlessExercise()
    rng = random.Random(1)
    for remaining in range(DAILY_NEW, 0, -1):
        due, new = learner.calendar.queue(ex, profile=ada.id, mode=learner.mode, now=NOW)
        assert (len(due), len(new)) == (0, remaining)
        assert learner.pick(ex, rng=rng, now=NOW) == new[0]
        learner.record(ex, question=new[0], answer=new[0].answer, correct=True, attempt_no=1, seconds=2, now=NOW)
    with pytest.raises(PracticeComplete):
        learner.pick(ex, rng=rng, now=NOW)
    assert len(learner.calendar.queue(ex, profile=ada.id, mode="SM-2", now=NOW + 86400)[1]) == DAILY_NEW
    learner.set_mode("FSRS")
    restored = Database()
    restored.restore(db.snapshot())
    learner = Learner(restored, profile=ada)
    assert learner.mode == "FSRS"
    due, new = learner.calendar.queue(ex, profile=ada.id, mode="FSRS", now=NOW)
    assert (len(due), len(new)) == (10, 0)
    learner.set_mode("SM-2")
    assert learner.calendar.queue(ex, profile=ada.id, mode="SM-2", now=NOW) == ([], [])
    other = Learner(restored, profile=restored.add_profile("Betty"))
    assert other.mode == "ASRS"
    other.set_mode("FSRS")
    other.set_mode("Alto")  # Callers using the original scheduler name select ASRS.
    assert other.mode == "ASRS"
    other.set_mode("ASRS")
    assert restored.conn.execute("SELECT scheduler FROM profiles WHERE id = ?", (other.profile.id,)).fetchone()[0] == "Alto"
    with pytest.raises(ValueError, match="Unknown question scheduler"):
        other.set_mode("missing")


def test_overlapping_ranges(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Widen and narrow a finite exercise while a card is awaiting review.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Isolate the exercise settings.
    """
    cfg = settings.NoteNameSettings(clefs={"treble"}, ranges={"treble": (28, 30)}, key_signatures={0})
    monkeypatch.setattr(settings, "note_names", cfg)
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode("SM-2")
    ex = NoteNames()
    due, new = learner.calendar.queue(ex, profile=learner.profile.id, mode="SM-2", now=NOW)
    assert (len(due), len(new)) == (0, 3)
    q = learner.pick(ex, rng=random.Random(0), now=NOW)
    learner.record(ex, question=q, answer=q.answer, correct=True, attempt_no=1, seconds=1, now=NOW)
    cfg.ranges["treble"] = (48, 49)
    assert [len(x) for x in learner.calendar.queue(ex, profile=learner.profile.id, mode="SM-2", now=NOW + 86400)] == [0, 2]
    cfg.ranges["treble"] = (22, 52)
    cfg.note_values = {"half"}
    due, new = learner.calendar.queue(ex, profile=learner.profile.id, mode="SM-2", now=NOW + 86400)
    assert [card.item_key() for card in due] == [q.item_key()]
    assert due[0].value == "half" and len(new) == DAILY_NEW
    cfg.clefs = {"bass"}
    assert ex.review_question(q, same_settings=False) is None
    cfg.clefs = {"treble"}
    sharp = replace(q, staff=[[Note.parse("C#4")]])
    assert ex.review_question(sharp, same_settings=False) is None
    assert all(card.item_key() != q.item_key() for card in new)


def test_sm2_intervals() -> None:
    """Three successful reviews follow the published 1, 6, 15 day progression."""
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode("SM-2")
    ex = NoteNames()
    now = NOW
    for days in (1, 6, 15):
        q = learner.pick(ex, rng=random.Random(1), now=now)
        learner.record(ex, question=q, answer=q.answer, correct=True, attempt_no=1, seconds=2, now=now)
        now += days * 86400
        assert db.conn.execute("SELECT due FROM review_schedules").fetchone()[0] == now


def test_old_database_migration(tmp_path: Path) -> None:
    """
    Prior answers become reviewable while retaining the profile's original scheduler.

    Parameters
    ----------
    tmp_path : Path
        Temporary database directory.
    """
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.executescript(_SCHEMA + "PRAGMA user_version=1; INSERT INTO profiles VALUES (1, 'Ada', 0);")
    ex = NoteNames()
    q = ex.generate(random.Random(3))
    conn.execute(
        "INSERT INTO items VALUES (1, 'NoteNames', ?, 1, 1, 1, 0, 1000, 1, ?, ?)",
        (q.item_key(), ex.settings_signature(), json.dumps(q.to_dict())),
    )
    conn.commit()
    conn.close()
    db = Database(path)
    learner = Learner(db, profile=db.profiles()[0])
    assert learner.mode == "ASRS"
    learner.set_mode("FSRS")
    assert learner.pick(ex, rng=random.Random(0), now=NOW).item_key() == q.item_key()
    assert db.conn.execute("SELECT introduced_on FROM practice_cards").fetchone()[0] is None
    db.conn.execute("DROP TABLE review_schedules")
    with pytest.raises(ValueError, match="schedule is missing"):
        check_snapshot(db.snapshot())


class EndlessExercise(Exercise):
    """A procedural generator with a practically unbounded set of questions."""

    def generate(self, rng: random.Random) -> Question:
        """
        Draw an item from a very large space.

        Parameters
        ----------
        rng : random.Random
            Candidate stream.

        Returns
        -------
        Question
            A distinct task for the sampled value.
        """
        return Question(str(rng.getrandbits(128)), choices=["A"], answer="A")


@pytest.mark.parametrize("mode", ["SM-2", "FSRS"])
def test_daily_allowances_across_midnight(mode: str) -> None:
    """
    Charge introductions and first review submissions independently across both calendar modes.

    Parameters
    ----------
    mode : str
        Scheduler used to introduce and review the cards.
    """
    db = Database()
    profile = db.add_profile("Ada")
    learner = Learner(db, profile=profile)
    learner.set_mode(mode)
    ex = EndlessExercise()
    rng = random.Random(5)
    start = datetime(2025, 6, 1, 23, 55).timestamp()
    calendar = learner.calendar
    calendar.set_limits(profile.id, new_cards=2, reviews=0)
    for remaining in (2, 1):
        q = learner.pick(ex, rng=rng, now=start)
        assert learner.pick(ex, rng=rng, now=start) == q
        assert calendar.counts(ex, profile=profile.id, mode=mode, now=start) == (0, remaining)
        learner.record(ex, question=q, answer="?", correct=False, attempt_no=1, seconds=2, now=start)
    with pytest.raises(PracticeComplete):
        learner.pick(ex, rng=rng, now=start + 60)
    calendar.set_limits(profile.id, exercise="EndlessExercise", new_cards=None, reviews=1)
    assert calendar.counts(ex, profile=profile.id, mode=mode, now=start + 60) == (1, 0)
    q = learner.pick(ex, rng=rng, now=start + 60)
    learner.record(ex, question=q, answer="?", correct=False, attempt_no=1, seconds=1, now=start + 60)
    learner.record(ex, question=q, answer=q.answer, correct=True, attempt_no=2, seconds=1, now=start + 61)
    other_mode = "FSRS" if mode == "SM-2" else "SM-2"
    assert calendar.counts(ex, profile=profile.id, mode=other_mode, now=start + 200) == (0, 0)
    assert db.conn.execute("SELECT completed FROM daily_reviews").fetchone()[0] == 1
    restored = Database()
    restored.restore(db.snapshot())
    calendar = Learner(restored, profile=profile).calendar
    assert calendar.counts(ex, profile=profile.id, mode=mode, now=start + 299) == (0, 0)
    assert calendar.counts(ex, profile=profile.id, mode=mode, now=start + 300) == (1, 2)
    assert calendar.counts(NoteNames(), profile=profile.id, mode=mode, now=start) == (0, 2)
    assert calendar.limits(restored.add_profile("Ben").id, exercise="EndlessExercise") == (10, 200)
    calendar.set_limits(profile.id, new_cards=120, reviews=5)
    assert calendar.counts(ex, profile=profile.id, mode=mode, now=start + 300) == (1, 120)
    calendar.set_limits(profile.id, exercise="EndlessExercise", new_cards=0, reviews=None)
    assert calendar.counts(ex, profile=profile.id, mode=mode, now=start + 300) == (2, 0)


def test_procedural_review_with_no_new_slots(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Recover an older review still produced by the generator when introductions are paused.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Change exercise settings and control the generator’s sample.
    """
    db = Database()
    profile = db.add_profile("Ada")
    learner = Learner(db, profile=profile)
    ex = EndlessExercise()
    rng = random.Random(5)
    reviewed, unseen = ex.generate(rng), ex.generate(rng)
    learner.record(ex, question=reviewed, answer=reviewed.answer, correct=True, attempt_no=1, seconds=1, now=NOW)
    learner.set_mode("SM-2")
    learner.calendar.set_limits(profile.id, new_cards=0, reviews=1)
    monkeypatch.setattr(ex, "settings_signature", lambda: "changed")
    sample = iter((unseen, reviewed))
    monkeypatch.setattr(ex, "generate", lambda rng: next(sample, unseen))
    assert learner.calendar.counts(ex, profile=profile.id, mode="SM-2", now=NOW) == (1, 0)
    assert learner.pick(ex, rng=rng, now=NOW) == reviewed


def test_v2_unanswered_introduction_survives_upgrade(tmp_path: Path) -> None:
    """
    Reopen an unanswered card even when both allowances are zero.

    Parameters
    ----------
    tmp_path : Path
        Directory for a previous-version database.
    """
    path = tmp_path / "previous.db"
    ex = EndlessExercise()
    q = ex.generate(random.Random(1))
    with sqlite3.connect(path) as old:
        old.executescript(
            _SCHEMA + _CALENDAR_SCHEMA + "PRAGMA user_version=2; INSERT INTO profiles VALUES (1, 'Ada', 0, 'SM-2');",
        )
        old.execute(
            "INSERT INTO practice_cards VALUES (1, 'EndlessExercise', ?, '', ?, '2023-11-14')",
            (q.item_key(), json.dumps(q.to_dict())),
        )
    db = Database(path)
    learner = Learner(db, profile=db.profiles()[0])
    learner.calendar.set_limits(1, new_cards=0, reviews=0)
    assert learner.pick(ex, rng=random.Random(2), now=NOW) == q
    learner.record(ex, question=q, answer=q.answer, correct=True, attempt_no=1, seconds=1, now=NOW)
    assert learner.calendar.counts(ex, profile=1, mode="SM-2", now=NOW + 86400) == (0, 0)
    assert db.conn.execute("SELECT COUNT(*) FROM daily_reviews").fetchone()[0] == 0
    db.conn.execute("DROP TABLE daily_reviews")
    with pytest.raises(ValueError, match="daily practice limits"):
        check_snapshot(db.snapshot())


def test_unbounded_generation() -> None:
    """Counting prepares only the requested items and does not introduce any."""
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    ex = EndlessExercise()
    due, new = learner.calendar.queue(ex, profile=learner.profile.id, mode="FSRS", now=NOW)
    assert not due and len(new) == DAILY_NEW
    assert len(learner.calendar._batches["EndlessExercise"].prepared) == DAILY_NEW
    assert db.conn.execute("SELECT COUNT(*) FROM practice_cards").fetchone()[0] == 0


def test_arts_spaces_misses_by_answered_trials(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Resume an ARTS sequence and use the last first attempt, even after a retry.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Restrict the generator to a single fresh candidate.
    """
    db = Database()
    profile = db.add_profile("Ada")
    learner = Learner(db, profile=profile)
    learner.set_mode("ARTS")
    rng = random.Random(17)
    ex = EndlessExercise()
    missed, other, fresh = (ex.generate(rng) for _ in range(3))
    monkeypatch.setattr(ex, "generate", lambda rng: fresh)
    learner.record(ex, question=missed, answer="?", correct=False, attempt_no=1, seconds=2)
    learner.record(ex, question=missed, answer="A", correct=True, attempt_no=2, seconds=1)
    assert learner.pick(ex, rng=rng, now=NOW + 86400) == fresh
    learner.record(ex, question=other, answer="A", correct=True, attempt_no=1, seconds=1)
    restored = Database()
    restored.restore(db.snapshot())
    learner = Learner(restored, profile=profile)
    assert learner.mode == "ARTS" and learner.pick(ex, rng=rng) == missed
    assert restored.conn.execute("SELECT COUNT(*) FROM review_schedules").fetchone()[0] == 0
    another = Learner(restored, profile=restored.add_profile("Ben"))
    another.set_mode("ARTS")
    assert another.pick(ex, rng=rng) == fresh
    monkeypatch.setattr(ex, "settings_signature", lambda: "other")
    assert learner.pick(ex, rng=rng, avoid=fresh.item_key()) == fresh
    monkeypatch.setattr(ex, "settings_signature", lambda: "")
    restored.conn.execute("UPDATE items SET payload = '{}' WHERE item_key = ?", (missed.item_key(),))
    assert learner.pick(ex, rng=rng) == fresh


def test_arts_correct_response_times_change_the_next_pick(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A slow correct answer can move ahead of an older quick answer and an unseen question.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Control which new question is available.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode("ARTS")
    rng = random.Random(11)
    ex = EndlessExercise()
    quick, slow, filler, fresh = (ex.generate(rng) for _ in range(4))
    monkeypatch.setattr(ex, "generate", lambda rng: fresh)
    for question, seconds in ((quick, 0.3), (slow, 15), (filler, 2), (filler, 1)):
        learner.record(ex, question=question, answer="A", correct=True, attempt_no=1, seconds=seconds)
    assert learner.pick(ex, rng=rng) == slow
    learner.record(ex, question=slow, answer="A", correct=True, attempt_no=1, seconds=0.2)
    assert learner.pick(ex, rng=rng) == fresh


def test_scheduler_controls(app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Choose a scheduler, open its tile, answer the only question and revisit its counts.

    Parameters
    ----------
    app : QApplication
        Desktop application fixture.
    monkeypatch : pytest.MonkeyPatch
        Isolate the exercise settings.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    window = MainWindow(learner)
    cfg = settings.NoteNameSettings(clefs={"treble"}, ranges={"treble": (28, 28)}, key_signatures={0})
    monkeypatch.setattr(settings, "note_names", cfg)
    window.show()
    window.home.set_mode("exercises", animate=False)
    card = next(c for c in window.home.cards if c.exercise_class is NoteNames)
    assert card.counts.isHidden()
    window.open_settings()
    dialog = window._settings
    changes = QSignalSpy(dialog.scheduler_changed)
    dialog.categories.setCurrentRow(7)
    algorithms = dialog.scheduler_list
    assert [algorithms.item(i).text() for i in range(algorithms.count())] == ["ASRS", "ARTS", "SM-2", "FSRS"]
    assert algorithms.currentItem().text() == "ASRS"
    assert "Alto Spaced Repetition System (ASRS)" in dialog.scheduler_description.text()
    assert changes.count() == 0
    QTest.mouseClick(algorithms.viewport(), Qt.MouseButton.LeftButton, pos=algorithms.visualItemRect(algorithms.item(1)).center())
    assert learner.mode == "ARTS" and "Adaptive Response-Time-based Sequencing" in dialog.scheduler_description.text()
    assert card.counts.isHidden()
    dialog.close()
    window.open_settings()
    dialog = window._settings
    dialog.categories.setCurrentRow(7)
    algorithms = dialog.scheduler_list
    assert algorithms.currentItem().text() == "ARTS" and "ARTS" in dialog.scheduler_description.text()
    changes = QSignalSpy(dialog.scheduler_changed)
    QTest.keyClick(algorithms, Qt.Key.Key_Down)
    assert learner.mode == "SM-2" and "SuperMemo 2" in dialog.scheduler_description.text()
    QTest.keyClick(algorithms, Qt.Key.Key_Down)
    assert learner.mode == "FSRS" and "Free Spaced Repetition Scheduler" in dialog.scheduler_description.text()
    assert changes.count() == 2
    app.processEvents()
    assert card.counts.isVisible() and "0 reviews due, 1 new card available" in card.accessibleDescription()
    dialog.close()
    card.click()
    view = window._exercise_page
    q = view.question
    view.submit(q.answer, button=None)
    view.next_question()
    assert view.question is None and view.next_button.text() == "Check again"
    assert view.prompt.isVisible() and not view.buttons
    window.show_home()
    assert "0 reviews due, 0 new cards available" in card.accessibleDescription()
    card.click()
    assert view.question is None
    window.open_settings()
    window._settings.categories.setCurrentRow(7)
    assert window._settings.scheduler_list.currentItem().text() == "FSRS"
    assert "Free Spaced Repetition Scheduler" in window._settings.scheduler_description.text()
    window._settings.scheduler_list.setCurrentRow(0)
    assert view.question is not None
    window._settings.close()
    window.show_home()
    assert card.counts.isHidden()
    learner.set_mode("FSRS")
    window._restore_defaults()
    assert learner.mode == "ASRS" and db.count_attempts(learner.profile.id) == 1
    window.close()


def test_daily_limit_controls_follow_the_scheduler(app: QApplication) -> None:
    """
    Override either field, restore inheritance, and leave the submenu when switching to ARTS.

    Parameters
    ----------
    app : QApplication
        Desktop application fixture.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    window = MainWindow(learner)
    window.show()
    window.home.set_mode("exercises", animate=False)
    window.open_settings()
    dialog = window._settings
    dialog.categories.setCurrentRow(7)
    assert dialog.daily_limits.isHidden()
    dialog.scheduler_list.setCurrentRow(2)
    assert dialog.daily_limits.isVisible()
    dialog.daily_limits.fields[0].setValue(3)
    dialog.daily_limits.fields[1].setValue(8)
    dialog.close()
    tile = next(card for card in window.home.cards if card.exercise_class is NoteNames)
    assert "3 new cards available" in tile.accessibleDescription()
    tile.click()
    view = window._exercise_page
    panel = view.settings_panel
    editor = panel.limits_editor
    assert not panel.limits_row.isHidden() and panel.limits_row.value.text() == "3 new · 8 reviews"
    panel.limits_row.click()
    QTest.qWait(250)
    assert panel.stack.currentIndex() == panel.limits_page
    assert all(box.isChecked() for box in editor.inherit)
    editor.inherit[0].click()
    editor.fields[0].setValue(5)
    assert learner.calendar.overrides(learner.profile.id, exercise="NoteNames") == (5, None)
    window.open_settings()
    dialog = window._settings
    dialog.categories.setCurrentRow(7)
    dialog.daily_limits.fields[0].setValue(2)
    dialog.daily_limits.fields[1].setValue(4)
    assert [field.value() for field in editor.fields] == [5, 4]
    editor.inherit[0].click()
    assert not editor.fields[0].isEnabled() and editor.fields[0].value() == 2
    dialog.scheduler_list.setCurrentRow(1)
    assert panel.limits_row.isHidden() and panel.stack.currentIndex() == 0 and dialog.daily_limits.isHidden()
    dialog.scheduler_list.setCurrentRow(3)
    assert not panel.limits_row.isHidden() and dialog.daily_limits.isVisible()
    window.show_home()
    dialog.daily_limits.fields[0].setValue(1)
    dialog.close()
    tile.click()
    assert panel.limits_row.value.text() == "1 new · 4 reviews"
    window.close()


def test_unplayable_prompts_and_unreadable_history(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Settings guidance and an unreadable saved card never become queued questions.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Isolate the notation filter.
    """
    monkeypatch.setattr(settings.notation, "terms", set())
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    ex = NotationIdentification()
    assert learner.calendar.queue(ex, profile=learner.profile.id, mode="SM-2", now=NOW) == ([], [])
    ex = ChordQualities()
    db.conn.execute(
        "INSERT INTO practice_cards VALUES (?, 'ChordQualities', 'lost', '', '{}', NULL, 0)",
        (learner.profile.id,),
    )
    db.conn.commit()
    due, new = learner.calendar.queue(ex, profile=learner.profile.id, mode="SM-2", now=NOW)
    assert due == [] and len(new) == DAILY_NEW


def test_failed_migration_keeps_current_database() -> None:
    """A malformed older backup fails migration before replacing live history."""
    broken = sqlite3.connect(":memory:")
    broken.executescript(
        "CREATE TABLE profiles (id); CREATE TABLE items (id); CREATE TABLE attempts (id); PRAGMA user_version=1;",
    )
    db = Database()
    ada = db.add_profile("Ada")
    with pytest.raises(ValueError, match="could not be migrated"):
        db.restore(broken.serialize())
    assert db.profiles() == [ada]
    broken.close()


@pytest.mark.parametrize("exercise_class", [NoteNames, NoteConstruction])
@pytest.mark.parametrize("mode", ["SM-2", "FSRS"])
def test_adding_a_key_after_finishing_a_note_exercise(
    exercise_class: type[Exercise],
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The key checkbox reopens a completed exercise and the tile counts every remaining new pitch.

    Parameters
    ----------
    exercise_class : type of Exercise
        Identification or construction.
    mode : str
        Active calendar scheduler.
    monkeypatch : pytest.MonkeyPatch
        Isolate the selected clef, range and keys.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode(mode)
    learner.calendar.set_limits(learner.profile.id, new_cards=30, reviews=None)
    window = MainWindow(learner)
    monkeypatch.setitem(settings.DEFAULT_RANGES, "treble", (28, 39))
    monkeypatch.setattr(settings, "note_names", settings.NoteNameSettings(clefs={"treble"}, key_signatures={0}))
    monkeypatch.setattr(settings, "construction", settings.ConstructionSettings(clefs={"treble"}, key_signature=True, keys={0}))
    window.show()
    window.home.set_mode("exercises", animate=False)
    tile = next(card for card in window.home.cards if card.exercise_class is exercise_class)
    assert "12 new cards available" in tile.accessibleDescription()
    tile.click()
    view = window._exercise_page
    for _ in range(12):
        question = view.question
        assert question is not None and question.key == 0
        learner.record(view.exercise, question=question, answer=question.answer, correct=True, attempt_no=1, seconds=2)
        view.next_question()
    assert view.question is None
    panel = view.settings_panel
    if isinstance(panel, NoteNameSettingsPanel):
        panel.key_boxes[1].click()
    else:
        assert isinstance(panel, NoteConstructionSettingsPanel)
        panel.major_keys.boxes[1].click()
    assert view.question is not None and view.question.key == 1
    window.show_home()
    assert "0 reviews due, 12 new cards available" in tile.accessibleDescription()
    window.close()


def test_finite_construction_catalog_matches_the_generator(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Count and filter each scale, degree, accidental and staff-signature combination.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Isolate the construction configuration.
    """
    monkeypatch.setitem(settings.DEFAULT_RANGES, "treble", (28, 34))
    cfg = settings.ConstructionSettings(
        clefs={"treble"},
        key_signature=True,
        keys={0, 2},
        major=True,
        minor=True,
        minor_keys={-1},
        staff_keys={0, 1},
        degrees={1, 3},
        accidentals=True,
    )
    monkeypatch.setattr(settings, "construction", cfg)
    ex = NoteConstruction()
    rng = random.Random(7)
    cards = list(ex.daily_candidates(rng))
    identities = {q.item_key() for q in cards}
    assert len(cards) == len(identities) == ex.card_count() == 3 * 2 * 2 * 3
    assert all(ex.generate(rng).item_key() in identities for _ in range(100))
    cfg.minor = False
    cfg.keys = {0}
    cfg.staff_keys = {0}
    cfg.degrees = {1}
    cfg.accidentals = False
    survivors = [q for q in cards if ex.review_question(q, same_settings=False) is not None]
    assert len(survivors) == ex.card_count() == 1
    cfg.question_type = "notes"
    assert ex.review_question(survivors[0], same_settings=False) is None
    assert ex.card_count() == 7


@pytest.mark.parametrize("scheduler", ["SM-2", "FSRS"])
@pytest.mark.parametrize("question_type", ["button", "staff"])
def test_adding_a_notation_symbol_after_exhausting_the_deck(
    scheduler: str,
    question_type: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A correct answer finishes a single-symbol deck. Selecting another symbol adds one card.

    Parameters
    ----------
    scheduler : str
        Calendar scheduler.
    question_type : str
        Answer controls used by the exercise.
    monkeypatch : pytest.MonkeyPatch
        Isolate the notation settings.
    """
    cfg = settings.NotationSettings(terms={"Vertical turn"}, question_type=question_type)
    monkeypatch.setattr(settings, "notation", cfg)
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode(scheduler)
    ex = NotationIdentification()
    counts = learner.calendar.counts(ex, profile=learner.profile.id, mode=scheduler, now=time.time())
    assert counts == (0, 1)
    view = ExerciseView(ex, learner=learner)
    q = view.question
    assert q is not None and q.answer == "Vertical turn"
    if question_type == "button":
        view.buttons[0].click()
    else:
        view.submit(q.answer, button=None)
    assert view.answered
    view.next_question()
    assert view.question is None
    assert learner.calendar.counts(ex, profile=learner.profile.id, mode=scheduler, now=time.time()) == (0, 0)
    panel = view.settings_panel
    assert isinstance(panel, NotationSettingsPanel)
    panel.terms.boxes["Accent"].click()
    assert view.question is not None and view.question.answer == "Accent" and view.question.notation_excerpt
    assert set(view.question.choices) == (cfg.terms if question_type == "button" else set())
    due, new = learner.calendar.queue(ex, profile=learner.profile.id, mode=scheduler, now=time.time())
    assert due == []
    assert len(new) == 1 and new[0].item_key() == view.question.item_key()
    assert ex.card_count() == 2


@pytest.mark.parametrize("question_type", ["button", "staff"])
def test_notation_catalog_has_one_card_per_term(question_type: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Exhaustive enumeration agrees with the tile count and the ordinary generator.

    Parameters
    ----------
    question_type : str
        Whether to click or identify a highlighted mark.
    monkeypatch : pytest.MonkeyPatch
        Isolate the enabled terms.
    """
    terms = set(settings.NOTATION_TERMS)
    monkeypatch.setattr(settings, "notation", settings.NotationSettings(terms=terms, question_type=question_type))
    ex = NotationIdentification()
    rng = random.Random(3)
    cards = list(ex.daily_candidates(rng))
    keys = {q.item_key() for q in cards}
    assert {q.answer for q in cards} == terms
    assert len(cards) == len(keys) == ex.card_count()
    groups = ex.card_groups()
    assert all(groups[q.item_key()] == q.answer for q in cards)
    assert all(groups[q.item_key()] == q.answer for q in (ex.generate(rng) for _ in range(200)))


def test_unselected_notation_cards_keep_their_schedule(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Restore due cards with eligible distractors after editing term, button and question-type settings.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Isolate the term selection.
    """
    cfg = settings.NotationSettings(terms={"Koron", "Turn", "Stem"})
    monkeypatch.setattr(settings, "notation", cfg)
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    learner.set_mode("SM-2")
    ex = NotationIdentification()
    q = learner.pick(ex, rng=random.Random(4), now=NOW)
    learner.record(ex, question=q, answer=q.answer, correct=True, attempt_no=1, seconds=1, now=NOW)
    cfg.terms = {q.answer}
    later = NOW + 86400
    due, new = learner.calendar.queue(ex, profile=learner.profile.id, mode="SM-2", now=later)
    assert len(due) == 1 and due[0].choices == [q.answer] and due[0].item_key() == q.item_key()
    assert ex.card_count() == 1 + len(new)
    cfg.question_type = "staff"
    assert ex.review_question(q, same_settings=False) is None
    assert learner.calendar.counts(ex, profile=learner.profile.id, mode="SM-2", now=later) == (0, ex.card_count())
    cfg.terms = set()
    assert learner.calendar.counts(ex, profile=learner.profile.id, mode="SM-2", now=later) == (0, 0)
    cfg.question_type = "button"
    cfg.terms = {q.answer}
    assert learner.pick(ex, rng=random.Random(1), now=later).item_key() == q.item_key()


@pytest.mark.parametrize("mode", ["SM-2", "FSRS"])
def test_existing_notation_examples_share_the_latest_review(mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A profile with multiple saved examples retains the latest grade and its due date.

    Parameters
    ----------
    mode : str
        Calendar scheduler used to grade the old examples.
    monkeypatch : pytest.MonkeyPatch
        Isolate the notation settings.
    """
    cfg = settings.NotationSettings(terms={"Vertical turn"})
    monkeypatch.setattr(settings, "notation", cfg)
    ex = NotationIdentification()
    rng = random.Random(3)
    examples = {q.item_key(): q for q in (ex.generate(rng) for _ in range(16))}
    old, recent, unanswered = list(examples.values())[:3]
    db = Database()
    profile = db.add_profile("Ada")
    learner = Learner(db, profile=profile)
    learner.set_mode(mode)
    # Recreate three separately introduced cards from a profile using the old catalog.
    for q in (old, recent, unanswered):
        db.conn.execute(
            "INSERT INTO practice_cards VALUES (?, 'NotationIdentification', ?, ?, ?, NULL, 0)",
            (profile.id, q.item_key(), ex.settings_signature(), json.dumps(q.to_dict())),
        )
    db.conn.commit()
    for q, correct, when in ((old, False, NOW), (recent, True, NOW + 90)):
        learner.record(ex, question=q, answer=q.answer if correct else "?", correct=correct, attempt_no=1, seconds=1, now=when)
    due_at = db.conn.execute("SELECT due FROM review_schedules WHERE item_key = ?", (recent.item_key(),)).fetchone()[0]
    if mode == "SM-2":
        assert due_at == NOW + 90 + 86400
    restored = Database()
    restored.restore(db.snapshot())
    learner = Learner(restored, profile=profile)
    with pytest.raises(PracticeComplete):
        learner.pick(ex, rng=random.Random(0), now=due_at - 1)
    due, new = learner.calendar.queue(ex, profile=profile.id, mode=mode, now=due_at)
    assert [q.item_key() for q in due] == [recent.item_key()] and not new
    assert restored.count_attempts(profile.id) == 2
    learner.record(ex, question=due[0], answer="?", correct=False, attempt_no=1, seconds=1, now=due_at)
    assert learner.calendar.counts(ex, profile=profile.id, mode=mode, now=due_at + 59) == (0, 0)
    assert learner.pick(ex, rng=random.Random(0), now=due_at + 60).item_key() == recent.item_key()
