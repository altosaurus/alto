"""A guided lesson on reading and writing key signatures."""

from __future__ import annotations

import random

from alto.lessons.base import Lesson, Staff, Step, Task
from alto.theory.pitch import MAJOR_KEYS
from alto.theory.scales import format_key_signature, mode_tonic


def _read_signature(rng: random.Random) -> Task:
    """
    Draw a signature and ask for the tonic in major or minor.

    Parameters
    ----------
    rng : random.Random
        Generator for the signature, mode, clef, and answer choices.

    Returns
    -------
    Task
        A staff-reading question with feedback for the displayed signature.
    """
    count = rng.randint(-7, 7)
    major = MAJOR_KEYS[count]
    minor = mode_tonic(count, mode="Natural minor (Aeolian)").name
    mode = rng.choice(("major", "minor"))
    correct = major if mode == "major" else minor
    other = rng.choice([name for name in MAJOR_KEYS.values() if name not in (major, minor)])
    return Task(
        clef=rng.choice(("treble", "bass")),
        key=count,
        prompt=f"In a {mode} key, what tonic goes with this signature?",
        choices=tuple(rng.sample([major, minor, other], 3)),
        correct=correct,
        hint="Find the major key first. If the question asks for minor, count up to the sixth note of that major scale.",
        explanation=f"This staff has {format_key_signature(count)}. {major} major and {minor} minor share that signature.",
    )


KEY_SIGNATURES = Lesson(
    key="key-signatures",
    title="Key Signatures",
    category="Scales & Keys",
    about="Read the sharps or flats after a clef and work out which ones to write for a given key.",
    summary="Read and build major and minor key signatures.",
    exercise="KeySignatures",
    related_exercises=("KeySignatureConstruction", "OrderOfKeys"),
    steps=(
        Step(
            title="Two ways to write F sharp",
            text=(
                "<p>Look at the F on the top line of each staff. On the first staff, a sharp just before the note "
                "raises it by a half step. On the second staff, the sharp sits just after the clef. Both notes sound "
                "like F♯.</p>"
                "<p>The sharps or flats grouped after the clef form the <b>key signature</b>. A sharp on F there "
                "tells you to play every F sharp, in every octave, unless a sign beside a note says otherwise.</p>"
            ),
            staves=(Staff("treble", "F#5", "Sharp beside the note"), Staff("treble", "F#5", "Sharp in the signature", 1)),
            hear=(("F#5",),),
            hear_label="Hear F sharp",
        ),
        Step(
            title="A natural beside the note",
            text=(
                "<p>Both staves still have F♯ in the signature. This time the F is in the bottom space, an octave "
                "lower. Read the first note using the signature. On the second staff, a <b>natural</b> (♮) beside "
                "the note cancels the sharp. Listen for the half step down.</p>"
                "<p>The natural applies to that F and any later F in the same octave until the next <b>barline</b>, "
                "unless another sign changes it sooner. Barlines are vertical lines that divide the staff into sections "
                "called <b>measures</b>.</p>"
            ),
            staves=(Staff("treble", "F#4", "First staff", 1), Staff("treble", "F4", "Second staff", 1)),
            hear=(("F#4",), ("F4",)),
            hear_label="Hear the two notes",
            make_task=lambda _rng: Task(
                prompt="After the barline, how would you play an F with no sign beside it?",
                choices=("F♭", "F", "F♯"),
                correct="F♯",
                hint="Look at the signature that is still in effect.",
                explanation="The natural lasted through its measure. The signature still calls for F♯.",
            ),
        ),
        Step(
            title="Major keys with sharps",
            text=(
                "<p>A key takes its name from its <b>tonic</b>, the note that feels like home. To find a major tonic "
                "from a sharp signature, read the last sharp on the right and go up one half step.</p>"
                "<p>Sharps appear in this order: <b>F C G D A E B</b>. On the first staff the only sharp is F♯. "
                "A half step above F♯ is G, so this is G major. The second staff adds C♯. A half step above C♯ "
                "is D, giving D major.</p>"
            ),
            staves=(Staff("treble", key=1, caption="G major"), Staff("treble", key=2, caption="D major")),
        ),
        Step(
            title="Major keys with flats",
            text=(
                "<p>Flats appear in the reverse order: <b>B E A D G C F</b>. With two or more flats, the "
                "<b>next-to-last flat</b> names the major key. On the second staff the flats are B♭, E♭, A♭. "
                "The middle one is E♭, so the key is E♭ major.</p>"
                "<p>Two signatures are worth remembering on their own. One flat (B♭) belongs to F major. "
                "C major has no sharps or flats.</p>"
            ),
            staves=(Staff("treble", key=-1, caption="F major"), Staff("treble", key=-3, caption="E♭ major")),
        ),
        Step(
            title="One signature, two tonics",
            text=(
                "<p>Play the notes of G major starting on its sixth note, E, and you have the E natural minor scale. "
                "Both scales use F♯. Keys paired this way are called <b>relative major and minor</b>. "
                "Their signatures match, but a different note feels like home.</p>"
                "<p>On this staff there are no sharps or flats. For the major key, start on C. "
                "For its relative minor, count six notes from C, counting C as one.</p>"
            ),
            staves=(Staff("bass", caption="No sharps or flats"),),
            make_task=lambda _rng: Task(
                prompt="What is the tonic if the music is in minor?",
                choices=("C", "E", "A"),
                correct="A",
                hint="Count C, D, E, F, G, A.",
                explanation="A is the sixth note of C major. C major and A minor share the empty signature.",
            ),
        ),
        Step(
            title="The signature for a given key",
            text=(
                "<p>To write a sharp signature, stop when you reach the sharp a half step below the major tonic. "
                "For D major, stop at C♯. Write F♯ and C♯.</p>"
                "<p>For a major key named with a flat, write the flats in order until you reach the tonic, "
                "then add one more. For E♭ major, write B♭, E♭, then A♭. Try the same method for A♭ major.</p>"
                "<p>For a minor key, first find its relative major a minor third (three half steps) above the tonic. "
                "From B, count C, C♯, D. B minor uses the same two sharps as D major.</p>"
            ),
            staves=(
                Staff("treble", key=-3, caption="A"),
                Staff("treble", key=-4, caption="B"),
                Staff("treble", key=4, caption="C"),
            ),
            make_task=lambda _rng: Task(
                prompt="Which staff has the signature you would write for A♭ major?",
                choices=("A", "B", "C"),
                correct="B",
                hint="Read B♭, E♭, A♭, then add D♭.",
                explanation="Staff B has four flats. A♭ is the next-to-last flat.",
            ),
        ),
        Step(
            title="Key signatures in treble and bass clefs",
            text=(
                "<p>Changing clefs moves the signs to different lines and spaces. Their letters and their order stay "
                "the same. Read the signature, then use the major or minor cue in the question to decide on a tonic.</p>"
            ),
            task_staff=True,
            make_task=_read_signature,
        ),
        Step(
            title="Reading and writing key signatures",
            text=(
                "<p>In <b>Key Signature Identification</b>, read the marks after the clef and choose the tonic "
                "for the scale named under the staff.</p>"
                "<p>In <b>Key Signature Construction</b>, start with the named key. Choose the number of sharps or "
                "flats to put on the staff, or choose ♮ for an empty signature, then press <b>Answer</b>.</p>"
            ),
            closing=True,
        ),
    ),
)
