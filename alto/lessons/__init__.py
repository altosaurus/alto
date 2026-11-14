"""
The lessons: guided walks through a topic, with small exercises along the way.

A lesson is plain data, a tuple of steps, so it can be read and tested without any window. The pages that show one are in
`alto.ui.lesson`.

Examples
--------
>>> [lesson.key for lesson in LESSONS]
['circle-of-fifths']
"""

from alto.lessons.base import (
    Lesson,
    Step,
    Task,
)
from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS

LESSONS: tuple[Lesson, ...] = (CIRCLE_OF_FIFTHS,)  # in the order they are listed

__all__ = [
    "LESSONS",
    "Lesson",
    "Step",
    "Task",
]
