"""Attempt and score transitions across a single exercise."""

import pytest

from alto.learning.practice_session import PracticeSession


def test_score_and_retries_across_questions() -> None:
    """Count each question once and reset the streak on a first miss."""
    session = PracticeSession()
    for streak in (1, 2):
        session = session.new_question(available=True).after_attempt(
            True,
            calendar_review=False,
            shuffle=False,
        )
        assert session.answered and not session.missed
        assert session.correct == session.total == session.streak == streak
    session = session.new_question(available=True)
    for attempt, correct in enumerate((False, False, True), start=1):
        session = session.after_attempt(
            correct,
            calendar_review=False,
            shuffle=False,
        )
        assert session.attempts == attempt and session.missed
        assert session.answered == correct
        assert (session.correct, session.total, session.streak) == (2, 3, 0)
    empty = session.new_question(available=False)
    assert empty.answered and not empty.missed and empty.attempts == 0
    assert (
        empty.after_attempt(True, calendar_review=False, shuffle=False)
        == empty
    )
    resumed = empty.new_question(available=True)
    assert (
        not resumed.answered and not resumed.missed and resumed.attempts == 0
    )
    assert (resumed.correct, resumed.total, resumed.streak) == (2, 3, 0)


@pytest.mark.parametrize(
    ("calendar_review", "shuffle"),
    [(True, False), (False, True)],
)
def test_miss_finishes_calendar_and_shuffle_questions(
    calendar_review: bool,
    shuffle: bool,
) -> None:
    """
    Reject further attempts on a missed calendar or shuffled question.

    Parameters
    ----------
    calendar_review : bool
        Whether missed cards return on a schedule.
    shuffle : bool
        Whether an answer hands control back to shuffled practice.
    """
    session = PracticeSession().after_attempt(
        False,
        calendar_review=calendar_review,
        shuffle=shuffle,
    )
    assert session.answered and session.missed and session.attempts == 1
    assert (
        session.after_attempt(
            True,
            calendar_review=calendar_review,
            shuffle=shuffle,
        )
        == session
    )
