"""
Answer-button intervals for Anki's default SM-2 and FSRS-6 deck
settings.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta

from fsrs import Card, Rating, Scheduler, State

DAY = 86_400
MAX_DAYS = 36_500
_FSRS = Scheduler(enable_fuzzing=False)
PASSING = (Rating.Hard, Rating.Good, Rating.Easy)


def _fuzz(days: float, *, minimum: int, factor: float) -> int:
    """
    Draw a whole-day interval within Anki's bounded review fuzz range.

    Parameters
    ----------
    days : float
        Base review interval in days.
    minimum : int
        Minimum allowed by the previous interval and adjacent grade.
    factor : float
        Shared draw for the current card, between zero and one.

    Returns
    -------
    int
        Review interval in days.

    Examples
    --------
    >>> _fuzz(4, minimum=1, factor=0.5)
    4
    """
    minimum = min(MAX_DAYS, max(1, minimum))
    days = max(minimum, min(MAX_DAYS, days))
    spread = 0.0
    if days >= 2.5:
        spread = (
            1
            + 0.15 * (min(days, 7) - 2.5)
            + 0.1 * max(0, min(days, 20) - 7)
            + 0.05 * max(0, days - 20)
        )
    low = max(minimum, math.floor(days - spread + 0.5))
    high = min(MAX_DAYS, math.floor(days + spread + 0.5))
    return low + int(factor * (high - low + 1))


@dataclass(frozen=True)
class Sm2State:
    """
    SM-2 learning step, review history, and actual delay for the current
    presentation.

    Examples
    --------
    >>> Sm2State.read(None).phase
    'learning'
    """

    repetitions: int = 0
    interval: int = 0
    ease: float = 2.5
    phase: str = "learning"
    step: int = 0
    delay: int = 0

    @classmethod
    def read(cls, previous: str | None) -> Sm2State:
        """
        Read a button-graded or original automatic SM-2 schedule.

        Parameters
        ----------
        previous : str or None
            Serialized schedule, if this card has been graded.

        Returns
        -------
        Sm2State
            Card state with the existing interval and ease preserved.

        Examples
        --------
        >>> Sm2State.read("[2, 6, 2.5]").phase
        'review'
        """
        if previous is None:
            return cls()
        stored = json.loads(previous)
        if isinstance(stored, dict):
            return cls(**stored)
        repetitions, interval, ease = stored
        return cls(
            repetitions,
            interval,
            ease,
            "review" if interval else "learning",
            delay=interval * DAY or 60,
        )


def inherited_state(
    key: str,
    *,
    source: str,
    state: str,
    due: float,
    rating: Rating,
) -> str:
    """
    Translate one saved calendar schedule into the other scheduler's
    initial state.

    Parameters
    ----------
    key : str
        Card identity.
    source : str
        Scheduler that produced the grade.
    state : str
        Serialized source state.
    due : float
        Original due timestamp.
    rating : Rating
        Last calendar grade.

    Returns
    -------
    str
        Destination state with the same due date and learning phase.

    Examples
    --------
    >>> result = inherited_state(
    ...     "abc",
    ...     source="SM-2",
    ...     state="[8, 180, 2.5]",
    ...     due=200 * DAY,
    ...     rating=Rating.Good,
    ... )
    >>> Card.from_json(result).stability
    180.0
    """
    deadline = datetime.fromtimestamp(due, UTC)
    if source == "FSRS":
        card = Card.from_json(state)
        assert (
            card.last_review is not None
        )  # Only graded cards have saved schedules.
        delay = round((deadline - card.last_review).total_seconds())
        days = max(1, round(delay / DAY)) if card.state == State.Review else 0
        sm2 = Sm2State(
            repetitions=min(days, 2),
            interval=days,
            phase=card.state.name.lower(),
            step=card.step or 0,
            delay=delay,
        )
        return json.dumps(asdict(sm2))

    sm2 = Sm2State.read(state)
    reviewed = deadline - timedelta(seconds=sm2.delay)
    card = Card(card_id=int(key[:15], 16), due=reviewed)
    if sm2.phase == "review":
        # FSRS-6's SM-2 conversion at 90% historical retention:
        # stability equals the full interval.
        stability = float(sm2.interval)
        w = _FSRS.parameters
        growth = math.exp(w[8]) * stability ** -w[9] * math.expm1(0.1 * w[10])
        card.stability = stability
        card.difficulty = max(1.0, min(10.0, 11 - (sm2.ease - 1) / growth))
        card.state, card.step = State.Review, None
        card.last_review = reviewed
    else:
        card, _ = _FSRS.review_card(card, rating, review_datetime=reviewed)
        card.state = (
            State.Relearning if sm2.phase == "relearning" else State.Learning
        )
        card.step = sm2.step
    card.due = deadline
    return card.to_json()


def _sm2_options(
    previous: str | None,
    *,
    due: float,
    now: float,
    factor: float,
) -> dict[Rating, tuple[int, str]]:
    """
    Calculate the four default SM-2 learning, relearning, or review
    outcomes.

    Parameters
    ----------
    previous : str or None
        Saved SM-2 schedule.
    due : float
        Scheduled review timestamp.
    now : float
        Answer timestamp.
    factor : float
        Common fuzz draw across the buttons.

    Returns
    -------
    dict
        Delay and serialized successor state by rating.

    Examples
    --------
    >>> _sm2_options(
    ...     None, due=0, now=0, factor=0.5
    ... )[Rating.Good][0]
    600
    """
    card = Sm2State.read(previous)
    learning = card.phase == "learning"
    relearning = card.phase == "relearning"
    if learning or relearning:
        hard = 900 if relearning else 600 if card.step else 330
        again = replace(card, step=0, delay=600 if relearning else 60)
        graduate = replace(
            card,
            phase="review",
            repetitions=max(1, card.repetitions),
            step=0,
        )
        if learning and card.step == 0:
            good = replace(card, step=1, delay=600)
        else:
            good = replace(graduate, interval=1, delay=DAY)
        easy_days = 2 if relearning else _fuzz(4, minimum=1, factor=factor)
        states = (
            again,
            replace(card, delay=hard),
            good,
            replace(graduate, interval=easy_days, delay=easy_days * DAY),
        )
    else:
        days = card.interval
        late = max(
            0,
            (
                datetime.fromtimestamp(now).date()
                - datetime.fromtimestamp(due).date()
            ).days,
        )
        hard = _fuzz(1.2 * days, minimum=days + 1, factor=factor)
        good = _fuzz(
            (days + late / 2) * card.ease,
            minimum=hard + 1,
            factor=factor,
        )
        easy = _fuzz(
            (days + late) * card.ease * 1.3,
            minimum=good + 1,
            factor=factor,
        )
        next_review = replace(card, repetitions=card.repetitions + 1)
        states = (
            Sm2State(
                ease=max(1.3, card.ease - 0.2),
                phase="relearning",
                delay=600,
            ),
            replace(
                next_review,
                interval=hard,
                ease=max(1.3, card.ease - 0.15),
                delay=hard * DAY,
            ),
            replace(next_review, interval=good, delay=good * DAY),
            replace(
                next_review,
                interval=easy,
                ease=card.ease + 0.15,
                delay=easy * DAY,
            ),
        )
    return {
        grade: (state.delay, json.dumps(asdict(state)))
        for grade, state in zip(Rating, states, strict=True)
    }


def read_fsrs_card(
    key: str,
    *,
    previous: str | None,
    due: datetime,
) -> Card:
    """
    Restore a saved FSRS card or start one for the question.

    Parameters
    ----------
    key : str
        The question's stable card key.
    previous : str or None
        The saved JSON, if the question has been reviewed.
    due : datetime
        Initial due time for a new card.

    Returns
    -------
    Card
        The restored or newly scheduled card.

    Examples
    --------
    A new card is due at the time of its first review.
    """
    if previous:
        return Card.from_json(previous)
    return Card(card_id=int(key[:15], 16), due=due)


def _fsrs_options(
    key: str,
    *,
    previous: str | None,
    now: float,
    factor: float,
) -> dict[Rating, tuple[int, str]]:
    """
    Apply Anki's learning steps and ordered review bounds to FSRS-6
    memory updates.

    Parameters
    ----------
    key : str
        Card identifier.
    previous : str or None
        Serialized FSRS card.
    now : float
        Answer timestamp.
    factor : float
        Common fuzz draw across the buttons.

    Returns
    -------
    dict
        Delay and updated FSRS card by rating.

    Examples
    --------
    >>> _fsrs_options(
    ...     "abc", previous=None, now=0, factor=0.5
    ... )[Rating.Hard][0]
    330
    """
    when = datetime.fromtimestamp(now, UTC)
    card = read_fsrs_card(key, previous=previous, due=when)
    prior_days = 0
    if card.last_review is not None:
        prior_days = round((card.due - card.last_review).total_seconds() / DAY)
        elapsed = (
            datetime.fromtimestamp(now).date()
            - card.last_review.astimezone().date()
        ).days
        card.last_review = when - timedelta(days=max(0, elapsed))
    options = {}
    minimum = 1
    for grade in Rating:
        updated, _ = _FSRS.review_card(card, grade, review_datetime=when)
        assert updated.stability is not None
        # At the default 90% retention, FSRS stability is the unrounded
        # interval in days.
        base = updated.stability
        if updated.state == State.Review:
            if card.state == State.Review:
                if math.floor(base + 0.5) > prior_days:
                    minimum = max(minimum, prior_days + 1)
                elif (
                    _fuzz(base, minimum=1, factor=math.nextafter(1.0, 0.0))
                    >= prior_days
                ):
                    minimum = max(minimum, prior_days)
            else:
                base = math.floor(base + 0.5)
            days = _fuzz(base, minimum=minimum, factor=factor)
            updated.due = when + timedelta(days=days)
            minimum = days + 1
        if card.state != State.Review and grade == Rating.Good:
            # Easy graduates even when Good would still be a learning
            # step.
            minimum = _fuzz(updated.stability, minimum=1, factor=factor) + 1
        options[grade] = (
            round((updated.due - when).total_seconds()),
            updated.to_json(),
        )
    return options


def review_options(
    key: str,
    *,
    mode: str,
    previous: str | None,
    due: float,
    now: float,
) -> dict[Rating, tuple[int, str]]:
    """
    Calculate a consistent set of answer-button intervals from one
    scheduling state.

    Parameters
    ----------
    key : str
        Card identity.
    mode : str
        SM-2 or FSRS.
    previous : str or None
        Schedule before this answer.
    due : float
        Due timestamp of the previous schedule.
    now : float
        Time of the answer.

    Returns
    -------
    dict
        Delay in seconds and serialized successor state for each grade.

    Examples
    --------
    >>> review_options(
    ...     "abc",
    ...     mode="SM-2",
    ...     previous=None,
    ...     due=0,
    ...     now=0,
    ... )[Rating.Again][0]
    60
    """
    factor = random.Random(f"{key}:{mode}:{previous}").random()
    if mode == "SM-2":
        return _sm2_options(previous, due=due, now=now, factor=factor)
    return _fsrs_options(key, previous=previous, now=now, factor=factor)
