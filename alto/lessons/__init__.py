"""
The lessons: guided walks through a topic, with small exercises along the way.

A lesson is plain data, a tuple of steps, so it can be read and tested without any window. The pages that show one are in
`alto.ui.lesson`.

Examples
--------
>>> [lesson.key for lesson in LESSONS]
['pitches-and-notes', 'clef-basics', 'intervals', 'scale-identification', 'key-signatures', 'circle-of-fifths']
"""

from alto.lessons.base import (
    Lesson,
    Staff,
    Step,
    Task,
)
from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
from alto.lessons.clef_basics import CLEF_BASICS
from alto.lessons.intervals import INTERVALS
from alto.lessons.key_signatures import KEY_SIGNATURES
from alto.lessons.pitches_and_notes import PITCHES_AND_NOTES
from alto.lessons.scale_identification import SCALE_IDENTIFICATION

LESSONS: tuple[Lesson, ...] = (PITCHES_AND_NOTES, CLEF_BASICS, INTERVALS, SCALE_IDENTIFICATION, KEY_SIGNATURES, CIRCLE_OF_FIFTHS)

__all__ = [
    "LESSONS",
    "Lesson",
    "Staff",
    "Step",
    "Task",
]
