"""Progress through attempts and questions in one exercise."""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class PracticeSession:
    """
    Track the exercise score and attempts on the current question.

    Attributes
    ----------
    correct : int
        Questions answered correctly on the first attempt.
    total : int
        Questions with at least one graded attempt.
    streak : int
        Consecutive questions answered correctly on the first attempt.
    attempts : int
        Graded attempts on the current question.
    missed : bool
        Whether any attempt on the current question was incorrect.
    answered : bool
        Whether the current question is closed to further attempts.
        Also true when the review queue is empty.

    Examples
    --------
    >>> session = PracticeSession().after_attempt(
    ...     False, calendar_review=False, shuffle=False
    ... )
    >>> session = session.after_attempt(
    ...     True, calendar_review=False, shuffle=False
    ... )
    >>> session.attempts, session.total, session.correct
    (2, 1, 0)
    """

    correct: int = 0
    total: int = 0
    streak: int = 0
    attempts: int = 0
    missed: bool = False
    answered: bool = False

    def new_question(self, *, available: bool) -> PracticeSession:
        """
        Keep the score and reset progress for the next question.

        Parameters
        ----------
        available : bool
            Whether the exercise has a question to answer.

        Returns
        -------
        PracticeSession
            Progress for the new question or the empty queue.

        Examples
        --------
        >>> PracticeSession().new_question(available=False).answered
        True
        """
        return PracticeSession(
            correct=self.correct,
            total=self.total,
            streak=self.streak,
            answered=not available,
        )

    def after_attempt(
        self,
        correct: bool,
        *,
        calendar_review: bool,
        shuffle: bool,
    ) -> PracticeSession:
        """
        Score the first attempt and determine retry eligibility.

        Parameters
        ----------
        correct : bool
            Whether the submitted answer was correct.
        calendar_review : bool
            Whether the scheduler brings misses back for later review.
        shuffle : bool
            Whether the learner is practicing in shuffle mode.

        Returns
        -------
        PracticeSession
            Progress after this submission.

        Examples
        --------
        >>> PracticeSession().after_attempt(
        ...     False, calendar_review=True, shuffle=False
        ... ).answered
        True
        """
        if self.answered:
            return self
        first = self.attempts == 0
        streak = self.streak
        if first:
            streak = streak + 1 if correct else 0
        return replace(
            self,
            correct=self.correct + (first and correct),
            total=self.total + first,
            streak=streak,
            attempts=self.attempts + 1,
            missed=self.missed or not correct,
            answered=correct or calendar_review or shuffle,
        )
