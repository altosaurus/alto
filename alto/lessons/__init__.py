"""
The lessons: guided walks through a topic, with small exercises along
the way.

A lesson is plain data, a tuple of steps, so it can be read and tested
without any window. The pages that show one are in
`alto.ui.lesson`.

Examples
--------
>>> [lesson.key for lesson in LESSONS]
['pitches-and-notes', 'clef-basics', 'duration', 'intervals',
'scale-identification', 'key-signatures', 'circle-of-fifths']
"""

from alto.lessons.base import (
    Lesson,
    Staff,
    Step,
    Task,
)
from alto.lessons.circle_of_fifths import CIRCLE_OF_FIFTHS
from alto.lessons.clef_basics import CLEF_BASICS
from alto.lessons.duration import DURATION
from alto.lessons.intervals import INTERVALS
from alto.lessons.key_signatures import KEY_SIGNATURES
from alto.lessons.pitches_and_notes import PITCHES_AND_NOTES
from alto.lessons.scale_identification import SCALE_IDENTIFICATION

LESSONS: list[Lesson] = [
    PITCHES_AND_NOTES,
    CLEF_BASICS,
    DURATION,
    INTERVALS,
    SCALE_IDENTIFICATION,
    KEY_SIGNATURES,
    CIRCLE_OF_FIFTHS,
]
(
    "Every lesson, in the order the lesson list shows them. Installed "
    "plugins add theirs at the end with `register_lesson`."
)


def register_lesson(lesson: Lesson) -> None:
    """
    Add a lesson, such as one that an installed plugin supplies, after
    the lessons already listed.

    Parameters
    ----------
    lesson : Lesson
        The lesson. Its key must not already be in use.

    Raises
    ------
    ValueError
        If another lesson has the same key.

    Examples
    --------
    >>> demo = Lesson(
    ...     key="demo-registered",
    ...     title="Demo",
    ...     about="",
    ...     summary="",
    ...     category="Demos",
    ...     steps=(),
    ...     exercise="NoteNames",
    ... )
    >>> register_lesson(demo)
    >>> LESSONS[-1] is demo
    True
    >>> LESSONS.remove(demo)
    """
    if any(existing.key == lesson.key for existing in LESSONS):
        raise ValueError(
            f"A lesson with the key {lesson.key} is already listed.",
        )
    LESSONS.append(lesson)


__all__ = [
    "LESSONS",
    "Lesson",
    "Staff",
    "Step",
    "Task",
    "register_lesson",
]
