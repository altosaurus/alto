"""
How long each operation may take before a test fails: about four to five
times what it took when the budgets were set.

The margin is wide on purpose. A shared build machine can be twice as
slow as this one from one run to the next, and a test that
fails for no reason soon gets ignored. A margin this size still catches
the kind of mistake that makes something ten times slower,
such as measuring a glyph the font does not have, for every name in the
circle of fifths, at every size.

Slower trends than that are for the ASV history to show. When an
operation is made faster or slower on purpose, change its budget
here in the same commit.

Examples
--------
>>> budget_seconds("page:KeySignatures")
0.15
>>> budget_seconds("paint:CircleOfFifths")
0.06
"""

from __future__ import annotations

MILLISECOND = 0.001

# The longest an operation may take, in milliseconds, by its name; a
# name ending in ":" stands for every name that starts with it.
WARM_MS = {
    "page:statistics": 200,
    "page:settings": 400,
    "page:lesson": 200,
    "page:lesson-step": 150,
    "page:lesson-to-exercise": 200,
    "page:exercise-to-lesson": 150,
    "page:home": 50,
    "page:": 150,  # an exercise
    "paint:": 60,
    "resize:": 150,  # ten sizes of the circle of fifths
    "question:": 50,
    "answer:": 50,
    "data:attempt-rows": 100,
    "data:item-rows": 80,
    "data:": 40,
    "learner:": 20,
}

# The first use in a new process, which also builds the fonts and
# layouts that are cached afterwards, and varies more.
COLD_MS = {
    "startup": 1000,
    "resize:": 150,
    "page:": 800,
}


def _lookup(
    table: dict[str, int],
    *,
    name: str,
) -> int:
    """
    Find the budget for a name: the exact name first, then the longest
    prefix that is listed.

    Parameters
    ----------
    table : dict of str to int
        The budgets in milliseconds.
    name : str
        The operation's name. Keyword-only.

    Returns
    -------
    int
        The budget in milliseconds.

    Raises
    ------
    KeyError
        If no entry fits, so that a new operation cannot go unwatched.

    Examples
    --------
    >>> (
    ...     _lookup(WARM_MS, name="page:home"),
    ...     _lookup(WARM_MS, name="page:NoteNames"),
    ... )
    (50, 150)
    >>> _lookup(WARM_MS, name="unknown")
    Traceback (most recent call last):
    KeyError: 'no budget for unknown'
    """
    if name in table:
        return table[name]
    prefixes = [
        prefix
        for prefix in table
        if name.startswith(prefix) and prefix.endswith(":")
    ]
    if not prefixes:
        raise KeyError(f"no budget for {name}")
    return table[max(prefixes, key=len)]


def budget_seconds(
    name: str,
    *,
    cold: bool = False,
) -> float:
    """
    Give how long an operation may take, in seconds.

    Parameters
    ----------
    name : str
        The operation's name, such as "page:KeySignatures".
    cold : bool, default False
        Whether it is the first use in a new process. Keyword-only.

    Returns
    -------
    float
        The budget.

    Examples
    --------
    >>> budget_seconds("startup", cold=True)
    1.0
    """
    return _lookup(COLD_MS if cold else WARM_MS, name=name) * MILLISECOND
