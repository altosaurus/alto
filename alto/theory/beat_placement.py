"""
Beat selections in two-measure rhythm exercises.

Slots count eighth notes from the start of the score. Undo uses
selection order. Beat numbers and recorded answers use score order.

Examples
--------
>>> toggle_beat([4, 0], slot=4)
[0]
"""

from collections.abc import Sequence
from itertools import groupby


def toggle_beat(marks: Sequence[int], *, slot: int) -> list[int]:
    """
    Toggle a slot and return the marks in selection order.

    Parameters
    ----------
    marks : sequence of int
        Previously selected slots in the order they were added.
    slot : int
        Slot selected by the learner.

    Returns
    -------
    list of int
        A new selection with the slot removed or appended.

    Examples
    --------
    >>> toggle_beat([4, 0], slot=2)
    [4, 0, 2]
    """
    result = list(marks)
    if slot in result:
        result.remove(slot)
    else:
        result.append(slot)
    return result


def number_beats(
    marks: Sequence[int],
    *,
    slots_per_bar: int,
) -> dict[int, int]:
    """
    Assign beat numbers in reading order, restarting at each bar.

    Parameters
    ----------
    marks : sequence of int
        Selected eighth-note slots.
    slots_per_bar : int
        Number of eighth-note slots in one measure.

    Returns
    -------
    dict of int to int
        The displayed beat number for each selected slot.

    Examples
    --------
    >>> number_beats([9, 6, 3], slots_per_bar=6)
    {3: 1, 6: 1, 9: 2}
    """
    return {
        slot: number
        for _, measure in groupby(
            sorted(marks),
            key=lambda slot: slot // slots_per_bar,
        )
        for number, slot in enumerate(measure, 1)
    }


def grade_beat_marks(
    marks: Sequence[int],
    *,
    expected: frozenset[int],
) -> tuple[bool, str]:
    """
    Grade a beat selection and format the choice for practice history.

    Parameters
    ----------
    marks : sequence of int
        Slots selected by the learner.
    expected : frozenset of int
        Main beat positions in the exercise meter.

    Returns
    -------
    tuple of bool and str
        Whether the selection matches, and the slots in score order.

    Examples
    --------
    >>> grade_beat_marks([9, 0, 6, 3], expected=frozenset({0, 3, 6, 9}))
    (True, '0 3 6 9')
    """
    return set(marks) == expected, " ".join(
        str(slot) for slot in sorted(marks)
    )
