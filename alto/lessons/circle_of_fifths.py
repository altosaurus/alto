"""
The lesson on the circle of fifths, taught from nothing.

It covers what a key is, what a fifth is, how the circle counts sharps
and flats, and what the inner ring and the neighbors of a
key mean.

Examples
--------
>>> len(CIRCLE_OF_FIFTHS.steps)
8
>>> summary("outer", place=2)
'<b>D major</b>: 2 sharps (F♯, C♯)'
"""

from __future__ import annotations

import random

from alto.lessons.base import (
    Lesson,
    Step,
    Task,
)
from alto.theory.fifths import (
    MAJORS,
    MINORS,
    SIGNATURES,
    accidentals_of,
)

LETTERS = (
    "CDEFGAB"  # the note names, in order, which wrap around: after B comes C
)


def key_name(ring: str, *, place: int) -> str:
    """
    Return the first name of the key in a cell, written out.

    Parameters
    ----------
    ring : str
        "outer" for the major key, "inner" for the minor.
    place : int
        The place on the circle, clockwise from the top. Keyword-only.

    Returns
    -------
    str
        "G major" or "E minor".

    Examples
    --------
    >>> (
    ...     key_name("outer", place=1),
    ...     key_name("inner", place=1),
    ... )
    ('G major', 'E minor')
    """
    return (
        f"{MAJORS[place][0]} major"
        if ring == "outer"
        else f"{MINORS[place][0][:-1]} minor"
    )


def summary(ring: str, *, place: int) -> str:
    """
    Say a key and its key signature in one line.

    Parameters
    ----------
    ring : str
        "outer" or "inner".
    place : int
        The place on the circle. Keyword-only.

    Returns
    -------
    str
        Simple HTML such as "<b>A major</b>: 3 sharps (F♯, C♯, G♯)".

    Examples
    --------
    >>> (
    ...     summary("outer", place=0),
    ...     summary("inner", place=11),
    ... )
    ('<b>C major</b>: no sharps or flats', '<b>D minor</b>: 1 flat
    (B♭)')
    """
    signature = SIGNATURES[place]
    if signature == 0:
        count = "no sharps or flats"
    else:
        word = "sharp" if signature > 0 else "flat"
        count = (
            f"{abs(signature)}"
            " "
            f"{word}"
            f"{('s' if abs(signature) > 1 else '')}"
            " ("
            f"{', '.join(accidentals_of(signature))}"
            ")"
        )
    return f"<b>{key_name(ring, place=place)}</b>: {count}"


def fifth_task(rng: random.Random) -> Task:
    """
    Ask for the letter a fifth above a random letter, answered with
    buttons.

    Parameters
    ----------
    rng : random.Random
        The random number generator.

    Returns
    -------
    Task
        The question.

    Examples
    --------
    >>> task = fifth_task(random.Random(1))
    >>> task.correct in LETTERS and len(
    ...     task.choices
    ... ) == 4 and task.correct in task.choices
    True
    """
    start = rng.randrange(7)
    spelled = " ".join(LETTERS[(start + step) % 7] for step in range(5))
    answer = LETTERS[(start + 4) % 7]
    others = [letter for letter in LETTERS if letter != answer]
    choices = sorted([answer, *rng.sample(others, 3)])
    return Task(
        prompt=(
            "Count up five letters from <b>"
            f"{LETTERS[start]}"
            "</b>, counting it as 1. Which letter do you land on?"
        ),
        hint=(
            "Say the letter names in order, one for each count: after G "
            "comes A, and after B comes C again."
        ),
        explanation=(
            f"{spelled}. So {answer} is a fifth above {LETTERS[start]}."
        ),
        choices=tuple(choices),
        correct=answer,
    )


def sharps_task(rng: random.Random) -> Task:
    """
    Ask for the major key with a given number of sharps, answered on the
    circle.

    Parameters
    ----------
    rng : random.Random
        The random number generator.

    Returns
    -------
    Task
        The question.

    Examples
    --------
    >>> task = sharps_task(random.Random(2))
    >>> ring, at = next(iter(task.cells))
    >>> (
    ...     ring,
    ...     SIGNATURES[at]
    ...     == int(
    ...         task.prompt.split("<b>")[1].split()[
    ...             0
    ...         ]
    ...     ),
    ... )
    ('outer', True)
    """
    count = rng.randint(1, 5)
    word = "sharp" if count == 1 else "sharps"
    return Task(
        prompt=f"Click the major key with <b>{count} {word}</b>.",
        hint=(
            "Start at C, at the top, and take "
            f"{count}"
            " step"
            f"{('s' if count > 1 else '')}"
            " clockwise."
        ),
        explanation=(
            f"{count}"
            " step"
            f"{('s' if count > 1 else '')}"
            " clockwise from C is "
            f"{MAJORS[count][0]}"
            " major: "
            f"{count}"
            " "
            f"{word}"
            "."
        ),
        cells=frozenset({("outer", count)}),
    )


def flats_task(rng: random.Random) -> Task:
    """
    Ask for the major key with a given number of flats, answered on the
    circle.

    Parameters
    ----------
    rng : random.Random
        The random number generator.

    Returns
    -------
    Task
        The question.

    Examples
    --------
    >>> task = flats_task(random.Random(3))
    >>> ring, at = next(iter(task.cells))
    >>> (
    ...     ring,
    ...     -SIGNATURES[at]
    ...     == int(
    ...         task.prompt.split("<b>")[1].split()[
    ...             0
    ...         ]
    ...     ),
    ... )
    ('outer', True)
    """
    count = rng.randint(1, 5)
    word = "flat" if count == 1 else "flats"
    place = 12 - count
    return Task(
        prompt=f"Click the major key with <b>{count} {word}</b>.",
        hint=(
            "Start at C and take "
            f"{count}"
            " step"
            f"{('s' if count > 1 else '')}"
            " counterclockwise this time."
        ),
        explanation=f"{count}"
        " step"
        f"{('s' if count > 1 else '')}"
        " counterclockwise from C is "
        f"{MAJORS[place][0]}"
        " major: "
        f"{count} {word}.",
        cells=frozenset({("outer", place)}),
    )


def relative_task(rng: random.Random) -> Task:
    """
    Ask for the relative minor of a major key, answered on the circle.

    Parameters
    ----------
    rng : random.Random
        The random number generator.

    Returns
    -------
    Task
        The question.

    Examples
    --------
    >>> task = relative_task(random.Random(4))
    >>> task.cells <= {
    ...     ("inner", at) for at in range(12)
    ... }
    True
    """
    place = rng.randrange(12)
    major, minor = (
        key_name("outer", place=place),
        key_name("inner", place=place),
    )
    return Task(
        prompt=(
            "Which minor key has the same key signature as <b>"
            f"{major}"
            "</b>? Click it on the inner ring."
        ),
        hint="It sits straight inside the major key, on the other ring.",
        explanation=(
            f"{minor}"
            " shares "
            f"{major}"
            "'s key signature: "
            f"{minor.split()[0]}"
            " is the sixth note of the "
            f"{major}"
            " scale."
        ),
        cells=frozenset({("inner", place)}),
    )


def neighbor_task(rng: random.Random) -> Task:
    """
    Ask for the key a fifth above or below a random key, answered on the
    circle.

    Parameters
    ----------
    rng : random.Random
        The random number generator.

    Returns
    -------
    Task
        The question.

    Examples
    --------
    >>> task = neighbor_task(random.Random(5))
    >>> ring, at = next(iter(task.cells))
    >>> ring, at in range(12)
    ('outer', True)
    """
    place = rng.randrange(12)
    above = rng.random() < 0.5
    answer = (place + (1 if above else -1)) % 12
    where, numeral, direction = (
        ("above", "V", "clockwise")
        if above
        else ("below", "IV", "counterclockwise")
    )
    return Task(
        prompt=(
            "In <b>"
            f"{key_name('outer', place=place)}"
            "</b>, which major key is a fifth "
            f"{where}"
            " it? Click it."
        ),
        hint=f"A fifth {where} is one step {direction} on the outer ring.",
        explanation=f"{MAJORS[answer][0]}"
        " is a fifth "
        f"{where}"
        " "
        f"{MAJORS[place][0]}"
        ". In the key of "
        f"{MAJORS[place][0]}"
        ", "
        f"its chord is the {numeral} chord.",
        cells=frozenset({("outer", answer)}),
    )


CIRCLE_OF_FIFTHS = Lesson(
    key="circle-of-fifths",
    title="The Circle of Fifths",
    about="A walk through the circle of fifths for a beginner: what a key"
    " is, what a fifth is, how the circle counts sharps and "
    "flats, and how to read the inner ring. Eight short steps with a "
    "few small exercises. Nothing is scored.",
    summary="Read the circle of fifths from scratch.",
    category="Scales & Keys",
    exercise="CircleOfFifths",
    steps=(
        Step(
            title="A map of major keys",
            text=(
                "<p>A <b>key</b> tells you which note feels like home "
                "and whether the music is major or minor. "
                "In C major, C is home. Play the example to hear the C "
                "major scale return to C.</p>"
                "<p>The <b>circle of fifths</b> is a map of keys. On "
                "the outer ring, neighboring major keys share six "
                "of their seven scale notes. Start at C and look one "
                "place clockwise to G. Only F changes to F♯, "
                "so G major has one sharp in its key signature.</p>"
            ),
            circle="rest",
            hear=(
                ("C4",),
                ("D4",),
                ("E4",),
                ("F4",),
                ("G4",),
                ("A4",),
                ("B4",),
                ("C5",),
            ),
            hear_label="Hear C major",
        ),
        Step(
            title="A fifth",
            text=(
                "<p>The circle is built from one distance between "
                "notes: the <b>fifth</b>.</p>"
                "<p>To find a fifth, count five letter names, starting "
                "with the note you are on as 1. From C that is "
                "<b>C D E F G</b>, so G is a fifth above C. The circle "
                "uses a <b>perfect fifth</b>, which spans "
                "seven half steps.</p>"
                "<p>Press Hear it: you will hear C, then G, then both "
                "together. Listen for the same distance when "
                "the notes sound together.</p>"
            ),
            hear=(("C4",), ("G4",), ("C4", "G4")),
            hear_label="Hear C and G",
            make_task=fifth_task,
        ),
        Step(
            title="Fifths clockwise from C",
            text=(
                "<p>Start at C, at the top of the circle. Every step "
                "<b>clockwise</b> goes up by a fifth: C, then G, then "
                "D, "
                "then "
                "A, E and B.</p>"
                "<p>Use the buttons to take steps, and watch the staff "
                "in the middle. With each step, one more sharp appears."
                " "
                "The new sharp is always the note just below the new "
                "key's first note: G brings F♯, and D brings C♯.</p>"
            ),
            circle="walk",
        ),
        Step(
            title="Sharp keys on the circle",
            text=(
                "<p>That gives you a way to find any key's sharps, "
                "without remembering them: count the steps clockwise "
                "from "
                "C. One step is one sharp, two steps are two sharps, "
                "and so on.</p>"
                "<p>The sharps always come in the same order: <b>F C G "
                "D A E B</b>. A key with three sharps has the first "
                "three, F♯, C♯ and G♯.</p>"
                "<p>Try it. You cannot get it wrong: you will get a "
                "hint, then the answer.</p>"
            ),
            circle="explore",
            make_task=sharps_task,
        ),
        Step(
            title="Flat keys on the circle",
            text=(
                "<p>Counterclockwise from C, each step is a fifth "
                "<i>lower</i>, and adds a <b>flat</b>: F has one flat "
                "(B♭), "
                "B♭ has two (B♭ and E♭), and so on. The flats come in "
                "the order sharps do, backwards: <b>B E A D G C "
                "F</b>.</p>"
                "<p>At the bottom, the two directions meet. F♯ major "
                "(six sharps) and G♭ major (six flats) are the same "
                "keys "
                "on the "
                "piano, spelled two ways. That is why that wedge, and "
                "two others, have two names.</p>"
            ),
            circle="explore",
            make_task=flats_task,
        ),
        Step(
            title="Relative minors on the inner ring",
            text=(
                "<p><b>Relative keys</b> are a major key and a minor "
                "key that share a key signature and have different "
                "tonics. Find C major on the outer ring and A minor "
                "just inside it. Both signatures are empty.</p>"
                "<p>To find the relative minor, count up to degree 6 of"
                " the major scale. In C major that note is A, "
                "so A is the tonic of its relative minor.</p>"
            ),
            circle="explore",
            make_task=relative_task,
        ),
        Step(
            title="A key and its neighbors",
            text=(
                "<p>Keys that sit next to each other on the circle have"
                " almost all their notes in common: only one note is "
                "different. That makes them the closest relatives, and "
                "music often moves between them.</p>"
                "<p>A <b>chord</b> is a group of notes heard together. "
                "Build one on C by taking alternate notes of "
                "C major: C, E and G. This is the <b>I chord</b>. The "
                "Roman numeral I means its starting note is degree "
                "1.</p>"
                "<p>In C major the <b>IV chord</b> starts on F (degree "
                "4) and the <b>V chord</b> starts on G (degree 5). "
                "Find F one place counterclockwise from C and G one "
                "place clockwise. Click C to see them light up.</p>"
            ),
            circle="explore",
            make_task=neighbor_task,
        ),
        Step(
            title="Circle of fifths practice",
            text=(
                "<p>You can read the circle of fifths:</p>"
                "<ul>"
                "<li>Clockwise is a fifth up and one more sharp. "
                "Counterclockwise is a fifth down and one more "
                "flat.</li>"
                "<li>The number of steps from C is the number of sharps"
                " or flats.</li>"
                "<li>The inner ring has each major key's relative "
                "minor, with the same key signature.</li>"
                "<li>The neighbors of a key are its IV and its V.</li>"
                "</ul>"
                "<p>The Circle of Fifths exercise asks these things, "
                "and remembers the ones you find hard. The reference "
                "pane "
                "beside it holds this circle to look things up on.</p>"
            ),
            circle="rest",
            closing=True,
        ),
    ),
)
