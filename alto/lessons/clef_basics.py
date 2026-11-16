"""
The lesson on clefs, taught from nothing.

It covers what a clef does, the three symbols (the G, C and F clef) and the line each clef puts them on, the way every C clef
points at middle C, and the rarer clefs.

Examples
--------
>>> len(CLEF_BASICS.steps)
10
>>> symbol_task(random.Random(1)).choices
('G clef', 'C clef', 'F clef')
"""

from __future__ import annotations

import random

from alto.lessons.base import (
    Lesson,
    Staff,
    Step,
    Task,
)
from alto.settings import (
    CLEF_NAMES,
    CLEF_SYMBOL_NAMES,
)

SYMBOLS = {"treble": "G", "bass": "F", "alto": "C", "tenor": "C", "soprano": "C", "mezzo": "C", "french": "G", "subbass": "F"}
LINES = ("Bottom line", "Second line", "Middle line", "Fourth line", "Top line")
LINE_OF = {"soprano": 0, "mezzo": 1, "alto": 2, "tenor": 3, "treble": 1, "bass": 3, "french": 0, "subbass": 4}  # counted from 0


def symbol_task(rng: random.Random) -> Task:
    """
    Ask which of the three symbols a clef is made with.

    Parameters
    ----------
    rng : random.Random
        Chooses the clef.

    Returns
    -------
    Task
        A clef drawn on a staff, and a button for each symbol.

    Examples
    --------
    >>> task = symbol_task(random.Random(2))
    >>> task.correct == CLEF_SYMBOL_NAMES[SYMBOLS[task.clef]]
    True
    """
    clef = rng.choice(["treble", "bass", "alto", "tenor", "mezzo", "soprano"])
    symbol = SYMBOLS[clef]
    return Task(
        prompt="Which symbol is this clef made with?",
        hint="Look at the shape: the G clef has a curl, the F clef has two dots, and the C clef is two curves facing the line.",
        explanation=f"It is the {CLEF_SYMBOL_NAMES[symbol]}: the {CLEF_NAMES[clef].lower()} clef is that symbol on one line.",
        choices=tuple(CLEF_SYMBOL_NAMES.values()),
        correct=CLEF_SYMBOL_NAMES[symbol],
        clef=clef,
    )


def identify_task(rng: random.Random) -> Task:
    """
    Ask which clef is drawn on a staff.

    Parameters
    ----------
    rng : random.Random
        Chooses the clef.

    Returns
    -------
    Task
        A clef drawn on a staff, and a button for each of the four everyday clefs.

    Examples
    --------
    >>> task = identify_task(random.Random(3))
    >>> task.correct in task.choices and task.clef != ""
    True
    """
    clef = rng.choice(["treble", "bass", "alto", "tenor"])
    where = LINES[LINE_OF[clef]].lower()
    return Task(
        prompt="Which clef is this?",
        hint="Work out the symbol first, then which line it is on.",
        explanation=f"It is the {CLEF_SYMBOL_NAMES[SYMBOLS[clef]]} on the {where}: the {CLEF_NAMES[clef].lower()} clef.",
        choices=tuple(CLEF_NAMES[c] for c in ("treble", "bass", "alto", "tenor")),
        correct=CLEF_NAMES[clef],
        clef=clef,
    )


def line_task(rng: random.Random) -> Task:
    """
    Ask which line of a blank staff a named clef is written on.

    Parameters
    ----------
    rng : random.Random
        Chooses the clef.

    Returns
    -------
    Task
        A blank staff, and a button for each line.

    Examples
    --------
    >>> task = line_task(random.Random(4))
    >>> task.correct in LINES and task.clef == ""
    True
    """
    clef = rng.choice(["treble", "bass", "alto", "tenor", "mezzo", "soprano"])
    return Task(
        prompt=f"On which line is the <b>{CLEF_NAMES[clef].lower()}</b> clef written?",
        hint="Count the lines from the bottom. The G clef circles the G line, the F clef has its dots round the F line, and a C "
        "clef is centred on middle C.",
        explanation=f"The {CLEF_NAMES[clef].lower()} clef is the {CLEF_SYMBOL_NAMES[SYMBOLS[clef]]} on the "
        f"{LINES[LINE_OF[clef]].lower()}.",
        choices=LINES,
        correct=LINES[LINE_OF[clef]],
    )


CLEF_BASICS = Lesson(
    key="clef-basics",
    title="Clef Basics",
    about="A walk through the clefs for a beginner: what a clef does, the three symbols (the G, C and F clef), the line each "
    "clef puts its symbol on, and how to tell them apart. Ten short steps with a few small exercises. Nothing is scored.",
    summary="Tell the clefs apart, from scratch.",
    category="Notation",
    exercise="ClefBasics",
    steps=(
        Step(
            title="What a clef does",
            text=(
                "<p>Music is written on five lines. But the lines do not mean a note by themselves: which note each line is "
                "depends on the <b>clef</b> at the start.</p>"
                "<p>The staves on the right have a note on the bottom line. In the treble clef it is E. In the bass clef it is "
                "G. The same place on the page is a different note.</p>"
                "<p>So a clef is a key to the staff, and you need it to read any note.</p>"
            ),
            staves=(
                Staff(clef="treble", note="E4", caption="Treble clef: the bottom line is E"),
                Staff(clef="bass", note="G2", caption="Bass clef: the bottom line is G"),
            ),
        ),
        Step(
            title="Three symbols",
            text=(
                "<p>Every clef is one of three symbols: the <b>G clef</b>, the <b>C clef</b> and the <b>F clef</b>. They are "
                "old, stylised letters.</p>"
                "<p>A clef is a symbol put on a particular line, and the symbol says which note that line is. The G clef "
                "says it is G, the F clef says F, and the C clef says <b>middle C</b>.</p>"
                "<p>So there are not many symbols to learn. The different clefs are the same three, put on different lines.</p>"
            ),
            staves=(
                Staff(clef="treble", caption="The G clef"),
                Staff(clef="alto", caption="The C clef"),
                Staff(clef="bass", caption="The F clef"),
            ),
        ),
        Step(
            title="The G clef",
            text=(
                "<p>The G clef has a curl that circles one line. That line is the G above middle C.</p>"
                "<p>On the <b>second</b> line, it is the <b>treble clef</b>, the clef of high voices and instruments such as "
                "the violin, flute and the right hand of the piano.</p>"
                "<p>On the <b>bottom</b> line it is the <b>French violin clef</b>, an old clef that put the G a line lower, "
                "to keep violin music on the staff.</p>"
            ),
            staves=(
                Staff(clef="treble", note="G4", caption="Treble clef: the G clef on the second line"),
                Staff(clef="french", caption="French violin clef: the G clef on the bottom line"),
            ),
        ),
        Step(
            title="The F clef",
            text=(
                "<p>The F clef has two dots, one above and one below a line. That line is the F below middle C.</p>"
                "<p>On the <b>fourth</b> line it is the <b>bass clef</b>, for low voices and instruments such as the cello "
                "and the left hand of the piano.</p>"
                "<p>On the <b>top</b> line it is the <b>subbass clef</b>, which is rarer. The <b>baritone clef</b> is the F "
                "clef on the <b>middle</b> line.</p>"
            ),
            staves=(
                Staff(clef="bass", note="F3", caption="Bass clef: the F clef on the fourth line"),
                Staff(clef="subbass", caption="Subbass clef: the F clef on the top line"),
            ),
        ),
        Step(
            title="The C clef and middle C",
            text=(
                "<p>The C clef is centred on a line, and that line is <b>middle C</b>. Its four common positions give four "
                "clefs, named for the voices they suited: <b>soprano</b> on the bottom line, <b>mezzo-soprano</b> on the "
                "second, <b>alto</b> on the middle and <b>tenor</b> on the fourth.</p>"
                "<p>Look at the staves on the right. The same note, middle C, is written on each, and each time it is on the "
                "line the clef is centred on. The alto clef is the one violas read.</p>"
            ),
            staves=(
                Staff(clef="soprano", note="C4", caption="Soprano: the bottom line"),
                Staff(clef="mezzo", note="C4", caption="Mezzo-soprano: the second line"),
                Staff(clef="alto", note="C4", caption="Alto: the middle line"),
                Staff(clef="tenor", note="C4", caption="Tenor: the fourth line"),
            ),
        ),
        Step(
            title="The rarer clefs",
            text=(
                "<p>Some clefs you will meet only now and then:</p>"
                "<ul>"
                "<li>The <b>French violin</b> clef, the G clef on the bottom line.</li>"
                "<li>The <b>subbass</b> clef, the F clef on the top line.</li>"
                "<li>The <b>baritone</b> clef, written two ways: the F clef on the middle line, or the C clef on the top "
                "line. They mean the same thing, and the Clef Basics exercise accepts both.</li>"
                "</ul>"
                "<p>They follow the same rule: a symbol on a line. Work out the symbol, then the line.</p>"
            ),
            staves=(
                Staff(clef="french", caption="French violin: the G clef on the bottom line"),
                Staff(clef="subbass", caption="Subbass: the F clef on the top line"),
            ),
        ),
        Step(
            title="Name the symbol",
            text=(
                "<p>Try the first half of the skill: which of the three symbols is this clef made with? Ignore the line for "
                "now. You cannot get it wrong: you will get a hint, then the answer.</p>"
            ),
            task_staff=True,
            make_task=symbol_task,
        ),
        Step(
            title="Find the line",
            text=(
                "<p>Now the second half: which line does a clef sit on? A named clef is shown, and the staff is blank. "
                "Count the lines from the bottom.</p>"
            ),
            task_staff=True,
            make_task=line_task,
        ),
        Step(
            title="Name the clef",
            text=(
                "<p>Now both halves: the symbol and the line. This is what the Clef Identification question asks. Work out "
                "the symbol, then find the line it is on.</p>"
            ),
            task_staff=True,
            make_task=identify_task,
        ),
        Step(
            title="What you can do now",
            text=(
                "<p>You can tell the clefs apart:</p>"
                "<ul>"
                "<li>There are three symbols: the G clef, the C clef and the F clef.</li>"
                "<li>The symbol says which note its line is: G, middle C or F.</li>"
                "<li>Treble is the G clef on the second line; bass is the F clef on the fourth; the C clefs are soprano, "
                "mezzo-soprano, alto and tenor from the bottom line up.</li>"
                "</ul>"
                "<p>The Clef Basics exercise asks you to put a clef on a blank staff, or to name one. The reference pane "
                "beside it holds a table of the clefs to look things up in.</p>"
            ),
            closing=True,
        ),
    ),
)
