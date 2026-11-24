"""
Daily exercise queues for SM-2 and FSRS.

The scheduler controls when an introduced card is due. Each exercise
supplies new
questions under its current settings. Counting a prepared question does
not introduce it.
"""

from __future__ import annotations

import json
import math
import random
import sqlite3
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fsrs import Card, Rating, Scheduler

from alto.exercises.base import Exercise, Question
from alto.learning.database import Database
from alto.learning.grading import (
    PASSING,
    Sm2State,
    inherited_state,
    read_fsrs_card,
    review_options,
)

DAILY_NEW = 10
DAILY_REVIEWS = 200
# A stored limit. NULL inherits the profile setting and zero pauses the
# queue.
UNLIMITED = -1
CALENDAR_SCHEDULERS = ("SM-2", "FSRS")
DEFAULT_SCHEDULER = "ASRS"
SCHEDULERS = (DEFAULT_SCHEDULER, "ARTS", *CALENDAR_SCHEDULERS)
_FSRS = Scheduler()


def _sm2_delay(interval: int) -> int:
    """
    Convert a stored SM-2 interval to seconds, including the retry after
    a miss.

    Parameters
    ----------
    interval : int
        Days until review, or zero for a missed card.

    Returns
    -------
    int
        Seconds between the first submission and the next scheduled
        review.

    Examples
    --------
    >>> _sm2_delay(0), _sm2_delay(1)
    (60, 86400)
    """
    return interval * 86400 if interval else 60


@dataclass
class _Batch:
    """
    One exercise's candidate stream for the current profile, settings
    and local day.

    Examples
    --------
    >>> batch = _Batch("today", iter(()), {})
    >>> batch.prepared
    {}
    """

    seed: str
    stream: Iterator[Question]
    prepared: dict[str, Question]


@dataclass
class _Available:
    """
    Cards and counts for one filtered exercise queue.

    Examples
    --------
    >>> _Available([], [], 0, 0, None).incorrect
    0
    """

    due: list[Question]
    new: list[Question]
    new_count: int
    incorrect: int
    retry_at: float | None
    current_queue: str | None = None


@dataclass(frozen=True)
class ReviewInterval:
    """
    A preview of one rating for a card in its current scheduling state.

    Examples
    --------
    >>> ReviewInterval(
    ...     600,
    ...     (1, "NoteNames", "abc", "FSRS"),
    ...     None,
    ... ).seconds
    600
    """

    seconds: int
    identity: tuple[int, str, str, str]
    previous_state: str | None
    rating: Rating = Rating.Good
    graded_state: str | None = None
    previous_due: float | None = None

    @property
    def duration(self) -> str:
        """
        Format a review interval for display above a grade button or
        beside the music.

        Returns
        -------
        str
            A whole-day interval or a short learning step in minutes and
            seconds.

        Examples
        --------
        >>> ReviewInterval(
        ...     330,
        ...     (1, "NoteNames", "abc", "FSRS"),
        ...     None,
        ... ).duration
        '5 min 30 s'
        """
        days, remainder = divmod(self.seconds, 86400)
        if not remainder:
            return f"{days} day" if days == 1 else f"{days} days"
        minutes, seconds = divmod(self.seconds, 60)
        return f"{minutes} min {seconds} s" if seconds else f"{minutes} min"


def _next_review(
    key: str,
    *,
    mode: str,
    previous: str | None,
    rating: Rating,
    now: float,
    preview_seconds: int | None = None,
) -> tuple[int, str]:
    """
    Calculate the delay and updated card state for a review.

    Parameters
    ----------
    key : str
        Card identity.
    mode : str
        Calendar scheduler.
    previous : str or None
        Serialized schedule before grading.
    rating : Rating
        Grade for the first answer.
    now : float
        Timestamp of the review.
    preview_seconds : int or None
        FSRS interval already drawn for this correct answer, including
        random variation.

    Returns
    -------
    tuple of int and str
        Delay in seconds and serialized schedule.

    Examples
    --------
    >>> _next_review(
    ...     "abc",
    ...     mode="SM-2",
    ...     previous=None,
    ...     rating=Rating.Good,
    ...     now=1000,
    ... )[0]
    86400
    """
    if mode == "FSRS":
        when = datetime.fromtimestamp(now, UTC)
        card = read_fsrs_card(key, previous=previous, due=when)
        card, _ = _FSRS.review_card(card, rating, review_datetime=when)
        if preview_seconds is not None:
            card.due = when + timedelta(seconds=preview_seconds)
        return round((card.due - when).total_seconds()), card.to_json()
    card = Sm2State.read(previous)
    repetitions, interval, ease = card.repetitions, card.interval, card.ease
    if rating == Rating.Good:
        interval = (
            (1, 6)[repetitions]
            if repetitions < 2
            else math.ceil(interval * ease)
        )
        repetitions += 1
    else:
        repetitions, interval, ease = 0, 0, max(1.3, ease - 0.32)
    return _sm2_delay(interval), json.dumps([repetitions, interval, ease])


class CalendarPractice:
    """
    Prepare daily exercise queues and store each scheduler's review
    dates.

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

    def inherit_schedules(self, profile: int, *, mode: str) -> None:
        """
        Initialize missing schedules for this profile from the other
        calendar scheduler.

        Parameters
        ----------
        profile : int
            Profile entering calendar practice.
        mode : str
            Selected scheduler. Adaptive practice uses no calendar
            schedules.

        Examples
        --------
        Switching to FSRS carries over an SM-2 due date without
        consuming a review.
        """
        if mode not in CALENDAR_SCHEDULERS:
            return
        source = "FSRS" if mode == "SM-2" else "SM-2"
        with self.db.write_transaction():
            rows = self.db.conn.execute(
                "SELECT exercise, item_key, state, due, last_rating FROM "
                "review_schedules s "
                "WHERE profile_id=? AND scheduler=? AND NOT EXISTS (SELECT "
                "1 FROM review_schedules d "
                "WHERE (d.profile_id,d.exercise,d.item_key,d.scheduler)=(s."
                "profile_id,s.exercise,s.item_key,?))",
                (profile, source, mode),
            )
            for row in rows.fetchall():
                key, due, rating = (
                    row["item_key"],
                    row["due"],
                    Rating(row["last_rating"]),
                )
                state = inherited_state(
                    key,
                    source=source,
                    state=row["state"],
                    due=due,
                    rating=rating,
                )
                self.db.conn.execute(
                    "INSERT INTO review_schedules (profile_id, exercise, "
                    "item_key, scheduler, due, state, last_rating) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (profile, row["exercise"], key, mode, due, state, rating),
                )

    def limits(self, profile: int, *, exercise: str = "") -> tuple[int, int]:
        """
        Return the effective daily new-card and review limits.

        Parameters
        ----------
        profile : int
            Profile whose settings to read.
        exercise : str
            Exercise class name, or an empty string for profile
            defaults.

        Returns
        -------
        tuple of int and int
            New cards and completed reviews allowed per exercise per
            local day. UNLIMITED removes the cap.

        Examples
        --------
        >>> CalendarPractice(Database()).limits(1)
        (10, 200)
        """
        new, reviews = DAILY_NEW, DAILY_REVIEWS
        for row in self.db.conn.execute(
            (
                "SELECT new_cards, reviews FROM practice_limits WHERE "
                "profile_id = ? AND exercise IN ('', ?) ORDER BY exercise"
            ),
            (profile, exercise),
        ):
            new = new if row[0] is None else row[0]
            reviews = reviews if row[1] is None else row[1]
        return new, reviews

    def overrides(
        self,
        profile: int,
        *,
        exercise: str,
    ) -> tuple[int | None, int | None]:
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
            A number for each override, or None for each inherited
            value.

        Examples
        --------
        >>> CalendarPractice(Database()).overrides(
        ...     1, exercise="NoteNames"
        ... )
        (None, None)
        """
        row = self.db.conn.execute(
            (
                "SELECT new_cards, reviews FROM practice_limits WHERE "
                "profile_id = ? AND exercise = ?"
            ),
            (profile, exercise),
        ).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def set_limits(
        self,
        profile: int,
        *,
        exercise: str = "",
        new_cards: int | None,
        reviews: int | None,
    ) -> None:
        """
        Save the profile defaults or an exercise's individual overrides.

        Parameters
        ----------
        profile : int
            Active profile.
        exercise : str
            Exercise class name, or an empty string for the profile
            defaults.
        new_cards : int or None
            Daily introductions, UNLIMITED for no cap, or None to
            inherit.
        reviews : int or None
            Daily reviews, UNLIMITED for no cap, or None to inherit.

        Examples
        --------
        >>> db = Database()
        >>> practice = CalendarPractice(db)
        >>> profile = db.add_profile("Ada").id
        >>> practice.set_limits(
        ...     profile, new_cards=5, reviews=30
        ... )
        >>> practice.limits(
        ...     profile, exercise="NoteNames"
        ... )
        (5, 30)
        """
        with self.db.write_transaction():
            self.db.conn.execute(
                "INSERT INTO practice_limits VALUES (?, ?, ?, ?) ON "
                "CONFLICT DO UPDATE "
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
        Restoring defaults keeps the day's introductions and completed
        reviews.
        """
        with self.db.write_transaction():
            self.db.conn.execute(
                "DELETE FROM practice_limits WHERE profile_id = ?",
                (profile,),
            )

    def queue(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
    ) -> tuple[list[Question], list[Question]]:
        """
        Find due reviews and prepare the remaining new cards for this
        local day.

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
            Due reviews, oldest first, and new questions available for
            introduction.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> ada = db.add_profile("Ada")
        >>> due, new = CalendarPractice(db).queue(
        ...     NoteNames(),
        ...     profile=ada.id,
        ...     mode="FSRS",
        ...     now=1000,
        ... )
        >>> not due and len(new) == DAILY_NEW
        True
        """
        available = self._available(
            exercise,
            profile=profile,
            mode=mode,
            now=now,
            limit=None,
        )
        return available.due, available.new

    def counts(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
    ) -> tuple[int, int]:
        """
        Count due reviews and unseen cards available with the selected
        settings.

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
            Due and new counts. Exact catalogs can be counted without
            rendering their cards.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> CalendarPractice(db).counts(
        ...     NoteNames(),
        ...     profile=db.add_profile("Ada").id,
        ...     mode="SM-2",
        ...     now=100,
        ... )[1] > 0
        True
        """
        due, new, _ = self.tile_counts(
            exercise,
            profile=profile,
            mode=mode,
            now=now,
        )
        return due, new

    def tile_counts(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
    ) -> tuple[int, int, int]:
        """
        Count available reviews, new cards, and missed cards awaiting a
        correct review.

        Parameters
        ----------
        exercise : Exercise
            Exercise with the current settings.
        profile : int
            Active profile ID.
        mode : str
            Active calendar scheduler.
        now : float
            Current timestamp.

        Returns
        -------
        tuple of int, int, int
            Due reviews, available new cards, and outstanding incorrect
            cards. A due retry counts in both review totals.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> CalendarPractice(db).tile_counts(
        ...     NoteNames(),
        ...     profile=db.add_profile("Ada").id,
        ...     mode="SM-2",
        ...     now=100,
        ... )[2]
        0
        """
        return self.study_counts(
            exercise,
            profile=profile,
            mode=mode,
            now=now,
        )[0]

    def study_counts(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
        current_key: str | None = None,
    ) -> tuple[tuple[int, int, int], str | None]:
        """
        Count the exercise queues and identify the queue of the question
        on screen.

        Parameters
        ----------
        exercise : Exercise
            Exercise with the current settings.
        profile : int
            Active profile ID.
        mode : str
            Active calendar scheduler.
        now : float
            Current timestamp.
        current_key : str or None
            Item key of the question awaiting an answer.

        Returns
        -------
        tuple
            The same review, new, and incorrect counts as the tiles,
            plus the current queue if a question is active.

        Examples
        --------
        A missed card that comes due again is underlined as incorrect
        during its retry.
        """
        available = self._available(
            exercise,
            profile=profile,
            mode=mode,
            now=now,
            limit=0,
            current_key=current_key,
        )
        return (
            len(available.due),
            available.new_count,
            available.incorrect,
        ), available.current_queue

    @staticmethod
    def _grouped_reviews(
        rows: Iterable[sqlite3.Row],
        *,
        groups: dict[str, str],
        mode: str,
    ) -> list[sqlite3.Row]:
        """
        Keep the most recently graded example of each eligible skill, in
        due order.

        Parameters
        ----------
        rows : iterable of sqlite3.Row
            Introduced examples in due order, including examples without
            a grade.
        groups : dict of str to str
            Eligible example keys and their shared skills.
        mode : str
            Scheduler whose saved state supplies the last review time.

        Returns
        -------
        list of sqlite3.Row
            One representative per introduced skill. Its existing
            schedule applies to the entire group.

        Examples
        --------
        Several previously graded Vertical turn examples contribute one
        review date.
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
                    reviewed = datetime.fromisoformat(
                        state["last_review"],
                    ).timestamp()
                else:
                    reviewed = row["due"] - (
                        state["delay"]
                        if isinstance(state, dict)
                        else _sm2_delay(state[1])
                    )
            if group not in latest or reviewed > latest[group][0]:
                latest[group] = reviewed, row
        return sorted(
            (row for _, row in latest.values()),
            key=lambda row: (
                row["due"] is not None,
                row["due"],
                row["item_key"],
            ),
        )

    def _available(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
        limit: int | None,
        avoid: str | None = None,
        current_key: str | None = None,
        wait_learning: bool = False,
    ) -> _Available:
        """
        Match introduced cards against the active catalog and prepare
        the requested new questions.

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
            Maximum new cards to render from an exact catalog. None
            requests them all.
        avoid : str or None
            Put this just-shown card behind other due reviews before
            applying the daily limit.
        current_key : str or None
            Identify which count includes the active question.
        wait_learning : bool
            Wake the exercise for successful learning steps as well as
            missed cards.

        Returns
        -------
        _Available
            Filtered queues, tile counts when counting, and the next
            eligible retry time when drawing a card.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> CalendarPractice(db)._available(
        ...     NoteNames(),
        ...     profile=1,
        ...     mode="SM-2",
        ...     now=100,
        ...     limit=0,
        ... ).new
        []
        """
        name = type(exercise).__name__
        signature = exercise.settings_signature()
        today = datetime.fromtimestamp(now).date().isoformat()
        seed = json.dumps([today, profile, name, signature])
        batch = self._batches.get(name)
        if batch is None or batch.seed != seed:
            batch = self._batches[name] = _Batch(
                seed,
                exercise.daily_candidates(random.Random(seed)),
                {},
            )
        groups = exercise.card_groups()
        catalog_size = (
            len(set(groups.values()))
            if groups is not None
            else exercise.card_count()
        )
        group_for_key = groups or {}
        new_limit, review_limit = self.limits(profile, exercise=name)
        introduced, reviewed = self.db.conn.execute(
            "SELECT (SELECT COUNT(*) FROM practice_cards WHERE profile_id ="
            " ? AND exercise = ? AND introduced_on = ?), "
            "COALESCE((SELECT completed FROM daily_reviews WHERE profile_id"
            " = ? AND exercise = ? AND day = ?), 0)",
            (profile, name, today, profile, name, today),
        ).fetchone()
        if new_limit == UNLIMITED:
            # Count exact catalogs in full. Procedural catalogs refill
            # this sample on each draw.
            new_slots = DAILY_NEW if catalog_size is None else catalog_size
        else:
            new_slots = max(0, new_limit - introduced)
        review_slots = (
            None
            if review_limit == UNLIMITED
            else max(0, review_limit - reviewed)
        )
        remaining = new_slots if catalog_size is None else catalog_size
        pending: set[str] = set()
        known = set()
        due: dict[str, Question | None] = {}
        retries: dict[str, float] = {}
        unrecognized_retries: set[str] = set()
        rows = self.db.conn.execute(
            "SELECT c.item_key, c.signature, c.payload, c.pending_new, "
            "s.due, s.state, s.last_rating FROM practice_cards c "
            "LEFT JOIN review_schedules s ON (c.profile_id, c.exercise, "
            "c.item_key) = (s.profile_id, s.exercise, s.item_key) "
            "AND s.scheduler = ? WHERE c.profile_id = ? AND c.exercise = ? "
            "ORDER BY s.due, c.item_key",
            (mode, profile, name),
        )
        reviews = (
            self._grouped_reviews(rows, groups=groups, mode=mode)
            if groups is not None
            else rows
        )
        for row in reviews:
            key = row["item_key"]
            known.add(group_for_key.get(key, key))
            ready = row["due"] is None or row["due"] <= now
            if row["last_rating"] == Rating.Again and (
                limit == 0 or (not ready and limit == 1 and review_slots != 0)
            ):
                retries[key] = row["due"]
            if wait_learning and not ready and review_slots != 0:
                state = json.loads(row["state"])
                if isinstance(state, dict) and (
                    state.get("phase") in ("learning", "relearning")
                    or (mode == "FSRS" and state.get("step") is not None)
                ):
                    retries[key] = row["due"]
            if not ready:
                if row["signature"] == signature:
                    if catalog_size is not None:
                        remaining -= 1
                    continue
                if catalog_size is None and key not in retries:
                    continue
            candidate = batch.prepared.get(key)
            if candidate is None:
                try:
                    candidate = exercise.review_question(
                        Question.from_dict(json.loads(row["payload"])),
                        same_settings=row["signature"] == signature,
                    )
                except (ValueError, TypeError, KeyError):
                    retries.pop(key, None)
                    continue
            if candidate is not None and catalog_size is not None:
                remaining -= 1
            if ready:
                due[key] = candidate
                if row["pending_new"]:
                    pending.add(key)
            elif key in retries and candidate is None:
                unrecognized_retries.add(key)

        remaining = max(0, min(remaining, new_slots))
        target = (
            min(remaining, limit)
            if catalog_size is not None and limit is not None
            else remaining
        )
        new = [
            q
            for key, q in batch.prepared.items()
            if group_for_key.get(key, key) not in known
        ][:target]
        # A procedural exercise can recognize an old card by generating
        # it again after settings change.
        # Keep that small compatibility sample available even when
        # today's introduction allowance is zero.
        probe = catalog_size is None and (
            bool(unrecognized_retries) or any(q is None for q in due.values())
        )
        while len(new) < target or (probe and len(batch.prepared) < DAILY_NEW):
            question = next(batch.stream, None)
            if question is None:
                break
            key = question.item_key()
            if key not in batch.prepared:
                batch.prepared[key] = question
                if (
                    group_for_key.get(key, key) not in known
                    and len(new) < target
                ):
                    new.append(question)
                elif key in due:
                    due[key] = question
        if avoid is not None and avoid in due:
            due[avoid] = due.pop(avoid)
        reviews_due = [
            q for key, q in due.items() if key not in pending and q is not None
        ][:review_slots]
        unfinished = [
            q for key, q in due.items() if key in pending and q is not None
        ]
        count = remaining if catalog_size is not None else len(new)
        for key in unrecognized_retries.difference(batch.prepared):
            del retries[key]
        incorrect = sum(
            key not in due or due[key] is not None for key in retries
        )
        retry_at = next(
            (when for when in retries.values() if when > now),
            None,
        )
        current_queue = None
        if current_key in pending:
            current_queue = "new"
        elif current_key in retries:
            current_queue = "incorrect"
        elif current_key in due:
            current_queue = "review"
        return _Available(
            reviews_due,
            unfinished + new,
            len(unfinished) + count,
            incorrect,
            retry_at,
            current_queue,
        )

    def take(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
    ) -> Question | None:
        """
        Take the first eligible card, recording a new introduction only
        when served.

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
        >>> from alto.exercises.library import (
        ...     ChordQualities,
        ... )
        >>> db = Database()
        >>> practice = CalendarPractice(db)
        >>> question = practice.take(
        ...     ChordQualities(),
        ...     profile=db.add_profile("Ada").id,
        ...     mode="SM-2",
        ...     now=1000,
        ... )
        >>> isinstance(question, Question)
        True
        """
        return self.take_or_wait(
            exercise,
            profile=profile,
            mode=mode,
            now=now,
        )[0]

    def take_or_wait(
        self,
        exercise: Exercise,
        *,
        profile: int,
        mode: str,
        now: float,
        avoid: str | None = None,
        wait_learning: bool = False,
    ) -> tuple[Question | None, float | None]:
        """
        Draw an eligible card or return the time when a missed card can
        be reviewed.

        Parameters
        ----------
        exercise : Exercise
            Exercise with the current settings.
        profile : int
            Active profile ID.
        mode : str
            Active calendar scheduler.
        now : float
            Presentation timestamp.
        avoid : str or None
            Prefer another available card to the one just shown.
        wait_learning : bool
            Also wake the exercise when a correctly answered learning
            card comes due.

        Returns
        -------
        tuple
            The next question and, when the queue is waiting for a
            retry, its due timestamp.

        Examples
        --------
        A single missed card can wake the exercise when its learning
        step expires.
        """
        with self.db.write_transaction():
            available = self._available(
                exercise,
                profile=profile,
                mode=mode,
                now=now,
                limit=1,
                avoid=avoid,
                wait_learning=wait_learning,
            )
            due, new = available.due, available.new
            if due and (due[0].item_key() != avoid or not new):
                return due[0], None
            if not new:
                return None, available.retry_at
            question = new[0]
            self.introduce(
                exercise,
                profile=profile,
                question=question,
                now=now,
            )
        return question, None

    def introduce(
        self,
        exercise: Exercise,
        *,
        profile: int,
        question: Question,
        now: float,
    ) -> None:
        """
        Register a calendar introduction once, in the caller's draw or
        answer transaction.

        Parameters
        ----------
        exercise : Exercise
            Exercise that supplied this question.
        profile : int
            Practicing profile.
        question : Question
            New or previously introduced question.
        now : float
            Time of introduction.

        Examples
        --------
        Answering a pending card keeps its original introduction day.
        """
        self.db.conn.execute(
            "INSERT INTO practice_cards (profile_id, exercise, item_key, "
            "signature, payload, introduced_on, pending_new) "
            "VALUES (?, ?, ?, ?, ?, ?, 1) ON CONFLICT DO NOTHING",
            (
                profile,
                type(exercise).__name__,
                question.item_key(),
                exercise.settings_signature(),
                json.dumps(question.to_dict()),
                datetime.fromtimestamp(now).date().isoformat(),
            ),
        )

    def _review_schedule(
        self,
        identity: tuple[int, str, str, str],
    ) -> tuple[str | None, float | None]:
        """
        Read the card's current schedule.

        Parameters
        ----------
        identity : tuple
            Profile, exercise, card key and scheduler.

        Returns
        -------
        tuple
            Serialized state and due timestamp, both absent before the
            first review.

        Examples
        --------
        >>> CalendarPractice(
        ...     Database()
        ... )._review_schedule(
        ...     (1, "NoteNames", "abc", "FSRS")
        ... )
        (None, None)
        """
        row = self.db.conn.execute(
            (
                "SELECT state, due FROM review_schedules WHERE "
                "(profile_id, exercise, item_key, scheduler) = (?, ?, ?, "
                "?)"
            ),
            identity,
        ).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def correct_interval(
        self,
        exercise: str,
        *,
        profile: int,
        key: str,
        mode: str,
        now: float,
    ) -> ReviewInterval:
        """
        Preview the next correct answer without grading the card.

        Parameters
        ----------
        exercise : str
            Exercise class name.
        profile : int
            Active profile ID.
        key : str
            Card identity.
        mode : str
            Calendar scheduler.
        now : float
            Presentation timestamp.

        Returns
        -------
        ReviewInterval
            Delay to display and reuse when the answer is submitted.

        Examples
        --------
        >>> CalendarPractice(
        ...     Database()
        ... ).correct_interval(
        ...     "NoteNames",
        ...     profile=1,
        ...     key="abc",
        ...     mode="FSRS",
        ...     now=1000,
        ... ).seconds
        600
        """
        identity = (profile, exercise, key, mode)
        previous, _ = self._review_schedule(identity)
        seconds, _ = _next_review(
            key,
            mode=mode,
            previous=previous,
            rating=Rating.Good,
            now=now,
        )
        return ReviewInterval(seconds, identity, previous)

    def passing_intervals(
        self,
        exercise: str,
        *,
        profile: int,
        key: str,
        mode: str,
        now: float,
        displayed: dict[Rating, ReviewInterval] | None = None,
    ) -> dict[Rating, ReviewInterval]:
        """
        Preview the three passing outcomes from one snapshot of this
        card.

        Parameters
        ----------
        exercise : str
            Exercise class name.
        profile : int
            Active profile.
        key : str
            Card identity.
        mode : str
            Calendar scheduler.
        now : float
            Presentation or answer timestamp.
        displayed : dict or None
            Previously displayed outcomes to reuse while this card's
            schedule is current.

        Returns
        -------
        dict
            Passing grades and their previews, including the state to
            save.

        Examples
        --------
        >>> practice = CalendarPractice(Database())
        >>> practice.passing_intervals(
        ...     "NoteNames",
        ...     profile=1,
        ...     key="abc",
        ...     mode="SM-2",
        ...     now=0,
        ... )[Rating.Good].seconds
        600
        """
        identity = (profile, exercise, key, mode)
        previous, due = self._review_schedule(identity)
        if displayed and all(
            (option.identity, option.previous_state, option.previous_due)
            == (identity, previous, due)
            for option in displayed.values()
        ):
            return displayed
        outcomes = review_options(
            key,
            mode=mode,
            previous=previous,
            due=due if due is not None else now,
            now=now,
        )
        return {
            grade: ReviewInterval(
                outcomes[grade][0],
                identity,
                previous,
                grade,
                outcomes[grade][1],
                due,
            )
            for grade in PASSING
        }

    def grade(
        self,
        exercise: str,
        *,
        profile: int,
        key: str,
        mode: str,
        correct: bool,
        now: float,
        manual_rating: Rating | None = None,
        preview: ReviewInterval | None = None,
    ) -> None:
        """
        Reschedule a card from the first submission to this
        presentation.

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
        manual_rating : Rating or None
            Explicit grade from a button or response time. None uses the
            original automatic schedule.
        now : float
            Answer timestamp.
        preview : ReviewInterval or None
            Correct-answer interval shown for this presentation.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> ada = db.add_profile("Ada")
        >>> practice = CalendarPractice(db)
        >>> question = practice.take(
        ...     NoteNames(),
        ...     profile=ada.id,
        ...     mode="SM-2",
        ...     now=1000,
        ... )
        >>> practice.grade(
        ...     "NoteNames",
        ...     profile=ada.id,
        ...     key=question.item_key(),
        ...     mode="SM-2",
        ...     correct=True,
        ...     now=1002,
        ... )
        >>> db.conn.execute(
        ...     "SELECT due FROM review_schedules"
        ... ).fetchone()[0]
        87402.0
        """
        rating = (manual_rating or Rating.Good) if correct else Rating.Again
        with self.db.write_transaction():
            identity = (profile, exercise, key, mode)
            previous, due = self._review_schedule(identity)
            matches = preview is not None and (
                preview.identity,
                preview.previous_state,
                preview.rating,
            ) == (
                identity,
                previous,
                rating,
            )
            if (
                manual_rating is not None
                and preview is not None
                and (not matches or preview.previous_due != due)
            ):
                # Another presentation has already graded the state
                # these buttons described.
                return
            seconds_shown = (
                preview.seconds if preview is not None and matches else None
            )
            pending = self.db.conn.execute(
                "UPDATE practice_cards SET pending_new = 0 WHERE "
                "(profile_id, exercise, item_key) = (?, ?, ?) "
                "AND pending_new = 1",
                (profile, exercise, key),
            ).rowcount
            if not pending:
                self.db.conn.execute(
                    (
                        "INSERT INTO daily_reviews VALUES (?, ?, ?, 1) ON "
                        "CONFLICT DO UPDATE SET completed=completed+1"
                    ),
                    (
                        profile,
                        exercise,
                        datetime.fromtimestamp(now).date().isoformat(),
                    ),
                )
            if manual_rating is None:
                seconds, state = _next_review(
                    key,
                    mode=mode,
                    previous=previous,
                    rating=rating,
                    now=now,
                    preview_seconds=seconds_shown,
                )
            elif preview is not None and preview.graded_state is not None:
                seconds, state = preview.seconds, preview.graded_state
                if mode == "FSRS":
                    card = Card.from_json(state)
                    card.last_review = datetime.fromtimestamp(now, UTC)
                    card.due = card.last_review + timedelta(seconds=seconds)
                    state = card.to_json()
            else:
                # An objective miss takes the Again transition without
                # prompting for a rating.
                seconds, state = review_options(
                    key,
                    mode=mode,
                    previous=previous,
                    due=due if due is not None else now,
                    now=now,
                )[rating]
            self.db.conn.execute(
                "INSERT INTO review_schedules (profile_id, exercise, "
                "item_key, scheduler, due, state, last_rating) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO UPDATE "
                "SET due=excluded.due, state=excluded.state, "
                "last_rating=excluded.last_rating",
                (*identity, now + seconds, state, rating),
            )
