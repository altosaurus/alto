"""
The lesson on the circle of fifths, taught from nothing.

It covers what a key is, what a fifth is, how the circle counts sharps and flats, and what the inner ring and the neighbours of a
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

LETTERS = "CDEFGAB"  # the note names, in order, which wrap round: after B comes C


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
    >>> key_name("outer", place=1), key_name("inner", place=1)
    ('G major', 'E minor')
    """
    return f"{MAJORS[place][0]} major" if ring == "outer" else f"{MINORS[place][0][:-1]} minor"


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
    >>> summary("outer", place=0), summary("inner", place=11)
    ('<b>C major</b>: no sharps or flats', '<b>D minor</b>: 1 flat (B♭)')
    """
    signature = SIGNATURES[place]
    if signature == 0:
        count = "no sharps or flats"
    else:
        word = "sharp" if signature > 0 else "flat"
        count = f"{abs(signature)} {word}{'s' if abs(signature) > 1 else ''} ({', '.join(accidentals_of(signature))})"
    return f"<b>{key_name(ring, place=place)}</b>: {count}"


def fifth_task(rng: random.Random) -> Task:
    """
    Ask for the letter a fifth above a random letter, answered with buttons.

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
    >>> task.correct in LETTERS and len(task.choices) == 4 and task.correct in task.choices
    True
    """
    start = rng.randrange(7)
    spelled = " ".join(LETTERS[(start + step) % 7] for step in range(5))
    answer = LETTERS[(start + 4) % 7]
    others = [letter for letter in LETTERS if letter != answer]
    choices = sorted([answer, *rng.sample(others, 3)])
    return Task(
        prompt=f"Count up five letters from <b>{LETTERS[start]}</b>, counting it as 1. Which letter do you land on?",
        hint="Say the letter names in order, one for each count: after G comes A, and after B comes C again.",
        explanation=f"{spelled}. So {answer} is a fifth above {LETTERS[start]}.",
        choices=tuple(choices),
        correct=answer,
    )


def sharps_task(rng: random.Random) -> Task:
    """
    Ask for the major key with a given number of sharps, answered on the circle.

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
    >>> ring, SIGNATURES[at] == int(task.prompt.split("<b>")[1].split()[0])
    ('outer', True)
    """
    count = rng.randint(1, 5)
    word = "sharp" if count == 1 else "sharps"
    return Task(
        prompt=f"Click the major key with <b>{count} {word}</b>.",
        hint=f"Start at C, at the top, and take {count} step{'s' if count > 1 else ''} clockwise.",
        explanation=f"{count} step{'s' if count > 1 else ''} clockwise from C is {MAJORS[count][0]} major: {count} {word}.",
        cells=frozenset({("outer", count)}),
    )


def flats_task(rng: random.Random) -> Task:
    """
    Ask for the major key with a given number of flats, answered on the circle.

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
    >>> ring, -SIGNATURES[at] == int(task.prompt.split("<b>")[1].split()[0])
    ('outer', True)
    """
    count = rng.randint(1, 5)
    word = "flat" if count == 1 else "flats"
    place = 12 - count
    return Task(
        prompt=f"Click the major key with <b>{count} {word}</b>.",
        hint=f"Start at C and take {count} step{'s' if count > 1 else ''} counterclockwise this time.",
        explanation=f"{count} step{'s' if count > 1 else ''} counterclockwise from C is {MAJORS[place][0]} major: "
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
    >>> task.cells <= {("inner", at) for at in range(12)}
    True
    """
    place = rng.randrange(12)
    major, minor = key_name("outer", place=place), key_name("inner", place=place)
    return Task(
        prompt=f"Which minor key has the same key signature as <b>{major}</b>? Click it on the inner ring.",
        hint="It sits straight inside the major key, on the other ring.",
        explanation=f"{minor} shares {major}'s key signature: {minor.split()[0]} is the sixth note of the {major} scale.",
        cells=frozenset({("inner", place)}),
    )


def neighbour_task(rng: random.Random) -> Task:
    """
    Ask for the key a fifth above or below a random key, answered on the circle.

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
    >>> task = neighbour_task(random.Random(5))
    >>> ring, at = next(iter(task.cells))
    >>> ring, at in range(12)
    ('outer', True)
    """
    place = rng.randrange(12)
    above = rng.random() < 0.5
    answer = (place + (1 if above else -1)) % 12
    where, numeral, direction = ("above", "V", "clockwise") if above else ("below", "IV", "counterclockwise")
    return Task(
        prompt=f"In <b>{key_name('outer', place=place)}</b>, which major key is a fifth {where} it? Click it.",
        hint=f"A fifth {where} is one step {direction} on the outer ring.",
        explanation=f"{MAJORS[answer][0]} is a fifth {where} {MAJORS[place][0]}. In the key of {MAJORS[place][0]}, "
        f"its chord is the {numeral} chord.",
        cells=frozenset({("outer", answer)}),
    )


CIRCLE_OF_FIFTHS = Lesson(
    key="circle-of-fifths",
    title="The Circle of Fifths",
    about="A walk through the circle of fifths for a beginner: what a key is, what a fifth is, how the circle counts sharps and "
    "flats, and how to read the inner ring. Eight short steps with a few small exercises. Nothing is scored.",
    summary="Read the circle of fifths from scratch.",
    category="Scales & Keys",
    exercise="CircleOfFifths",
    steps=(
        Step(
            title="Why keys need a map",
            text=(
                "<p>Almost every song is built from seven of the twelve notes on a piano. Which seven notes it uses is "
                "the song's <b>key</b>.</p>"
                "<p>The white keys, played from one C up to the next, make the key of <b>C major</b>. Press Hear it to listen to "
                "it.</p>"
                "<p>Every other key needs some black keys. They are written as sharps (♯) or flats (♭) at the start of each "
                "line of music, and together they are the key's <b>key signature</b>. There are twelve major keys, and each has "
                "its own. The <b>circle of fifths</b>, below, is a map of all twelve: it shows how they are related, and how "
                "many sharps or flats each one has. The rest of this lesson shows you how to read it.</p>"
            ),
            circle="rest",
            hear=(("C4",), ("D4",), ("E4",), ("F4",), ("G4",), ("A4",), ("B4",), ("C5",)),
            hear_label="Hear C major",
        ),
        Step(
            title="A fifth",
            text=(
                "<p>The circle is built from one distance between notes: the <b>fifth</b>.</p>"
                "<p>To find a fifth, count five letter names, starting with the note you are on as 1. From C that is "
                "<b>C D E F G</b>, so G is a fifth above C. On a piano it is seven keys along, counting the black ones.</p>"
                "<p>Press Hear it: you will hear C, then G, then both together. They sound steady together, which is why "
                "fifths are used to link the keys.</p>"
            ),
            hear=(("C4",), ("G4",), ("C4", "G4")),
            hear_label="Hear C and G",
            make_task=fifth_task,
        ),
        Step(
            title="Walking clockwise",
            text=(
                "<p>Start at C, at the top of the circle. Every step <b>clockwise</b> goes up by a fifth: C, then G, then D, "
                "then "
                "A, E and B.</p>"
                "<p>Use the buttons to take steps, and watch the staff in the middle. With each step, one more sharp appears. "
                "The new sharp is always the note just below the new key's first note: G brings F♯, and D brings C♯.</p>"
            ),
            circle="walk",
        ),
        Step(
            title="Counting sharps",
            text=(
                "<p>That gives you a way to find any key's sharps, without remembering them: count the steps clockwise from "
                "C. One step is one sharp, two steps are two sharps, and so on.</p>"
                "<p>The sharps always come in the same order: <b>F C G D A E B</b>. A key with three sharps has the first "
                "three, F♯, C♯ and G♯.</p>"
                "<p>Try it. You cannot get it wrong: you will get a hint, then the answer.</p>"
            ),
            circle="explore",
            make_task=sharps_task,
        ),
        Step(
            title="Flats go the other way",
            text=(
                "<p>Counterclockwise from C, each step is a fifth <i>lower</i>, and adds a <b>flat</b>: F has one flat (B♭), "
                "B♭ has two (B♭ and E♭), and so on. The flats come in the order sharps do, backwards: <b>B E A D G C F</b>.</p>"
                "<p>At the bottom, the two directions meet. F♯ major (six sharps) and G♭ major (six flats) are the same keys "
                "on the "
                "piano, spelt two ways. That is why that wedge, and two others, have two names.</p>"
            ),
            circle="explore",
            make_task=flats_task,
        ),
        Step(
            title="The inner ring: relative minors",
            text=(
                "<p>Each major key has a partner <b>minor</b> key that uses exactly the same notes, and the same key signature, "
                "but starts on a different one. They are called <b>relative</b> keys.</p>"
                "<p>The inner ring shows them. A minor sits under C major: it is the white keys again, starting from A, the "
                "sixth note of C major. In the same way, every minor key is the sixth note of its major.</p>"
            ),
            circle="explore",
            make_task=relative_task,
        ),
        Step(
            title="A key and its neighbours",
            text=(
                "<p>Keys that sit next to each other on the circle have almost all their notes in common: only one note is "
                "different. That makes them the closest relatives, and music often moves between them.</p>"
                "<p>The key one step clockwise is a fifth above, called the <b>V</b> (five). The one counterclockwise is a "
                "fifth below, the <b>IV</b> (four). Together with the key itself, <b>I</b>, they give the three main major "
                "chords of the key. Click any key to see its chords lit, with the minor ones on the inner ring.</p>"
            ),
            circle="explore",
            make_task=neighbour_task,
        ),
        Step(
            title="What you can do now",
            text=(
                "<p>You can read the circle of fifths:</p>"
                "<ul>"
                "<li>Clockwise is a fifth up and one more sharp. Counterclockwise is a fifth down and one more flat.</li>"
                "<li>The number of steps from C is the number of sharps or flats.</li>"
                "<li>The inner ring has each major key's relative minor, with the same key signature.</li>"
                "<li>The neighbours of a key are its IV and its V.</li>"
                "</ul>"
                "<p>The Circle of Fifths exercise asks these things, and remembers the ones you find hard. The reference pane "
                "beside it holds this circle to look things up on.</p>"
            ),
            circle="rest",
            closing=True,
        ),
    ),
)
