"""A first lesson connecting a sound, a piano key, and a written note."""

from alto.lessons.base import Lesson, Staff, Step, Task

PITCHES_AND_NOTES = Lesson(
    key="pitches-and-notes",
    title="Pitches and Notes",
    category="Notation",
    about="Hear how high or low a sound is, find it on a keyboard, and see how it is written.",
    summary="Connect a sound, a piano key, and a note on the page.",
    exercise="KeyboardNotes",
    related_exercises=("NoteNames", "NoteConstruction", "NotationIdentification"),
    steps=(
        Step(
            title="High and low pitches",
            text=(
                "<p><b>Pitch</b> is how high or low a sound seems. Hum a comfortable sound, then hum a higher one. "
                "You changed its pitch. Musicians give pitches names so someone else can sing or play them.</p>"
                "<p>A <b>note</b> can mean a musical sound or the mark that tells you to play it. "
                "Listen to these two notes in order.</p>"
            ),
            hear=(("C4",), ("G4",)),
            hear_label="Hear the two notes",
            make_task=lambda _rng: Task(
                prompt="Which sound is higher?",
                choices=("First", "Second"),
                correct="Second",
                hint="Play the pair again and follow it with your voice.",
                explanation="The second sound is higher. On a piano you move to the right to play higher pitches.",
            ),
        ),
        Step(
            title="C on the piano keyboard",
            text=(
                "<p>On a piano the white keys use seven letter names. Starting on C and moving right, they go "
                "<b>C D E F G A B</b>, then begin again at C. The black keys form groups of two and three.</p>"
                "<p>Find the group of two black keys. The white key immediately to its left is C. "
                "Move one white key to the right of C. Which letter names the highlighted key?</p>"
            ),
            keyboard_note="D4",
            make_task=lambda _rng: Task(
                prompt="Name the highlighted white key.",
                choices=("B", "C", "D"),
                correct="D",
                hint="Start at C and read the letters in order.",
                explanation="D is the white key between the two black keys in this group.",
            ),
        ),
        Step(
            title="Octaves and note names",
            text=(
                "<p>Play C, then the next C above it. Both have the same letter name. The distance between them is "
                "an <b>octave</b>. To specify which C to play, add an octave number. "
                "<b>Middle C</b>, near the middle of a piano, is C4. The next C above it is C5.</p>"
                "<p>The number changes at C. The white keys from C4 through B4 share the number 4.</p>"
            ),
            keyboard_note="C5",
            hear=(("C4",), ("C5",)),
            hear_label="Hear middle C, then the highlighted C",
        ),
        Step(
            title="Notes on lines and spaces",
            text=(
                "<p>A <b>staff</b> has five lines. Read a note by the center of its oval, the <b>notehead</b>. "
                "The vertical stroke attached to this oval on some notes is the <b>stem</b>. "
                "Moving up from a line to the next space, or from a space to the next line, advances one letter.</p>"
                "<p>The sign at the left is a <b>clef</b>. It tells you which pitches belong on the staff. "
                "This is the <b>treble clef</b>. Its curl marks G4 on the second line from the bottom. "
                "Follow the two examples from that line to the space above it.</p>"
            ),
            staves=(Staff("treble", note="G4", caption="G4 on the second line"), Staff("treble", note="A4")),
            make_task=lambda _rng: Task(
                prompt="Which letter goes in the space just above G?",
                choices=("F", "G", "A"),
                correct="A",
                hint="The letter names repeat after G.",
                explanation="The space above G4 holds A4. To write A4, center its notehead in that space.",
            ),
        ),
        Step(
            title="Sharps, flats, and naturals",
            text=(
                "<p>The distance from a piano key to its immediate neighbor, counting black and white keys, "
                "is a <b>half step</b>. An <b>accidental</b> is a sign before a written note. A <b>sharp</b> (♯) "
                "raises the letter’s usual pitch by a half step. A <b>flat</b> (♭) lowers it by a half step. "
                "A <b>natural</b> (♮) restores the usual pitch.</p>"
                "<p>The highlighted black key is one half step above C. Listen to C and then C♯. "
                "To write C♯, keep the notehead in C’s place and add a sharp.</p>"
            ),
            keyboard_note="C#4",
            hear=(("C4",), ("C#4",)),
            hear_label="Hear C, then C sharp",
        ),
        Step(
            title="Reading and writing notes",
            text=(
                "<p>Try the same idea in either direction. On a keyboard, find a group of black keys and count to "
                "the highlighted note. On a staff, start at the clef’s known line and count letters to the notehead. "
                "To write a named note, count to its line or space, then place it there.</p>"
            ),
            closing=True,
        ),
    ),
)
