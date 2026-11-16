"""
The lessons: guided walks through a topic, with small exercises along the way.

A lesson is plain data, a tuple of steps, so it can be read and tested without any window. The pages that show one are in
`alto.ui.lesson`.

Examples
--------
>>> [lesson.key for lesson in LESSONS]
['circle-of-fifths', 'clef-basics', 'scale-identification']
"""

from alto.lessons.base import (
    Lesson,
    Staff,
    Step,
    Task,
)
from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
from alto.lessons.clef_basics import CLEF_BASICS
from alto.lessons.scale_identification import SCALE_IDENTIFICATION

LESSONS: tuple[Lesson, ...] = (CIRCLE_OF_FIFTHS, CLEF_BASICS, SCALE_IDENTIFICATION)  # in the order they are listed

__all__ = [
    "LESSONS",
    "Lesson",
    "Staff",
    "Step",
    "Task",
]
