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
    about="Read the tonic and recognize major, minor and modal step patterns.",
    summary="Recognize scales and modes on the staff.",
    category="Scales & Keys",
    exercise="ScaleIdentification",
    steps=(
        Step(
            title="Find the tonic",
            scale="Major (Ionian)",
            scale_tonic="D4",
            scale_explore=False,
            make_task=lambda _rng: Task(
                prompt="What is the tonic of the scale shown?",
                choices=("C", "D", "F♯"),
                correct="D",
                hint="Read the first and last notes on the staff.",
                explanation="Both are D: the scale begins on D4 and ends on D5.",
            ),
            text=(
                "<p>The exercise shows a scale from its tonic to the same note an octave away. "
                "Read the clef and name the first note, including its accidental: that is the scale key.</p>"
                "<p>The staff key signature does not by itself identify the scale. Apply its sharps or flats, "
                "then any accidentals written beside the notes.</p>"
            ),
        ),
        Step(
            title="Count the steps",
            scale="Major (Ionian)",
            text=(
                "<p>A half step (H) is one semitone; a whole step (W) is two. Natural E–F and B–C are half steps. "
                "Include all sharps and flats when counting the seven gaps.</p>"
                "<p>Click each gap below the staff to hear its notes. Find the two half steps in C major, then change "
                "the tonic to D: the written notes change but the pattern stays W W H W W W H.</p>"
            ),
            hear=tuple((n,) for n in ("C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5")),
        ),
        Step(
            title="Major and minor",
            scale="Natural minor (Aeolian)",
            scale_tonic="A4",
            text=(
                "<p>Major: <b>W W H W W W H</b>. Natural minor: <b>W H W W H W W</b>.</p>"
                "<p>Harmonic minor raises natural minor's seventh degree: <b>W H W W H 3H H</b>. "
                "3H means three semitones, an augmented second.</p>"
                "<p>Ascending melodic minor raises degrees 6 and 7: <b>W H W W W W H</b>. "
                "The scale explorer shows the ascending form. Switch between the three minor types on the right; "
                "watch degrees 6 and 7, and click the 3H gap in harmonic minor to hear it.</p>"
            ),
        ),
        Step(
            title="Recognize modes",
            scale="Dorian",
            scale_tonic="D4",
            text=(
                "<p>Compared with major, Lydian raises 4 and Mixolydian lowers 7. Compared with natural minor, "
                "Dorian raises 6, Phrygian lowers 2, and Locrian lowers 2 and 5.</p>"
                "<p>Ionian is major; Aeolian is natural minor. Keep the tonic fixed and switch between Dorian "
                "and natural minor to see degree 6 move. Then compare major with Lydian and Mixolydian.</p>"
            ),
        ),
        Step(
            title="Try a pattern",
            scale="Dorian",
            scale_tonic="D4",
            scale_explore=False,
            text="<p>Identify the scale from its seven gaps.</p>",
            make_task=lambda _rng: Task(
                prompt="Which scale type is shown on the staff?",
                choices=("Dorian", "Major", "Natural minor"),
                correct="Dorian",
                hint="Its sixth degree is raised compared with natural minor.",
                explanation="Dorian has half steps between degrees 2–3 and 6–7.",
            ),
        ),
        Step(
            title="Read, compare, identify",
            scale="Harmonic minor",
            scale_tonic="A4",
            scale_explore=False,
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
