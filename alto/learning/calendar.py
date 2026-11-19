"""
Daily exercise queues for SM-2 and FSRS.

The scheduler controls when an introduced card is due. Each exercise supplies new
questions under its current settings. Counting a prepared question does not introduce it.
"""

from __future__ import annotations

import json
import math
import random
import sqlite3
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

from fsrs import Card, Rating, Scheduler

from alto.exercises.base import Exercise, Question
from alto.learning.database import Database

DAILY_NEW = 10
DAILY_REVIEWS = 200
CALENDAR_SCHEDULERS = ("SM-2", "FSRS")
DEFAULT_SCHEDULER = "ASRS"
SCHEDULERS = (DEFAULT_SCHEDULER, "ARTS", *CALENDAR_SCHEDULERS)
_FSRS = Scheduler()


def _sm2_delay(interval: int) -> int:
    """
    Convert a stored SM-2 interval to seconds, including the retry after a miss.

    Parameters
    ----------
    interval : int
        Days until review, or zero for a missed card.

    Returns
    -------
    int
        Seconds between the first submission and the next scheduled review.

    Examples
    --------
    >>> _sm2_delay(0), _sm2_delay(1)
    (60, 86400)
    """
    return interval * 86400 if interval else 60


@dataclass
class _Batch:
    """
    One exercise's candidate stream for the current profile, settings and local day.

    Examples
    --------
    >>> batch = _Batch("today", iter(()), {})
    >>> batch.prepared
    {}
    """

    seed: str
    stream: Iterator[Question]
    prepared: dict[str, Question]


class CalendarPractice:
    """
    Prepare daily exercise queues and store each scheduler's review dates.

    Examples
    --------
    >>> practice = CalendarPractice(Database())
    >>> practice.db.profiles()
    []
    """

    def __init__(self, db: Database) -> None:
        """
        Attach the queues to an Alto database.

        Parameters
        ----------
        db : Database
            Database containing the profile and its cards.

        Examples
        --------
        >>> CalendarPractice(Database())._batches
        {}
        """
        self.db = db
        self._batches: dict[str, _Batch] = {}

    def limits(self, profile: int, *, exercise: str = "") -> tuple[int, int]:
        """
        Return the effective daily new-card and review limits.

        Parameters
        ----------
        profile : int
            Profile whose settings to read.
        exercise : str
            Exercise class name, or an empty string for profile defaults.

        Returns
        -------
        tuple of int and int
            New cards and completed reviews allowed per exercise per local day.

        Examples
        --------
        >>> CalendarPractice(Database()).limits(1)
        (10, 200)
        """
        new, reviews = DAILY_NEW, DAILY_REVIEWS
        for row in self.db.conn.execute(
            "SELECT new_cards, reviews FROM practice_limits WHERE profile_id = ? AND exercise IN ('', ?) ORDER BY exercise",
            (profile, exercise),
        ):
            new = new if row[0] is None else row[0]
            reviews = reviews if row[1] is None else row[1]
        return new, reviews

    def overrides(self, profile: int, *, exercise: str) -> tuple[int | None, int | None]:
        """
        Read the two explicitly saved limits for an exercise.

        Parameters
        ----------
        profile : int
            Active profile.
        exercise : str
            Exercise class name.

        Returns
        -------
        tuple
            A number for each override, or None for each inherited value.

        Examples
        --------
        >>> CalendarPractice(Database()).overrides(1, exercise="NoteNames")
        (None, None)
        """
        row = self.db.conn.execute(
            "SELECT new_cards, reviews FROM practice_limits WHERE profile_id = ? AND exercise = ?",
            (profile, exercise),
        ).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def set_limits(self, profile: int, *, exercise: str = "", new_cards: int | None, reviews: int | None) -> None:
        """
        Save the profile defaults or an exercise's individual overrides.

        Parameters
        ----------
        profile : int
            Active profile.
        exercise : str
            Exercise class name, or an empty string for the profile defaults.
        new_cards : int or None
            Daily introductions, or None to inherit.
        reviews : int or None
            Daily reviews, or None to inherit.

        Examples
        --------
        >>> db = Database()
        >>> practice = CalendarPractice(db)
        >>> profile = db.add_profile("Ada").id
        >>> practice.set_limits(profile, new_cards=5, reviews=30)
        >>> practice.limits(profile, exercise="NoteNames")
        (5, 30)
        """
        with self.db.write_transaction():
            self.db.conn.execute(
                "INSERT INTO practice_limits VALUES (?, ?, ?, ?) ON CONFLICT DO UPDATE "
                "SET new_cards=excluded.new_cards, reviews=excluded.reviews",
                (profile, exercise, new_cards, reviews),
            )

    def reset_limits(self, profile: int) -> None:
        """
        Restore the profile defaults and remove its exercise overrides.

        Parameters
        ----------
        profile : int
            Profile whose limits to reset.

        Examples
        --------
        Restoring defaults keeps the day's introductions and completed reviews.
        """
        with self.db.write_transaction():
            self.db.conn.execute("DELETE FROM practice_limits WHERE profile_id = ?", (profile,))

    def queue(self, exercise: Exercise, *, profile: int, mode: str, now: float) -> tuple[list[Question], list[Question]]:
        """
        Find due reviews and prepare the remaining new cards for this local day.

        Parameters
        ----------
        exercise : Exercise
            Exercise with its current settings.
        profile : int
            Active profile ID.
        mode : str
            Calendar scheduler whose due dates apply.
        now : float
            Current timestamp.

        Returns
        -------
        tuple of list of Question and list of Question
            Due reviews, oldest first, and new questions available for introduction.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> ada = db.add_profile("Ada")
        >>> due, new = CalendarPractice(db).queue(NoteNames(), profile=ada.id, mode="FSRS", now=1000)
        >>> not due and len(new) == DAILY_NEW
        True
        """
        due, new, _ = self._available(exercise, profile=profile, mode=mode, now=now, limit=None)
        return due, new

    def counts(self, exercise: Exercise, *, profile: int, mode: str, now: float) -> tuple[int, int]:
        """
        Count due reviews and unseen cards available with the selected settings.

        Parameters
        ----------
        exercise : Exercise
            Exercise shown on the tile.
        profile : int
            Active profile.
        mode : str
            Calendar scheduler.
        now : float
            Current timestamp.

        Returns
        -------
        tuple of int and int
            Due and new counts. Exact catalogs can be counted without rendering their cards.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> CalendarPractice(db).counts(NoteNames(), profile=db.add_profile("Ada").id, mode="SM-2", now=100)[1] > 0
        True
        """
        due, _, count = self._available(exercise, profile=profile, mode=mode, now=now, limit=0)
        return len(due), count

    @staticmethod
    def _grouped_reviews(rows: Iterable[sqlite3.Row], *, groups: dict[str, str], mode: str) -> list[sqlite3.Row]:
        """
        Keep the most recently graded example of each eligible skill, in due order.

        Parameters
        ----------
        rows : iterable of sqlite3.Row
            Introduced examples in due order, including examples without a grade.
        groups : dict of str to str
            Eligible example keys and their shared skills.
        mode : str
            Scheduler whose saved state supplies the last review time.

        Returns
        -------
        list of sqlite3.Row
            One representative per introduced skill. Its existing schedule applies to the entire group.

        Examples
        --------
        Several previously graded Vertical turn examples contribute one review date.
        """
        latest: dict[str, tuple[float, sqlite3.Row]] = {}
        for row in rows:
            group = groups.get(row["item_key"])
            if group is None:
                continue
            reviewed = -math.inf
            if row["due"] is not None:
                state = json.loads(row["state"])
                if mode == "FSRS":
                    reviewed = datetime.fromisoformat(state["last_review"]).timestamp()
                else:
                    reviewed = row["due"] - _sm2_delay(state[1])
            if group not in latest or reviewed > latest[group][0]:
                latest[group] = reviewed, row
        return sorted((row for _, row in latest.values()), key=lambda row: (row["due"] is not None, row["due"], row["item_key"]))

    def _available(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
        limit: int | None,
    ) -> tuple[list[Question], list[Question], int]:
        """
        Match introduced cards against the active catalog and prepare the requested new questions.

        Parameters
        ----------
        exercise : Exercise
            Exercise with its current settings.
        profile : int
            Active profile.
        mode : str
            Calendar scheduler.
        now : float
            Current timestamp.
        limit : int or None
            Maximum new cards to render from an exact catalog. None requests them all.

        Returns
        -------
        tuple
            Reviews, prepared new questions, and the available new-card count.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> CalendarPractice(db)._available(NoteNames(), profile=1, mode="SM-2", now=100, limit=0)[1]
        []
        """
        name = type(exercise).__name__
        signature = exercise.settings_signature()
        today = datetime.fromtimestamp(now).date().isoformat()
        seed = json.dumps([today, profile, name, signature])
        batch = self._batches.get(name)
        if batch is None or batch.seed != seed:
            batch = self._batches[name] = _Batch(seed, exercise.daily_candidates(random.Random(seed)), {})
        groups = exercise.card_groups()
        catalog_size = len(set(groups.values())) if groups is not None else exercise.card_count()
        group_for_key = groups or {}
        new_limit, review_limit = self.limits(profile, exercise=name)
        introduced, reviewed = self.db.conn.execute(
            "SELECT (SELECT COUNT(*) FROM practice_cards WHERE profile_id = ? AND exercise = ? AND introduced_on = ?), "
            "COALESCE((SELECT completed FROM daily_reviews WHERE profile_id = ? AND exercise = ? AND day = ?), 0)",
            (profile, name, today, profile, name, today),
        ).fetchone()
        new_slots = max(0, new_limit - introduced)
        review_slots = max(0, review_limit - reviewed)
        remaining = new_slots if catalog_size is None else catalog_size
        pending: set[str] = set()
        known = set()
        due: dict[str, Question | None] = {}
        rows = self.db.conn.execute(
            "SELECT c.item_key, c.signature, c.payload, c.pending_new, s.due, s.state FROM practice_cards c "
            "LEFT JOIN review_schedules s ON (c.profile_id, c.exercise, c.item_key) = (s.profile_id, s.exercise, s.item_key) "
            "AND s.scheduler = ? WHERE c.profile_id = ? AND c.exercise = ? ORDER BY s.due, c.item_key",
            (mode, profile, name),
        )
        reviews = self._grouped_reviews(rows, groups=groups, mode=mode) if groups is not None else rows
        for row in reviews:
            key = row["item_key"]
            known.add(group_for_key.get(key, key))
            ready = row["due"] is None or row["due"] <= now
            if catalog_size is None and not ready:
                continue
            if row["signature"] == signature and not ready:
                remaining -= 1
                continue
            candidate = batch.prepared.get(key)
            if candidate is None:
                try:
                    candidate = exercise.review_question(
                        Question.from_dict(json.loads(row["payload"])),
                        same_settings=row["signature"] == signature,
                    )
                except (ValueError, TypeError, KeyError):
                    continue
            if candidate is not None and catalog_size is not None:
                remaining -= 1
            if ready:
                due[key] = candidate
                if row["pending_new"]:
                    pending.add(key)

        remaining = max(0, min(remaining, new_slots))
        target = min(remaining, limit) if catalog_size is not None and limit is not None else remaining
        new = [q for key, q in batch.prepared.items() if group_for_key.get(key, key) not in known][:target]
        # A procedural exercise can recognize an old card by generating it again after settings change.
        # Keep that small compatibility sample available even when today's introduction allowance is zero.
        probe = catalog_size is None and any(q is None for q in due.values())
        while len(new) < target or (probe and len(batch.prepared) < DAILY_NEW):
            question = next(batch.stream, None)
            if question is None:
                break
            key = question.item_key()
            if key not in batch.prepared:
                batch.prepared[key] = question
                if group_for_key.get(key, key) not in known and len(new) < target:
                    new.append(question)
                elif key in due:
                    due[key] = question
        reviews_due = [q for key, q in due.items() if key not in pending and q is not None][:review_slots]
        unfinished = [q for key, q in due.items() if key in pending and q is not None]
        count = remaining if catalog_size is not None else len(new)
        return reviews_due, unfinished + new, len(unfinished) + count

    def take(self, exercise: Exercise, *, profile: int, mode: str, now: float) -> Question | None:
        """
        Take the first eligible card, recording a new introduction only when served.

        Parameters
        ----------
        exercise : Exercise
            Exercise being opened or advanced.
        profile : int
            Active profile ID.
        mode : str
            Active calendar scheduler.
        now : float
            Presentation timestamp.

        Returns
        -------
        Question or None
            Next question, or None once the available work is finished.

        Examples
        --------
        >>> from alto.exercises.library import ChordQualities
        >>> db = Database()
        >>> practice = CalendarPractice(db)
        >>> question = practice.take(ChordQualities(), profile=db.add_profile("Ada").id, mode="SM-2", now=1000)
        >>> isinstance(question, Question)
        True
        """
        with self.db.write_transaction():
            due, new, _ = self._available(exercise, profile=profile, mode=mode, now=now, limit=1)
            if due:
                return due[0]
            if not new:
                return None
            question = new[0]
            self.db.conn.execute(
                "INSERT INTO practice_cards VALUES (?, ?, ?, ?, ?, ?, 1) ON CONFLICT DO NOTHING",
                (
                    profile,
                    type(exercise).__name__,
                    question.item_key(),
                    exercise.settings_signature(),
                    json.dumps(question.to_dict()),
                    datetime.fromtimestamp(now).date().isoformat(),
                ),
            )
        return question

    def grade(self, exercise: str, *, profile: int, key: str, mode: str, correct: bool, now: float) -> None:
        """
        Reschedule a card from the first submission to this presentation.

        Parameters
        ----------
        exercise : str
            Exercise class name.
        profile : int
            Active profile ID.
        key : str
            Stable card identity.
        mode : str
            Scheduler selected for this review.
        correct : bool
            Whether the first submission was correct.
        now : float
            Answer timestamp.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> ada = db.add_profile("Ada")
        >>> practice = CalendarPractice(db)
        >>> question = practice.take(NoteNames(), profile=ada.id, mode="SM-2", now=1000)
        >>> practice.grade("NoteNames", profile=ada.id, key=question.item_key(), mode="SM-2", correct=True, now=1002)
        >>> db.conn.execute("SELECT due FROM review_schedules").fetchone()[0]
        87402.0
        """
        with self.db.write_transaction():
            identity = (profile, exercise, key, mode)
            row = self.db.conn.execute(
                "SELECT state FROM review_schedules WHERE (profile_id, exercise, item_key, scheduler) = (?, ?, ?, ?)",
                identity,
            ).fetchone()
            pending = self.db.conn.execute(
                "UPDATE practice_cards SET pending_new = 0 WHERE (profile_id, exercise, item_key) = (?, ?, ?) "
                "AND pending_new = 1",
                (profile, exercise, key),
            ).rowcount
            if not pending:
                self.db.conn.execute(
                    "INSERT INTO daily_reviews VALUES (?, ?, ?, 1) ON CONFLICT DO UPDATE SET completed=completed+1",
                    (profile, exercise, datetime.fromtimestamp(now).date().isoformat()),
                )
            if mode == "FSRS":
                when = datetime.fromtimestamp(now, UTC)
                card = Card.from_json(row[0]) if row else Card(card_id=int(key[:15], 16), due=when)
                card, _ = _FSRS.review_card(card, Rating.Good if correct else Rating.Again, review_datetime=when)
                due, state = card.due.timestamp(), card.to_json()
            else:
                repetitions, interval, ease = json.loads(row[0]) if row else (0, 0, 2.5)
                if correct:
                    interval = (1, 6)[repetitions] if repetitions < 2 else math.ceil(interval * ease)
                    repetitions += 1
                else:
                    repetitions, interval = 0, 0
                    ease = max(1.3, ease - 0.32)  # SM-2 grade 2. Grade 4 leaves ease unchanged.
                due, state = now + _sm2_delay(interval), json.dumps([repetitions, interval, ease])
            self.db.conn.execute(
                "INSERT INTO review_schedules VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT DO UPDATE "
                "SET due=excluded.due, state=excluded.state",
                (*identity, due, state),
            )
