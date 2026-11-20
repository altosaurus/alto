"""
Ties the profile, the database and the scheduler together for the exercise screen.

Examples
--------
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> question = learner.pick(NoteNames(), rng=random.Random(1))
>>> question.answer in question.choices
True
"""

from __future__ import annotations

import json
import random
import time

from fsrs import Rating

from alto.exercises.base import (
    Exercise,
    Question,
)
from alto.learning import scheduler
from alto.learning.calendar import CALENDAR_SCHEDULERS, DEFAULT_SCHEDULER, SCHEDULERS, CalendarPractice, ReviewInterval
from alto.learning.database import (
    Database,
    ItemRecord,
    Profile,
)
from alto.learning.response_times import WINDOW, ResponseTimes

# The database identifier predates the ASRS name and is shared with older backups.
_STORED_ASRS = "Alto"


class PracticeComplete(Exception):
    """
    The current exercise has no scheduled cards available.

    Examples
    --------
    >>> issubclass(PracticeComplete, Exception)
    True
    """

    def __init__(self, retry_at: float | None = None) -> None:
        """
        Carry the next missed card's due time to the exercise screen.

        Parameters
        ----------
        retry_at : float or None
            Scheduled timestamp, or None when practice is finished for now.

        Examples
        --------
        >>> PracticeComplete().retry_at is None
        True
        """
        super().__init__()
        self.retry_at = retry_at


class Learner:
    """
    Chooses what a profile is asked next and records how it was answered.

    Attributes
    ----------
    FRESH : int
        How many new questions are generated for each pick, alongside the ones asked before.
    db : Database
        Where answers and what is known about each question are stored.
    profile : Profile
        Whose answers these are.

    Examples
    --------
    >>> from alto.exercises.library import NoteNames
    >>> db = Database()
    >>> learner = Learner(db, profile=db.add_profile("Ada"))
    >>> rng = random.Random(2)
    >>> question = learner.pick(NoteNames(), rng=rng)
    >>> learner.record(NoteNames(), question=question, answer=question.answer, correct=True, attempt_no=1, seconds=2.5)
    >>> db.count_attempts(learner.profile.id)
    1
    """

    FRESH = 10  # new questions generated for each pick, alongside the ones asked before

    def __init__(
        self,
        db: Database,
        *,
        profile: Profile,
    ) -> None:
        """
        Create a learner for one profile.

        Parameters
        ----------
        db : Database
            The database to read and write.
        profile : Profile
            The profile that is practicing. Keyword-only.

        Examples
        --------
        >>> database = Database()
        >>> learner = Learner(database, profile=database.add_profile("Ada"))
        >>> learner.profile.name
        'Ada'
        """
        self.db = db
        self.set_profile(profile)

    def set_profile(self, profile: Profile) -> None:
        """
        Open a profile's practice queues and resume its selected scheduler.

        Parameters
        ----------
        profile : Profile
            Profile loaded at launch, selected in the app, or restored from backup.

        Examples
        --------
        >>> db = Database()
        >>> learner = Learner(db, profile=db.add_profile("Ada"))
        >>> learner.set_profile(db.add_profile("Ben"))
        >>> learner.profile.name
        'Ben'
        """
        self.profile = profile
        self.calendar = CalendarPractice(self.db)
        self.calendar.inherit_schedules(profile.id, mode=self.mode)

    @property
    def mode(self) -> str:
        """
        Return this profile's question scheduler.

        Returns
        -------
        str
            ASRS, ARTS, SM-2 or FSRS.

        Examples
        --------
        >>> db = Database()
        >>> Learner(db, profile=db.add_profile("Ada")).mode
        'ASRS'
        """
        stored = self.db.conn.execute("SELECT scheduler FROM profiles WHERE id = ?", (self.profile.id,)).fetchone()[0]
        return DEFAULT_SCHEDULER if stored == _STORED_ASRS else stored

    @property
    def self_grading(self) -> bool:
        """
        Read the profile's SM-2 and FSRS grading preference.

        Returns
        -------
        bool
            Whether a correct answer waits for a grade.

        Examples
        --------
        >>> db = Database()
        >>> Learner(db, profile=db.add_profile("Ada")).self_grading
        False
        """
        return bool(self.db.conn.execute("SELECT self_grading FROM profiles WHERE id = ?", (self.profile.id,)).fetchone()[0])

    def response_times(self, exercise: str) -> ResponseTimes:
        """
        Read the rolling sample for one exercise and the current profile's thresholds.

        Parameters
        ----------
        exercise : str
            Registered exercise class name.

        Returns
        -------
        ResponseTimes
            Up to 100 recent, uninterrupted, correct first answers across practice modes.

        Examples
        --------
        >>> db = Database()
        >>> Learner(db, profile=db.add_profile("Ada")).response_times("KeyboardNotes").times
        ()
        """
        easy, hard = self.db.conn.execute(
            "SELECT easy_percent, hard_percent FROM profiles WHERE id=?",
            (self.profile.id,),
        ).fetchone()
        rows = self.db.conn.execute(
            "SELECT duration_ms FROM attempts WHERE profile_id=? AND exercise=? AND attempt_no=1 AND correct=1 "
            "AND duration_ms>0 AND timing_valid=1 ORDER BY answered_at DESC, id DESC LIMIT ?",
            (self.profile.id, exercise, WINDOW),
        )
        return ResponseTimes(tuple(sorted(row[0] for row in rows)), easy, hard)

    def set_speed_thresholds(self, *, easy: int, hard: int) -> None:
        """
        Save the two tail percentages for this profile.

        Parameters
        ----------
        easy : int
            Percentage of fastest correct answers.
        hard : int
            Percentage of slowest correct answers.

        Raises
        ------
        ValueError
            If the bands overlap or a percentage is negative.

        Examples
        --------
        Setting both tails to zero assigns Good to every correct first answer.
        """
        if min(easy, hard) < 0 or easy + hard > 100:
            raise ValueError("The two percentages must be nonnegative and total at most 100.")
        with self.db.write_transaction():
            self.db.conn.execute("UPDATE profiles SET easy_percent=?, hard_percent=? WHERE id=?", (easy, hard, self.profile.id))

    def set_self_grading(self, enabled: bool) -> None:
        """
        Choose how this profile grades correct calendar reviews.

        Parameters
        ----------
        enabled : bool
            Show Hard, Good, and Easy after a correct answer.

        Examples
        --------
        >>> db = Database()
        >>> learner = Learner(db, profile=db.add_profile("Ada"))
        >>> learner.set_self_grading(True)
        >>> learner.self_grading
        True
        """
        with self.db.conn:
            self.db.conn.execute("UPDATE profiles SET self_grading = ? WHERE id = ?", (enabled, self.profile.id))

    def set_mode(self, mode: str) -> None:
        """
        Select the question scheduler for this profile.

        Parameters
        ----------
        mode : str
            Scheduler name.

        Raises
        ------
        ValueError
            For an unsupported scheduler.

        Examples
        --------
        >>> db = Database()
        >>> learner = Learner(db, profile=db.add_profile("Ada"))
        >>> learner.set_mode("FSRS")
        >>> learner.mode
        'FSRS'
        """
        if mode != _STORED_ASRS and mode not in SCHEDULERS:
            raise ValueError(f"Unknown question scheduler: {mode}")
        stored = _STORED_ASRS if mode == DEFAULT_SCHEDULER else mode
        with self.db.write_transaction():
            self.calendar.inherit_schedules(self.profile.id, mode=mode)
            self.db.conn.execute("UPDATE profiles SET scheduler = ? WHERE id = ?", (stored, self.profile.id))

    def pick(
        self,
        exercise: Exercise,
        *,
        rng: random.Random,
        avoid: str | None = None,
        now: float | None = None,
    ) -> Question:
        """
        Return the next eligible question using the profile's selected scheduler.

        Parameters
        ----------
        exercise : Exercise
            The exercise being practiced.
        rng : random.Random
            The random number generator used to make new questions and to draw one. Keyword-only.
        avoid : str or None, default None
            The `item_key` of the question just asked, so it does not come straight back. Keyword-only.
        now : float or None, default None
            The current time as a timestamp; the clock is used if None. Keyword-only.

        Returns
        -------
        Question
            The question to ask.

        Raises
        ------
        PracticeComplete
            If the calendar scheduler has no cards currently available.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> learner = Learner(db, profile=db.add_profile("Ada"))
        >>> first = learner.pick(NoteNames(), rng=random.Random(3))
        >>> second = learner.pick(NoteNames(), rng=random.Random(3), avoid=first.item_key())
        >>> second.item_key() != first.item_key()
        True
        """
        now = time.time() if now is None else now
        mode = self.mode
        if mode == "ARTS":
            return self._pick_arts(exercise, rng=rng, avoid=avoid)
        if mode in CALENDAR_SCHEDULERS:
            card, retry_at = self.calendar.take_or_wait(
                exercise,
                profile=self.profile.id,
                mode=mode,
                now=now,
                avoid=avoid,
                wait_learning=self.self_grading or self.response_times(type(exercise).__name__).ready,
            )
            if card is None:
                raise PracticeComplete(retry_at)
            return card
        name = type(exercise).__name__
        options: dict[str, tuple[Question, float]] = {}
        for _ in range(self.FRESH):
            q = exercise.generate(rng)
            key = q.item_key()
            if key in options or key == avoid:
                continue
            item = self.db.get_item(self.profile.id, exercise=name, item_key=key)
            options[key] = (
                q,
                scheduler.weight(item.strain if item else None, last_seen=item.last_seen if item else None, now=now),
            )
        for item in self.db.replay_candidates(self.profile.id, exercise=name, signature=exercise.settings_signature()):
            if item.item_key in options or item.item_key == avoid:
                continue
            try:
                q = exercise.refresh(Question.from_dict(json.loads(item.payload)))
            except (ValueError, KeyError, TypeError):
                continue
            options[item.item_key] = (q, scheduler.weight(item.strain, last_seen=item.last_seen, now=now))
        if not options:  # every candidate was the question to avoid
            return exercise.generate(rng)
        questions, weights = zip(*options.values())
        return scheduler.choose(questions, weights=weights, rng=rng)

    def _pick_arts(self, exercise: Exercise, *, rng: random.Random, avoid: str | None) -> Question:
        """
        Choose the highest-priority eligible question, breaking ties at random.

        Parameters
        ----------
        exercise : Exercise
            Exercise with the learner's current settings.
        rng : random.Random
            Source for new questions and tied priorities.
        avoid : str or None
            Last presented question, skipped when another is available.

        Returns
        -------
        Question
            A fresh question or a saved example selected by ARTS.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> learner = Learner(db, profile=db.add_profile("Ada"))
        >>> bool(learner._pick_arts(NoteNames(), rng=random.Random(1), avoid=None).answer)
        True
        """
        fresh = {q.item_key(): q for q in (exercise.generate(rng) for _ in range(self.FRESH))}
        priorities = dict.fromkeys(fresh, 1.0)
        name = type(exercise).__name__
        signature = exercise.settings_signature()
        # Rank first submissions within this exercise. SQLite takes the answer columns from
        # the row with the minimum gap, which is unique and is the item's latest trial.
        rows = self.db.conn.execute(
            "WITH trials AS (SELECT item_key, correct, duration_ms, ROW_NUMBER() OVER (ORDER BY id DESC) - 1 AS gap "
            "FROM attempts WHERE profile_id = ? AND exercise = ? AND attempt_no = 1), "
            "latest AS (SELECT item_key, correct, duration_ms, MIN(gap) AS intervening FROM trials GROUP BY item_key) "
            "SELECT latest.*, i.signature FROM latest JOIN items i ON i.item_key = latest.item_key "
            "WHERE i.profile_id = ? AND i.exercise = ?",
            (self.profile.id, name, self.profile.id, name),
        )
        for row in rows:
            key = row["item_key"]
            if key in fresh or row["signature"] == signature:
                priorities[key] = scheduler.arts_priority(
                    row["intervening"],
                    correct=row["correct"],
                    duration_ms=row["duration_ms"],
                )
        if avoid is not None:
            priorities.pop(avoid, None)
        while priorities:
            highest = max(priorities.values())
            key = rng.choice([key for key, score in priorities.items() if score == highest])
            if key in fresh:
                return fresh[key]
            item = self.db.get_item(self.profile.id, exercise=name, item_key=key)
            if item is not None:
                try:
                    return exercise.refresh(Question.from_dict(json.loads(item.payload)))
                except (ValueError, KeyError, TypeError):
                    pass
            del priorities[key]
        return rng.choice(list(fresh.values()))

    def record(
        self,
        exercise: Exercise,
        *,
        question: Question,
        answer: str,
        correct: bool,
        attempt_no: int,
        seconds: float,
        now: float | None = None,
        preview: ReviewInterval | None = None,
        passing_previews: dict[Rating, ReviewInterval] | None = None,
        self_grading: bool = False,
        timing_valid: bool = True,
    ) -> ReviewInterval | None:
        """
        Log one answer and update what is known about the question.

        Parameters
        ----------
        exercise : Exercise
            The exercise being practiced.
        question : Question
            The question that was answered. Keyword-only.
        answer : str
            What was answered. Keyword-only.
        correct : bool
            Whether the answer was right. Keyword-only.
        attempt_no : int
            1 for the first answer to this showing of the question, 2 for the second and so on. Keyword-only.
        seconds : float
            How long the answer took. Keyword-only.
        now : float or None, default None
            When it was answered, as a timestamp; the clock is used if None. Keyword-only.
        preview : ReviewInterval or None
            Correct-answer interval displayed for this question.
        passing_previews : dict or None
            Hard, Good, and Easy intervals shown during speed grading.
        self_grading : bool
            Defer scheduling a correct calendar answer until the learner rates it.

        timing_valid : bool
            Whether the presentation was uninterrupted. False excludes it from timing.

        Returns
        -------
        ReviewInterval or None
            The interval chosen by speed grading, once enough earlier answers exist.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> db = Database()
        >>> learner = Learner(db, profile=db.add_profile("Ada"))
        >>> q = learner.pick(NoteNames(), rng=random.Random(4))
        >>> learner.record(NoteNames(), question=q, answer="?", correct=False, attempt_no=1, seconds=3.0)
        >>> learner.record(NoteNames(), question=q, answer=q.answer, correct=True, attempt_no=2, seconds=1.0)
        >>> [row["correct"] for row in db.attempts(learner.profile.id)]
        [0, 1]
        >>> # noinspection PyUnresolvedReferences
        >>> db.get_item(learner.profile.id, exercise="NoteNames", item_key=q.item_key()).wrong_attempts
        1
        """
        now = time.time() if now is None else now
        name, key = type(exercise).__name__, question.item_key()
        assigned = None
        with self.db.write_transaction():
            mode = self.mode
            first = attempt_no == 1
            duration = round(seconds * 1000)
            rating = Rating.Again if self_grading else None
            if first and mode in CALENDAR_SCHEDULERS and not self_grading:
                sample = self.response_times(name)
                if sample.ready:
                    rating = sample.grade(duration if timing_valid else 0) if correct else Rating.Again
                    if correct:
                        assigned = self.calendar.passing_intervals(
                            name,
                            profile=self.profile.id,
                            key=key,
                            mode=mode,
                            now=now,
                            displayed=passing_previews,
                        )[rating]
                    preview = assigned
            self.db.add_attempt(
                self.profile.id,
                exercise=name,
                item_key=key,
                attempt_no=attempt_no,
                answer=answer,
                correct=correct,
                duration_ms=duration,
                timing_valid=timing_valid,
                answered_at=now,
            )
            old = self.db.get_item(self.profile.id, exercise=name, item_key=key)
            strain = old.strain if old else scheduler.NEW_STRAIN
            strain = scheduler.update_strain(
                strain,
                correct=correct,
                attempt_no=attempt_no,
                seconds=seconds,
                par_seconds=exercise.par_seconds,
            )
            self.db.save_item(
                self.profile.id,
                exercise=name,
                item_key=key,
                item=ItemRecord(
                    strain=strain,
                    seen=(old.seen if old else 0) + (1 if first else 0),
                    first_try_right=(old.first_try_right if old else 0) + (1 if first and correct else 0),
                    wrong_attempts=(old.wrong_attempts if old else 0) + (0 if correct else 1),
                    total_first_ms=(old.total_first_ms if old else 0) + (round(seconds * 1000) if first else 0),
                    last_seen=now,
                    signature=exercise.settings_signature(),
                    payload=json.dumps(question.to_dict()),
                ),
            )
            if first and mode in CALENDAR_SCHEDULERS:
                self.calendar.introduce(exercise, profile=self.profile.id, question=question, now=now)
                if not (correct and self_grading):
                    self.calendar.grade(
                        name,
                        profile=self.profile.id,
                        key=key,
                        mode=mode,
                        correct=correct,
                        now=now,
                        preview=preview,
                        manual_rating=rating,
                    )
        return assigned
