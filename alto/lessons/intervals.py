"""A guided introduction to naming intervals on the staff and keyboard."""

from __future__ import annotations

import random

from alto.lessons.base import Lesson, Step, Task


def _name_pair(rng: random.Random) -> Task:
    """
    Choose an ascending pair for the learner to name.

    Returns
    -------
    Task
        An interval question with feedback for that pair.
    """
    low, high, letters, half_steps, answer = rng.choice(
        (
            ("D", "F", "D E F", 3, "m3"),
            ("F", "A", "F G A", 4, "M3"),
            ("D", "G", "D E F G", 5, "P4"),
            ("F", "C", "F G A B C", 7, "P5"),
        ),
    )
    return Task(
        prompt=f"From {low} up to the nearest {high}, what is the interval?",
        choices=("m3", "M3", "P4", "P5"),
        correct=answer,
        hint=f"Count {letters}. Then count the half steps, including the black keys.",
        explanation=f"Count {letters} for the number. The distance is {half_steps} half steps, so the answer is {answer}.",
    )


INTERVALS = Lesson(
    key="intervals",
    title="Intervals",
    category="Intervals",
    about="Name the distance between two pitches by counting letter names and half steps.",
    summary="Read and hear intervals on the staff and keyboard.",
    exercise="IntervalNames",
    related_exercises=("KeyboardIntervals",),
    steps=(
        Step(
            title="Count both notes",
            text=(
                "<p>An <b>interval</b> is the distance between two pitches. Its <b>number</b> counts the letter names "
                "from one note to the other, including both ends. From G up to B, count G (1), A (2), B (3). "
                "That makes G to B a <b>third</b>.</p>"
                "<p>Find G on the second line of the treble staff. The next space is A, and the line above it is B. "
                "Going from G up to B is <b>ascending</b>. Going from B down to G is <b>descending</b>.</p>"
            ),
            hear=(("G4",), ("B4",)),
            hear_label="Hear G, then B",
            hear_display="staff",
            make_task=lambda _rng: Task(
                prompt="What is the interval number going from B down to G?",
                choices=("Second", "Third", "Fourth"),
                correct="Third",
                hint="Start at B and count it as one.",
                explanation="B, A, G spans three letters in the downward direction.",
            ),
        ),
        Step(
            title="Measure a third on the keyboard",
            text=(
                "<p>From C up to E is another third. Its <b>quality</b> tells us more about its size. "
                "Measure it in <b>half steps</b>, also called <b>semitones</b>. Moving to the very next key, black or white, "
                "is one half step. Start at zero on C.</p>"
                "<p>Follow C → C♯ → D → D♯ → E. Those four moves make C to E a <b>major third</b>, written "
                "<b>M3</b>. A third spanning three half steps is a <b>minor third</b>, written <b>m3</b>.</p>"
            ),
            hear=(("C4",), ("E4",)),
            hear_label="Hear C, then E",
            hear_display="keyboard",
        ),
        Step(
            title="Lower the upper note",
            text=(
                "<p>On the treble staff, start at E on the bottom line. The space just below it is D. One step lower, "
                "middle C sits on a short extra line called a <b>ledger line</b>.</p>"
                "<p>Keep C in place and lower E to E♭. Its notehead stays on E’s line, "
                "and the flat lowers its pitch by one half step. Listen to the new pair.</p>"
            ),
            hear=(("C4",), ("Eb4",)),
            hear_label="Hear C, then E flat",
            hear_display="staff",
            make_task=lambda _rng: Task(
                prompt="Which interval do C and E♭ now form?",
                choices=("M3", "m3", "Second"),
                correct="m3",
                hint="Count C, D, E for the number. Subtract one half step from the original four.",
                explanation="The letter span is still a third. Its three half steps make it a minor third.",
            ),
        ),
        Step(
            title="Perfect intervals",
            text=(
                "<p>Different interval numbers use different quality names. For thirds, we used major and minor. "
                "For fourths and fifths, the usual starting quality is <b>perfect</b> (P). "
                "A perfect fourth (P4) spans five half steps. A perfect fifth (P5) spans seven.</p>"
                "<p>Count C, D, E, F, G on the staff. C to G is a fifth, and its seven half steps make it perfect. "
                "Here the notes sound together, forming a <b>harmonic</b> interval. Playing the notes one after the other "
                "makes a <b>melodic</b> interval. Both ways of playing C and G give a perfect fifth.</p>"
                "<p>The same pitch with the same name gives a <b>perfect unison</b> (P1, zero half steps). "
                "From C to the next C above it is a <b>perfect octave</b> (P8, twelve half steps).</p>"
            ),
            hear=(("C4", "G4"),),
            hear_label="Hear C and G together",
            hear_display="staff",
        ),
        Step(
            title="Seconds, sixths, and sevenths",
            text=(
                "<p>Seconds, sixths, and sevenths also come in major and minor sizes. "
                "Count up from C to the nearest D. Two letters give a second. On the keyboard, C → C♯ → D "
                "gives two half steps, a major second (M2). C to D♭ is one half step, a minor second (m2).</p>"
                "<p>You can use these sizes for intervals starting on any note. The major intervals span "
                "2 half steps (M2), 4 (M3), 9 (M6), and 11 (M7). For the minor interval with the same number, "
                "subtract one half step.</p>"
            ),
            hear=(("C4",), ("D4",)),
            hear_display="keyboard",
            hear_label="Hear a major second",
            make_task=lambda _rng: Task(
                prompt="C up to B is a major seventh. How many half steps separate C and B♭?",
                choices=("9", "10", "11"),
                correct="10",
                hint="Start with the eleven half steps of a major seventh and lower B by one.",
                explanation="Eleven minus one is ten. C to B♭ is a minor seventh (m7).",
            ),
        ),
        Step(
            title="What the spelling tells you",
            text=(
                "<p>Widen a perfect or major interval by one half step while keeping its letter span, and its quality "
                "becomes <b>augmented</b> (A). Narrow a perfect or minor interval by one half step and it becomes "
                "<b>diminished</b> (d).</p>"
                "<p>From C to F is a perfect fourth. Raise F to F♯ and you get an augmented fourth (A4). "
                "From C to G is a perfect fifth. Lower G to G♭ and you get a diminished fifth (d5). "
                "F♯ and G♭ are two names for the same black key. The keyboard exercise accepts this distance "
                "with the combined label <b>A4 / d5</b>. On the staff the letter names tell you which one to choose.</p>"
            ),
            hear=(("C4",), ("F#4",)),
            hear_display="keyboard",
            hear_label="Hear the six-half-step interval",
            make_task=lambda _rng: Task(
                prompt="If the upper note is written G♭, which name fits the interval above C?",
                choices=("A4", "d5"),
                correct="d5",
                hint="Count from C to the written letter G, including both letters.",
                explanation="C, D, E, F, G gives a fifth. The flat narrows the perfect fifth to a diminished fifth.",
            ),
        ),
        Step(
            title="Name a new pair",
            text=(
                "<p>Start with the letters to find the number, then count the half steps to find the quality. "
                "For this check, use three half steps for m3, four for M3, five for P4, and seven for P5. "
                "On the white keys, E to F and B to the next C each take one half step. "
                "Every other neighboring pair of white keys has a black key between them and takes two half steps.</p>"
            ),
            make_task=_name_pair,
        ),
        Step(
            title="Practice identifying intervals",
            text=(
                "<p>In <b>Interval Identification</b>, read the two notes on the staff and name their interval. "
                "In <b>Keyboard Interval Identification</b>, count from the lower highlighted key to the higher one. "
                "To practice the sizes used in the last step, select m3, M3, P4, and P5 in the keyboard exercise settings.</p>"
            ),
            closing=True,
        ),
    ),
)
