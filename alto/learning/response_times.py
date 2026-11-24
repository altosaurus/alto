"""Rolling response times for one learner and exercise."""

from __future__ import annotations

from dataclasses import dataclass

from fsrs import Rating

WINDOW = 100
MINIMUM = 40


@dataclass(frozen=True)
class ResponseTimes:
    """
    Sorted millisecond timings and the profile's fastest and slowest
    tail percentages.

    Examples
    --------
    >>> sample = ResponseTimes(
    ...     tuple(range(1, 101)), 15, 15
    ... )
    >>> (
    ...     sample.grade(1).name,
    ...     sample.grade(50).name,
    ...     sample.grade(100).name,
    ... )
    ('Easy', 'Good', 'Hard')
    """

    times: tuple[int, ...]
    easy_percent: int
    hard_percent: int

    @property
    def ready(self) -> bool:
        """
        Check whether this exercise has enough eligible answers.

        Returns
        -------
        bool
            True once at least 40 previous answers are available.

        Examples
        --------
        >>> ResponseTimes((), 15, 15).ready
        False
        """
        return len(self.times) >= MINIMUM

    def percentile(self, percent: int) -> float:
        """
        Interpolate a percentile between adjacent observations in a
        nonempty sample.

        Parameters
        ----------
        percent : int
            Percentile from zero to 100.

        Returns
        -------
        float
            Elapsed milliseconds at the requested percentile.

        Examples
        --------
        >>> ResponseTimes(
        ...     (1000, 2000), 15, 15
        ... ).percentile(25)
        1250.0
        """
        index, remainder = divmod((len(self.times) - 1) * percent, 100)
        lower = self.times[index]
        return (
            lower
            + (self.times[min(index + 1, len(self.times) - 1)] - lower)
            * remainder
            / 100
        )

    def grade(self, milliseconds: int) -> Rating:
        """
        Grade a correct first answer against earlier answers to this
        exercise.

        Parameters
        ----------
        milliseconds : int
            Eligible duration, or zero if the timing is unavailable.

        Returns
        -------
        Rating
            Hard for slow answers, Easy for fast answers, and Good for
            ties or missing timings.

        Examples
        --------
        >>> ResponseTimes((1000,) * 40, 15, 15).grade(
        ...     1000
        ... ).name
        'Good'
        """
        if self.ready and milliseconds > 0:
            if self.easy_percent and milliseconds < self.percentile(
                self.easy_percent,
            ):
                return Rating.Easy
            if self.hard_percent and milliseconds > self.percentile(
                100 - self.hard_percent,
            ):
                return Rating.Hard
        return Rating.Good
