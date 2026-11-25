"""A first rhythm lesson on counting the length of sound and silence."""

from alto.lessons.base import Lesson, Step, Task

DURATION = Lesson(
    key="duration",
    title="Duration",
    category="Rhythm",
    about="Count a steady beat to read how long to play and when to rest.",
    summary="Count note lengths and keep the beat through a rest.",
    exercise="RythmicEquations",
    steps=(
        Step(
            title="The beat and the quarter note",
            text=(
                "<p>Hum a short sound, then a long one. How long each lasts "
                "is its <b>duration</b>. A <b>beat</b> is the steady pulse "
                "you can tap as you listen. We can measure duration by "
                "counting beats.</p>"
                "<p>In this lesson, a <b>quarter note</b> lasts one beat. "
                "The stacked numbers <b>4/4</b> tell you to count four "
                "quarter-note beats in each group, called a <b>measure</b>. "
                "The vertical bar line marks its end.</p>"
                "<p>Find the quarter note’s filled oval. The thin line "
                "attached to it is the stem. Here a metronome click marks the "
                "start of each note. Tap with the four clicks as you "
                "count “one, two, three, four.” Start a hum on each tap.</p>"
            ),
            rhythm=("quarter",) * 4,
            hear_label="Hear four quarter notes",
        ),
        Step(
            title="The half note",
            text=(
                "<p>A <b>half note</b> lasts as long as two quarter notes. "
                "Its oval is open and it has a stem. Find the half note "
                "at the start of this example. The two filled ovals after "
                "it are quarter notes.</p>"
                "<p>Tap four times at the same speed as before. Start "
                "humming at the first click, keep humming through beat two, "
                "then hum again with the clicks on three and four.</p>"
            ),
            rhythm=("half", "quarter", "quarter"),
            hear_label="Hear the rhythm",
            single_question=True,
            make_task=lambda _rng: Task(
                prompt="On which beat does the first quarter note begin?",
                choices=("Beat 2", "Beat 3", "Beat 4"),
                correct="Beat 3",
                hint="Count both beats of the open oval before moving on.",
                explanation="The half note takes beats 1 and 2. The first "
                "quarter note begins on beat 3.",
            ),
        ),
        Step(
            title="The whole note",
            text=(
                "<p>A <b>whole note</b> is an open oval without a stem. "
                "It lasts as long as two half notes or four quarter notes."
                "</p><p>One click starts the whole note. Hold your hum as "
                "you tap two, three, four. All four taps fit inside one "
                "note.</p>"
            ),
            rhythm=("whole",),
            hear_label="Count a whole note",
        ),
        Step(
            title="The quarter rest",
            text=(
                "<p>A <b>rest</b> marks time spent silent. Find the "
                "zigzag symbol between the two notes. It is a <b>quarter "
                "rest</b> and takes the same time as a quarter note.</p>"
                "<p>Keep tapping all four beats. Hum on one, go quiet on "
                "two, then start a half note on three and hold it through "
                "four. Listen for clicks on one and three.</p>"
            ),
            rhythm=("quarter", "quarter-rest", "half"),
            hear_label="Hear the rhythm with a rest",
            single_question=True,
            make_task=lambda _rng: Task(
                prompt="If you put a quarter note in place of the rest, "
                "what happens on beat 2?",
                choices=("A note sounds", "The beat disappears"),
                correct="A note sounds",
                hint="Tap once for a quarter rest and once for a quarter "
                "note. Which one would you hum?",
                explanation="You play a sound on beat 2. Both symbols last "
                "one beat, so the half note still starts on beat 3.",
            ),
        ),
        Step(
            title="Four beats of rhythm",
            text=(
                "<p>Try this rhythm before you play it. Read the three "
                "symbols from left to right. Tap four steady beats, hum "
                "the notes, and keep tapping through the rest. Then play "
                "the example to check your timing.</p>"
                "<p>In the practice exercise, fill in the blank so both "
                "sides of the equation last equally long."
                "</p>"
            ),
            rhythm=("half", "quarter-rest", "quarter"),
            hear_label="Check the rhythm",
            single_question=True,
            make_task=lambda _rng: Task(
                prompt="On which beat do you start humming again?",
                choices=("Beat 2", "Beat 3", "Beat 4"),
                correct="Beat 4",
                hint="Count two beats for the half note and one for the rest.",
                explanation="Hold the half note through beats 1 and 2, "
                "rest on beat 3, and play the quarter note on beat 4.",
            ),
            closing=True,
        ),
    ),
)
