"""
Build balanced rhythm equations with exact operator counts.

Examples
--------
An equation with one operation per side can compare a sum to a product.
"""

from __future__ import annotations

import math
import operator
import random
from collections.abc import Iterator, Sequence
from functools import lru_cache, partial

from alto import settings
from alto.exercises.base import Question

FACTORS = tuple(range(2, 9))
# A dotted thirty-second is three quarters of a sixteenth. Leave enough
# integer units for every permitted division on either side to be exact.
UNITS_PER_SIXTEENTH = 4 * math.lcm(*FACTORS) ** settings.MAX_RHYTHM_OPERATORS
FORWARD = {
    "+": operator.add,
    "−": operator.sub,
    "×": operator.mul,
    "÷": operator.floordiv,
}
INVERSE = {
    "+": operator.sub,
    "−": operator.add,
    "×": operator.floordiv,
    "÷": operator.mul,
}


def _operands(
    operators: tuple[str, ...],
    *,
    values: tuple[int, ...],
    grouped: bool,
) -> Iterator[tuple[str, tuple[int, ...]]]:
    """
    Pair selected operations with legal right operands.

    Parameters
    ----------
    operators : tuple of str
        Enabled operation signs.
    values : tuple of int
        Available musical durations.
    grouped : bool
        Whether this operand must be a tied or beamed note group.

    Yields
    ------
    tuple
        An operation and its possible operands.

    Examples
    --------
    >>> list(_operands(("+", "×"), values=(4,), grouped=True))
    [('+', (4,))]
    """
    for sign in operators:
        if sign in ("+", "−"):
            yield sign, values
        elif not grouped:
            yield sign, FACTORS


def _prefix_operators(
    operators: tuple[str, ...],
    *,
    sign: str,
    parentheses: bool,
) -> tuple[str, ...]:
    """
    Find the operations allowed before a given sign on one side.

    Parameters
    ----------
    operators : tuple of str
        Available signs.
    sign : str
        Operation applied to the prefix.
    parentheses : bool
        Whether a sum can be grouped before multiplying or dividing.

    Returns
    -------
    tuple of str
        Signs available while building the prefix.

    Examples
    --------
    >>> _prefix_operators(("+", "×"), sign="×", parentheses=False)
    ('×',)
    """
    if not parentheses and sign in ("×", "÷"):
        return tuple(op for op in operators if op in ("×", "÷"))
    return operators


@lru_cache(maxsize=128)
def _totals(
    count: int,
    *,
    operators: tuple[str, ...],
    ordinary: tuple[int, ...],
    groups: tuple[int, ...],
    group_at: int,
    parentheses: bool = False,
) -> frozenset[int]:
    """
    Find the nonnegative durations attainable at this operator count.

    Parameters
    ----------
    count : int
        Exact number of operators.
    operators : tuple of str
        Enabled operation signs.
    ordinary : tuple of int
        Durations of selected symbols.
    groups : tuple of int
        Durations of the selected type of note group.
    group_at : int
        Operand reserved for a group, or -1 for single symbols.
    parentheses : bool
        Whether an expression can group operations with parentheses.

    Returns
    -------
    frozenset of int
        Attainable totals in exact duration units.

    Examples
    --------
    >>> _totals(1, operators=("+",), ordinary=(4,),
    ...         groups=(), group_at=-1)
    frozenset({8})
    """
    values = groups if group_at == count else ordinary
    if count == 0:
        return frozenset(values)
    totals = set()
    for sign, amounts in _operands(
        operators,
        values=values,
        grouped=group_at == count,
    ):
        previous = _totals(
            count - 1,
            operators=_prefix_operators(
                operators,
                sign=sign,
                parentheses=parentheses,
            ),
            ordinary=ordinary,
            groups=groups,
            group_at=group_at if group_at < count else -1,
            parentheses=parentheses,
        )
        apply = FORWARD[sign]
        for amount in amounts:
            totals.update(apply(value, amount) for value in previous)
    return frozenset(value for value in totals if value >= 0)


def _side(
    rng: random.Random,
    *,
    count: int,
    slot: int,
    target: int,
    operators: tuple[str, ...],
    ordinary: dict[int, list[str]],
    group: dict[int, list[str]],
    totals: partial[frozenset[int]],
    parentheses: bool,
) -> list[str]:
    """
    Recover one expression with the chosen total.

    Parameters
    ----------
    rng : random.Random
        Chooses among legal steps.
    target : int
        Total required for this side.
    operators : tuple of str
        Enabled signs.
    ordinary : dict
        Single symbols by duration.
    group : dict
        Grouped symbols by duration.
    totals : partial
        Cached prefix totals for this selection.
    count : int
        Requested operators on this side.
    slot : int
        Reserved group position, or -1.
    parentheses : bool
        Whether an expression can group operations with parentheses.

    Returns
    -------
    list of str
        Printable expression tokens.

    Examples
    --------
    Multiplying a sum encloses it in parentheses.
    """
    total = target
    steps = []
    for index in range(count, 0, -1):
        names = group if index == slot else ordinary
        values = tuple(names)
        options = []
        for sign, amounts in _operands(
            operators,
            values=values,
            grouped=index == slot,
        ):
            prefix = _prefix_operators(
                operators,
                sign=sign,
                parentheses=parentheses,
            )
            previous = totals(
                index - 1,
                operators=prefix,
                group_at=slot if slot < index else -1,
            )
            matches = [
                n
                for n in amounts
                if (sign != "×" or total % n == 0)
                and INVERSE[sign](total, n) in previous
            ]
            if matches:
                options.append((sign, matches, prefix))
        sign, matches, operators = rng.choice(options)
        n = rng.choice(matches)
        operand = str(n) if sign in ("×", "÷") else rng.choice(names[n])
        steps.append((sign, operand))
        total = INVERSE[sign](total, n)
    names = group if slot == 0 else ordinary
    tokens = [rng.choice(names[total])]
    additive = False
    for sign, operand in reversed(steps):
        if additive and sign in ("×", "÷"):
            tokens = ["(", *tokens, ")"]
        tokens.extend((sign, operand))
        additive = sign in ("+", "−")
    # Two subtractions can also ask learners to add the durations first.
    if parentheses and "+" in operators:
        match steps:
            case [("−", last), ("−", penultimate), *_]:
                tokens[-3:] = ["(", penultimate, "+", last, ")"]
    return tokens


def equation_tokens(
    rng: random.Random,
    *,
    ordinary: dict[float, list[str]],
    grouped: tuple[dict[float, list[str]], ...],
    left: int,
    right: int,
    operators: tuple[str, ...],
    right_operators: tuple[str, ...] | None = None,
    parentheses: bool = True,
) -> list[str]:
    """
    Choose a shared total, then build both sides backwards from it.

    Parameters
    ----------
    rng : random.Random
        Chooses the grouping, total, signs and symbols.
    ordinary : dict
        Single note and rest names by duration in sixteenth notes.
    grouped : tuple of dict
        Separate tables of tied and beamed names by duration.
    left : int
        Operator count before the equals sign.
    right : int
        Operator count after the equals sign.
    operators : tuple of str
        Signs allowed on the left and, by default, on the right.
    right_operators : tuple of str or None
        Separate selection of signs for the right side.
    parentheses : bool
        Whether an expression can group operations with parentheses.

    Returns
    -------
    list of str
        Equation tokens, or an empty list if no equation fits.

    Examples
    --------
    >>> equation_tokens(random.Random(0), ordinary={4: ["q"]},
    ...     grouped=(), left=1, right=1, operators=("+",))
    ['q', '+', 'q', '=', 'q', '+', 'q']
    """
    if right_operators is None:
        right_operators = operators
    plain = {
        round(value * UNITS_PER_SIXTEENTH): names
        for value, names in ordinary.items()
    }
    kinds = [{}, *(table for table in grouped if table)]
    rng.shuffle(kinds)
    plain_values = tuple(sorted(plain))
    for table in kinds:
        group = {
            round(value * UNITS_PER_SIXTEENTH): names
            for value, names in table.items()
        }
        group_values = tuple(sorted(group))
        positions = [(-1, -1)]
        if group:
            positions = [(i, -1) for i in range(left + 1)] + [
                (-1, i) for i in range(right + 1)
            ]
            rng.shuffle(positions)

        totals = partial(
            _totals,
            ordinary=plain_values,
            groups=group_values,
            parentheses=parentheses,
        )
        for left_slot, right_slot in positions:
            common = totals(
                left,
                operators=operators,
                group_at=left_slot,
            ) & totals(
                right,
                operators=right_operators,
                group_at=right_slot,
            )
            if common:
                target = rng.choice(sorted(common))
                side = partial(
                    _side,
                    rng,
                    target=target,
                    ordinary=plain,
                    group=group,
                    totals=totals,
                    parentheses=parentheses,
                )
                return [
                    *side(count=left, slot=left_slot, operators=operators),
                    "=",
                    *side(
                        count=right,
                        slot=right_slot,
                        operators=right_operators,
                    ),
                ]
    return []


def counted_operands(
    ordinary: dict[float, list[str]],
) -> dict[float, list[str]]:
    """
    Supply counts for totals without a selected single symbol.

    Parameters
    ----------
    ordinary : dict
        Selected symbols by duration.

    Returns
    -------
    dict
        Count and unit tokens indexed by their combined duration.

    Examples
    --------
    >>> counted_operands({4: ["quarter"]})[12]
    ['3:quarter']
    """
    counted: dict[float, list[str]] = {}
    for unit, names in ordinary.items():
        for count in range(1, 9):
            counted.setdefault(count * unit, []).extend(
                f"{count}:{name}" for name in names
            )
    return counted


def _blank_prompt(tokens: Sequence[str], *, blank: int) -> str:
    """
    Show the equation with one token hidden.

    Parameters
    ----------
    tokens : sequence of str
        Complete equation in score order.
    blank : int
        Position of the token to hide.

    Returns
    -------
    str
        The question prompt.

    Examples
    --------
    >>> _blank_prompt(("half", "÷", "2", "=", "quarter"), blank=2)
    'half ÷ _ = quarter'
    """
    return " ".join(
        "_" if index == blank else token for index, token in enumerate(tokens)
    )


def _count_question(
    tokens: Sequence[str],
    *,
    blank: int,
    count: int,
    unit: str,
) -> Question:
    """
    Ask for a duration as a whole number of the given note value.

    Parameters
    ----------
    tokens : sequence of str
        Balanced equation.
    blank : int
        Position to replace.
    count : int
        Number of units in the missing duration.
    unit : str
        Note or equivalent rest used as the counting unit.

    Returns
    -------
    Question
        The equation with its unit shown above the blank.

    Examples
    --------
    >>> _count_question(["half", "=", "half"], blank=2,
    ...                 count=2, unit="quarter").caption
    'Count in quarter notes.'
    """
    name = unit.removesuffix("-rest").replace("breve", "double whole")
    name = name.replace("_", "-").replace("dotted-", "dotted ")
    return Question(
        _blank_prompt(tokens, blank=blank),
        choices=[str(n) for n in range(1, 9)],
        answer=str(count),
        caption=f"Count in {name} notes.",
    )


def number_question(
    rng: random.Random,
    *,
    tokens: Sequence[str],
    ordinary: dict[float, list[str]],
) -> Question:
    """
    Hide a numeric factor, or count a duration in an explicit unit.

    Parameters
    ----------
    rng : random.Random
        Selects the blank and counting unit.
    tokens : sequence of str
        Balanced equation. Each factor scales the preceding subtotal,
        with any additive prefix enclosed in parentheses.
    ordinary : dict
        Selected note and rest symbols by duration.

    Returns
    -------
    Question
        A numeric answer with a unit caption when counting durations.

    Examples
    --------
    >>> tokens = ["half", "÷", "2", "=", "quarter"]
    >>> number_question(random.Random(0), tokens=tokens,
    ...     ordinary={4: ["quarter"], 8: ["half"]}).answer
    '2'
    >>> tokens
    ['half', '÷', '2', '=', 'quarter']
    """
    factors: list[int] = []
    symbol_slots: list[int] = []
    total = 0
    sign = "+"
    for index, token in enumerate(tokens):
        if ":" in token:
            count, unit = token.split(":")
            return _count_question(
                tokens,
                blank=index,
                count=int(count),
                unit=unit,
            )
        if token == "=":
            sign, total = "+", 0
        elif token in FORWARD:
            sign = token
        elif token not in ("(", ")"):
            if token.isdecimal():
                if total:
                    factors.append(index)
                value = int(token)
            else:
                duration = sum(
                    settings.RHYTHM_DURATIONS[name]
                    for name in token.replace("|", "~").split("~")
                )
                value = round(duration * UNITS_PER_SIXTEENTH)
                if token in settings.RHYTHM_DURATIONS:
                    symbol_slots.append(index)
            total = FORWARD[sign](total, value)
    if factors:
        blank = rng.choice(factors)
        answer = tokens[blank]
        return Question(
            _blank_prompt(tokens, blank=blank),
            choices=[str(n) for n in FACTORS],
            answer=answer,
        )
    blank = rng.choice(symbol_slots)
    duration = settings.RHYTHM_DURATIONS[tokens[blank]]
    units = [
        unit
        for unit in ordinary
        if duration % unit == 0 and 1 <= duration / unit <= 8
    ]
    unit = rng.choice(units)
    return _count_question(
        tokens,
        blank=blank,
        count=int(duration / unit),
        unit=rng.choice(ordinary[unit]),
    )


def equation_question(
    rng: random.Random,
    *,
    symbols: dict[str, float],
    ties: bool,
    beams: bool,
    left: int,
    right: int,
    operators: tuple[str, ...],
    right_operators: tuple[str, ...],
    parentheses: bool,
    answer_types: set[str],
) -> Question:
    """
    Build a rhythm question from the enabled symbols and operations.

    Parameters
    ----------
    rng : random.Random
        Chooses the equation, blank, and answer type.
    symbols : dict of str to float
        Enabled notation and its duration in sixteenth notes.
    ties, beams : bool
        Allow tied or beamed operands, respectively.
    left, right : int
        Number of operations required on each side.
    operators, right_operators : tuple of str
        Allowed operations on the left and right sides.
    parentheses : bool
        Allow parentheses to group operations.
    answer_types : set of str
        Enabled answers, drawn from "symbol" and "number".

    Returns
    -------
    Question
        The equation with one blank, or a prompt to revise the options.

    Examples
    --------
    >>> q = equation_question(
    ...     random.Random(0), symbols={"quarter": 4}, ties=False,
    ...     beams=False, left=1, right=1, operators=("+",),
    ...     right_operators=("+",), parentheses=False,
    ...     answer_types={"symbol"},
    ... )
    >>> q.answer
    'quarter'
    """
    ordinary: dict[float, list[str]] = {}
    tied: dict[float, list[str]] = {}
    beamed: dict[float, list[str]] = {}
    for name, duration in symbols.items():
        ordinary.setdefault(duration, []).append(name)
    if ties:
        notes = [name for name in symbols if not name.endswith("-rest")]
        for index, first in enumerate(notes):
            for second in notes[index:]:
                duration = symbols[first] + symbols[second]
                tied.setdefault(duration, []).append(f"{first}~{second}")
    if beams:
        for name in settings.RHYTHM_BEAM_COUNTS:
            if name in symbols:
                duration = 2 * symbols[name]
                beamed.setdefault(duration, []).append(f"{name}|{name}")
    build = partial(
        equation_tokens,
        rng,
        ordinary=ordinary,
        left=left,
        right=right,
        operators=operators,
        right_operators=right_operators,
        parentheses=parentheses,
    )
    tokens = build(grouped=(tied, beamed))
    if not tokens and "number" in answer_types:
        tokens = build(grouped=(counted_operands(ordinary),))
        if tokens:
            return number_question(rng, tokens=tokens, ordinary=ordinary)
    if not tokens:
        return Question(
            "These settings cannot form a balanced equation. "
            "Change the operator counts, operations, or symbols.",
            choices=[],
            answer="",
        )
    if "number" in answer_types and (
        "symbol" not in answer_types or rng.choice((False, True))
    ):
        return number_question(rng, tokens=tokens, ordinary=ordinary)
    blank = rng.choice(
        [i for i, token in enumerate(tokens) if token in symbols],
    )
    answer = tokens[blank]
    return Question(
        _blank_prompt(tokens, blank=blank),
        choices=list(symbols),
        answer=answer,
        accept=tuple(
            name
            for name, duration in symbols.items()
            if name != answer and duration == symbols[answer]
        ),
    )
