"""Reading scales and recognizing their interval patterns."""

from alto.lessons.base import (
    Lesson,
    Step,
    Task,
)

SCALE_PATTERNS = {
    "Major (Ionian)": "W W H W W W H",
    "Dorian": "W H W W W H W",
    "Phrygian": "H W W W H W W",
    "Lydian": "W W W H W W H",
    "Mixolydian": "W W H W W H W",
    "Natural minor (Aeolian)": "W H W W H W W",
    "Locrian": "H W W H W W W",
    "Harmonic minor": "W H W W H 3H H",
    "Melodic minor": "W H W W W W H",
}

SCALE_IDENTIFICATION = Lesson(
    key="scale-identification",
    title="Scale Identification",
    about="Learn how to name a scale by its home note and the distances between its notes.",
    summary="Recognize scales and modes on the staff.",
    category="Scales & Keys",
    exercise="ScaleIdentification",
    steps=(
        Step(
            title="The tonic",
            scale="Major (Ionian)",
            scale_tonic="D4",
            scale_explore=False,
            single_question=True,
            make_task=lambda _rng: Task(
                prompt="What is the tonic of the scale shown?",
                choices=("C", "D", "F♯"),
                correct="D",
                hint="Read the first and last notes on the staff.",
                explanation="Both are D: the scale begins on D4 and ends on D5.",
            ),
            text=(
                "<p>A <b>scale</b> is a set of notes arranged from low to high or high to low. Its <b>tonic</b> is the "
                "note that feels like home. These examples begin on the tonic and end an <b>octave</b> higher, "
                "at the next note of the same name. C4 (middle C) and C5 are two such Cs. The number tells you which octave.</p>"
                "<p>Each note has a numbered place called a <b>scale degree</b>. Count the tonic as 1. "
                "The marks between notes show the size of each step. A <b>half step</b> (H), or <b>semitone</b>, "
                "goes to the very next piano key, counting black and white keys. A <b>whole step</b> (W) spans two "
                "half steps.</p>"
                "<p>An <b>accidental</b> is a sign beside a note. A <b>sharp</b> (♯) raises its letter’s usual pitch "
                "by a half step, a <b>flat</b> (♭) lowers it by a half step, and a <b>natural</b> (♮) restores it. "
                "Include any sign that applies when you name the tonic.</p>"
            ),
        ),
        Step(
            title="The major scale pattern",
            scale="Major (Ionian)",
            text=(
                "<p>A <b>major scale</b> follows the pattern W W H W W W H going up. "
                "Play C major on the white piano keys and its two half steps fall at E–F and B–C. "
                "A <b>key signature</b> is a group of sharps or flats after the clef that applies to those letters "
                "in every octave. Account for the signature and any accidental beside a note when counting steps.</p>"
                "<p>Click each gap below the staff to hear its notes. Find the two half steps in C major, then change "
                "the tonic to D: the written notes change but the pattern stays W W H W W W H.</p>"
            ),
            hear=tuple((n,) for n in ("C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5")),
        ),
        Step(
            title="Three forms of the minor scale",
            scale="Natural minor (Aeolian)",
            scale_tonic="A4",
            text=(
                "<p>A <b>natural minor scale</b> follows a different pattern going up: <b>W H W W H W W</b>. "
                "From A, that gives A B C D E F G A.</p>"
                "<p>Harmonic minor raises natural minor’s seventh degree by a half step (G becomes G♯ in A minor): "
                "<b>W H W W H 3H H</b>. "
                "Here F and G♯ are neighboring letter names three half steps apart. This distance is an "
                "<b>augmented second</b> (3H).</p>"
                "<p><b>Ascending</b> means moving up in pitch. Ascending melodic minor raises degrees 6 and 7 by a "
                "half step each: <b>W H W W W W H</b>. "
                "The scale explorer shows the ascending form. Switch between the three minor types on the right; "
                "watch degrees 6 and 7, and click the 3H gap in harmonic minor to hear it.</p>"
            ),
        ),
        Step(
            title="Modes and their scale degrees",
            scale="Dorian",
            scale_tonic="D4",
            text=(
                "<p>A <b>mode</b> is a scale pattern defined by how its steps are arranged around the tonic. "
                "Keep the home note the same to hear what changes. Compared with major, Lydian raises 4 and "
                "Mixolydian lowers 7. Compared with natural minor, "
                "Dorian raises 6, Phrygian lowers 2, and Locrian lowers 2 and 5.</p>"
                "<p>Ionian is major; Aeolian is natural minor. Keep the tonic fixed and switch between Dorian "
                "and natural minor to see degree 6 move. Then compare major with Lydian and Mixolydian.</p>"
            ),
        ),
        Step(
            title="A scale’s pattern of steps",
            scale="Dorian",
            scale_tonic="D4",
            scale_explore=False,
            text="<p>Identify the scale from its seven gaps.</p>",
            single_question=True,
            make_task=lambda _rng: Task(
                prompt="Which scale type is shown on the staff?",
                choices=("Dorian", "Major", "Natural minor"),
                correct="Dorian",
                hint="Its sixth degree is raised compared with natural minor.",
                explanation="Dorian has half steps between degrees 2–3 and 6–7.",
            ),
        ),
        Step(
            title="The tonic and scale type",
            scale="Harmonic minor",
            scale_tonic="A4",
            scale_explore=False,
            single_question=True,
            make_task=lambda _rng: Task(
                prompt="Identify this scale, including its tonic.",
                choices=("A natural minor", "A harmonic minor", "C major"),
                correct="A harmonic minor",
                hint="Start on A. Look for the G♯ and the three-semitone gap above F.",
                explanation="A harmonic minor raises G to G♯, giving the pattern W H W W H 3H H.",
            ),
            text=(
                "<p>Read the tonic, apply the signature and accidentals, then compare the seven gaps with a scale pattern. "
                "Choose the matching tonic and type.</p><p>Use the exercise settings to focus on particular clefs, "
                "staff keys, scale keys and scale types. The reference pane lists the patterns.</p>"
            ),
            closing=True,
        ),
    ),
)
