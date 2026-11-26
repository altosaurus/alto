"""A searchable glossary of the notation terms used in Alto."""

from dataclasses import dataclass
from itertools import pairwise
from math import ceil

from PySide6.QtCore import QSize, QSizeF, Qt, Signal
from PySide6.QtGui import (
    QHideEvent,
    QIcon,
    QKeySequence,
    QResizeEvent,
    QShortcut,
)
from PySide6.QtWidgets import (
    QBoxLayout,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from alto.audio import sounds
from alto.exercises import REGISTRY
from alto.lessons import LESSONS
from alto.settings import RHYTHM_DURATIONS
from alto.terms import (
    PLUGIN_TERMS,
    PluginTerm,
)
from alto.theory.pitch import Note
from alto.ui.fingerboard import FingerboardWidget
from alto.ui.home import ExerciseCard, lesson_card
from alto.ui.icons import SEARCH, set_svg_icon
from alto.ui.keyboard import KeyboardWidget
from alto.ui.meter_staff import MeterStaff
from alto.ui.reference import ExplorableCircle
from alto.ui.staff import StaffWidget
from alto.ui.staff_playback import StaffPlayback
from alto.ui.widgets import SegmentedControl
from alto.ui.zoom import px

_STEP_LABELS = {1: "H", 2: "W", 3: "3H"}
PLUGIN_ROLE = (
    Qt.ItemDataRole.UserRole
)  # the name of a plugin's entry, on its row in the list


@dataclass(frozen=True)
class _Example:
    """
    A caption and the spelled pitches to display and play, in reading
    order.

    Pitches are separated by spaces and sound one after another. Join
    pitches with "+" to stack them in one column, so that
    they are written and sound together, as in "C4+G4". A rhythm
    with empty pitches plays clicks at its written onsets.
    """

    pitches: str
    caption: str
    clef: str = "treble"
    signature: int = 0
    rhythm: str = ""
    bpm: int = 100
    meter: tuple[int, int] | None = None
    counts: tuple[str, ...] = ()
    bar_line: str = ""
    click_levels: tuple[float, ...] = ()

    @property
    def beat_ms(self) -> int | None:
        """Return the pulse interval for counted examples."""
        if not self.rhythm or not self.pitches:
            return None
        quarter_ms = 60_000 / self.bpm
        if self.meter in ((6, 8), (9, 8), (12, 8)):
            return round(1.5 * quarter_ms)
        return round(quarter_ms)

    def durations_ms(self) -> tuple[int, ...]:
        """
        Convert written rhythm into playback timing.

        Returns
        -------
        tuple of int
            Milliseconds per sounding note, combining tied values.
        """
        quarter = RHYTHM_DURATIONS["quarter"]
        return tuple(
            round(
                60_000
                / self.bpm
                * sum(RHYTHM_DURATIONS[v] for v in group.split("~"))
                / quarter,
            )
            for group in self.rhythm.split()
        )


@dataclass(frozen=True, kw_only=True)
class _Term:
    """
    Keep the explanation, demonstration, and practice material for one
    concept together.
    """

    definition: str
    guide: str
    examples: tuple[_Example, ...]
    exercises: tuple[str, ...]
    lesson: str | None = None
    keyboard: bool = False
    label_steps: bool = False
    circle: bool = False


def _meter_example(
    beats: int,
    *,
    divisions: int = 1,
    bars_per_group: int = 1,
) -> _Example:
    """
    Build two groups of counted measures at the same tapping speed.

    Parameters
    ----------
    beats : int
        Main beats in each measure.
    divisions : int
        Sound one pulse, two equal parts, or three equal parts per beat.
    bars_per_group : int
        Measures per group. A louder downbeat marks each group’s start.

    Returns
    -------
    _Example
        Counts, click levels, note values, and time signature.
    """
    syllables = {1: (), 2: ("&",), 3: ("la", "li")}[divisions]
    levels = []
    counts = []
    for bar in range(bars_per_group):
        for beat in range(1, beats + 1):
            level = 0.6
            if beat == 1:
                level = 1.0 if bar == 0 else 0.8
            elif beats == 4 and beat == 3:
                level = 0.8
            levels.append(level)
            levels.extend([0.35] * len(syllables))
            counts.extend((str(beat), *syllables))
    value = "quarter" if divisions == 1 else "eighth"
    meter = (beats * 3, 8) if divisions == 3 else (beats, 4)
    caption = f"{meter[0]}/{meter[1]} · {beats} beats per measure"
    if divisions > 1:
        caption += f" · {divisions} sounds per beat"
    if bars_per_group > 1:
        caption += f" · {bars_per_group}-measure groups"
    return _Example(
        "",
        caption,
        rhythm=" ".join([value] * (len(counts) * 2)),
        # At 150 quarters per minute, a dotted quarter lasts 600 ms too.
        bpm=150 if divisions == 3 else 100,
        meter=meter,
        counts=tuple(counts * 2),
        click_levels=tuple(levels * 2),
    )


TERMS = {
    "musical alphabet": _Term(
        definition="The musical alphabet uses seven letter names for notes. "
        "In ascending order they are A, B, C, D, E, F, and G. "
        "After G, the names start again at A.",
        guide="Say each letter as its note sounds. On the way up, listen "
        "for G moving to A. On the way down, A leads back to G.",
        examples=(
            _Example("C4 D4 E4 F4 G4 A4 B4 C5", "Ascending · C D E F G A B C"),
            _Example(
                "C5 B4 A4 G4 F4 E4 D4 C4",
                "Descending · C B A G F E D C",
            ),
        ),
        exercises=("NoteNames", "KeyboardNotes"),
        lesson="pitches-and-notes",
    ),
    "piano keyboard": _Term(
        definition="A piano keyboard arranges pitches from low on the left "
        "to high on the right. The black keys repeat in groups of two "
        "and three.",
        guide="Find the pair of black keys. The white key immediately to "
        "their left is C. Switch examples and use the group of three "
        "black keys to find F the same way.",
        examples=(
            _Example("C4", "C · just left of two black keys"),
            _Example("F4", "F · just left of three black keys"),
        ),
        exercises=("KeyboardNotes",),
        lesson="pitches-and-notes",
        keyboard=True,
    ),
    "middle C": _Term(
        definition="Middle C is the C near the center of a piano keyboard. "
        "Its name in scientific pitch notation is C4.",
        guide="Switch clefs and listen. The same piano key is written on "
        "the first short line below the treble staff or the first short "
        "line above the bass staff.",
        examples=(
            _Example("C4", "Middle C below the treble staff"),
            _Example("C4", "Middle C above the bass staff", clef="bass"),
        ),
        exercises=("KeyboardNotes", "NoteConstruction"),
        lesson="clef-basics",
    ),
    "parallel minor": _Term(
        definition="The parallel minor of a major key is the minor key "
        "with the same home note, or tonic. C minor is the parallel "
        "minor of C major.",
        guide="Play C major, then switch to C natural minor. Both scales "
        "begin and end on C. Listen for E, A, and B moving down a half "
        "step to E♭, A♭, and B♭.",
        examples=(
            _Example("C4 D4 E4 F4 G4 A4 B4 C5", "C major"),
            _Example(
                "C4 D4 Eb4 F4 G4 Ab4 Bb4 C5",
                "C natural minor",
                signature=-3,
            ),
        ),
        exercises=("ScaleIdentification", "KeySignatures"),
        lesson="key-signatures",
    ),
    "rhythm": _Term(
        definition="Rhythm is the pattern of sounds and silences in time. "
        "It includes when notes begin and how long they last.",
        guide="Tap four steady beats. Each click starts a note. In the first "
        "example, the clicks fall on 1, 3, and 4. In the second, they fall "
        "on 1, 2, and 3. Keep tapping while the long note is highlighted.",
        examples=(
            _Example(
                "",
                "Long, short, short · count 1–2, 3, 4",
                rhythm="half quarter quarter",
            ),
            _Example(
                "",
                "Short, short, long · count 1, 2, 3–4",
                rhythm="quarter quarter half",
            ),
        ),
        exercises=("RythmicEquations",),
        lesson="duration",
    ),
    "tie": _Term(
        definition="A tie is a curved line joining two notes of the same "
        "pitch. Play the first note and hold it for the combined length "
        "of both notes.",
        guide="Count three clicks. In the first example C sounds on clicks "
        "one and two. In the tied example C holds through the second "
        "click. G enters on the third click both times.",
        examples=(
            _Example(
                "C4 C4 G4",
                "Two separate Cs, then G",
                rhythm="quarter quarter quarter",
                meter=(3, 4),
            ),
            _Example(
                "C4 G4",
                "Two tied Cs, then G",
                rhythm="quarter~quarter quarter",
                meter=(3, 4),
            ),
        ),
        exercises=("RythmicEquations", "NotationIdentification"),
    ),
    "dot": _Term(
        definition="A dot to the right of a note or rest adds half of "
        "its original duration. This is called an augmentation dot.",
        guide="Tap two steady beats. In the first example, the second click "
        "lands on your second tap. Add the dot and it lands halfway "
        "between that tap and the next beat.",
        examples=(
            _Example(
                "",
                "Quarter note · click on beat two",
                rhythm="quarter quarter",
                meter=(2, 4),
            ),
            _Example(
                "",
                "Dotted quarter · click half a beat later",
                rhythm="dotted-quarter eighth",
                meter=(2, 4),
            ),
        ),
        exercises=("RythmicEquations", "NotationIdentification"),
    ),
    "beat": _Term(
        definition="A beat is the regular pulse you can tap along with "
        "in music. Beats form groups called measures. A note can last "
        "for several beats or for part of one.",
        guide="Tap with the four clicks. Switch to the half notes and keep "
        "tapping at the same speed. You still tap four beats, but now "
        "you hear a click only on beats one and three.",
        examples=(
            _Example(
                "",
                "Four beats · one note per tap",
                meter=(4, 4),
                counts=("1", "2", "3", "4"),
                rhythm="quarter quarter quarter quarter",
            ),
            _Example(
                "",
                "Four beats · two taps per note",
                meter=(4, 4),
                counts=("1–2", "3–4"),
                rhythm="half half",
            ),
        ),
        exercises=("RythmicEquations",),
        lesson="duration",
    ),
    "meter": _Term(
        definition="Meter is the recurring pattern of stronger and weaker "
        "beats in music. The first beat of each group is the downbeat.",
        guide="Tap at the same speed in both examples. A stronger click marks "
        "each downbeat. Count the taps until the next strong click.",
        examples=(_meter_example(2), _meter_example(3)),
        exercises=(
            "BeatConstruction",
            "BeatIdentification",
            "NotationIdentification",
            "RythmicEquations",
        ),
    ),
    "measure": _Term(
        definition="A measure, also called a bar, is a span of music set "
        "off by bar lines. In 2/4, a full measure lasts two quarter-note "
        "beats.",
        guide="Count from one vertical line to the next. Switch examples "
        "and tap the same two beats. Adding a sound on each “&” doubles "
        "the number of notes in the measure while its length stays the same.",
        examples=(_meter_example(2), _meter_example(2, divisions=2)),
        exercises=(
            "BeatConstruction",
            "BeatIdentification",
            "NotationIdentification",
            "RythmicEquations",
        ),
    ),
    "bar line": _Term(
        definition="A bar line is a vertical line across the staff that "
        "marks the boundary of a measure. It is also spelled “barline.”",
        guide="Count the four quarter notes and find the single line to "
        "their right. Switch examples to see a double bar line, which "
        "often marks a change of section.",
        examples=(
            _Example(
                "",
                "Single bar line at the end of a measure",
                meter=(4, 4),
                rhythm="quarter quarter quarter quarter",
                counts=("1", "2", "3", "4"),
                bar_line="Barline",
            ),
            _Example(
                "",
                "Double bar line at a section boundary",
                meter=(4, 4),
                rhythm="quarter quarter quarter quarter",
                counts=("1", "2", "3", "4"),
                bar_line="Double barline",
            ),
        ),
        exercises=("NotationIdentification",),
    ),
    "duple meter": _Term(
        definition="Duple means grouped in twos. In duple meter, each "
        "measure has two main beats.",
        guide="Tap once on each number. In 2/4, say “1 & 2 &.” In 6/8, "
        "say “1 la li 2 la li.” Your foot still taps twice per measure.",
        examples=(
            _meter_example(2, divisions=2),
            _meter_example(2, divisions=3),
        ),
        exercises=(
            "BeatConstruction",
            "BeatIdentification",
            "NotationIdentification",
            "RythmicEquations",
        ),
    ),
    "triple meter": _Term(
        definition="Triple means grouped in threes. In triple meter, each "
        "measure has three main beats.",
        guide="Count “1, 2, 3” with the numbered pulses. In 3/4 each beat "
        "divides in two. Switch to 9/8 and hear three sounds within each tap.",
        examples=(
            _meter_example(3, divisions=2),
            _meter_example(3, divisions=3),
        ),
        exercises=(
            "BeatConstruction",
            "BeatIdentification",
            "NotationIdentification",
            "RythmicEquations",
        ),
    ),
    "quadruple meter": _Term(
        definition="Quadruple means grouped in fours. In quadruple meter, "
        "each measure has four main beats. Beat one usually feels strongest, "
        "with a lighter emphasis on beat three.",
        guide="Tap “1, 2, 3, 4” in both examples. Listen for the strongest "
        "click on one and a lighter accent on three. In 12/8, say three "
        "syllables for each tap.",
        examples=(
            _meter_example(4, divisions=2),
            _meter_example(4, divisions=3),
        ),
        exercises=(
            "BeatConstruction",
            "BeatIdentification",
            "NotationIdentification",
            "RythmicEquations",
        ),
    ),
    "metric accent": _Term(
        definition="A metric accent is the emphasis a beat gets from its "
        "place in the meter. You can feel it even when the player keeps "
        "the volume steady.",
        guide="In 3/4, hear a strong click on one followed by two softer "
        "clicks. Switch to 4/4 and listen for a second, lighter accent "
        "on three.",
        examples=(_meter_example(3), _meter_example(4)),
        exercises=("NotationIdentification", "RythmicEquations"),
    ),
    "hypermeter": _Term(
        definition="Hypermeter is a recurring pattern of stronger and weaker "
        "measures. A whole measure can feel like one beat in a larger group.",
        guide="Tap twice per measure. The loudest click begins each group. "
        "Count how many measures pass before it returns, first in groups "
        "of two measures and then in groups of four.",
        examples=(
            _meter_example(2, bars_per_group=2),
            _meter_example(2, bars_per_group=4),
        ),
        exercises=("RythmicEquations",),
    ),
    "divisions of the beat": _Term(
        definition="Divisions of the beat are the equal parts within a "
        "beat. Two and three are common ways to divide a beat.",
        guide="Tap on the numbered clicks. First say “1 & 2 &,” then say "
        "“1 la li 2 la li.” Keep your taps equally far apart as the "
        "number of sounds per tap changes.",
        examples=(
            _meter_example(2, divisions=2),
            _meter_example(2, divisions=3),
        ),
        exercises=("RythmicEquations",),
    ),
    "simple beat": _Term(
        definition="A simple beat divides naturally into two equal parts. "
        "For example, a quarter-note beat divides into two eighth notes.",
        guide="Tap on each number and say “&” halfway to the next tap. "
        "Switch from two to three beats per measure and keep the same "
        "two-part division.",
        examples=(
            _meter_example(2, divisions=2),
            _meter_example(3, divisions=2),
        ),
        exercises=("RythmicEquations",),
    ),
    "compound beat": _Term(
        definition="A compound beat divides naturally into three equal "
        "parts. In 6/8 and 9/8, a dotted quarter note is the main beat "
        "and each of its three parts is an eighth note.",
        guide="Say “1 la li” with the first three clicks. Keep three clicks "
        "per tap as you switch from two main beats in 6/8 to three in 9/8.",
        examples=(
            _meter_example(2, divisions=3),
            _meter_example(3, divisions=3),
        ),
        exercises=("RythmicEquations",),
    ),
    "tempo": _Term(
        definition="Tempo is the speed of the beat. It can be measured "
        "in beats per minute (BPM).",
        guide="Tap with the metronome at 60 BPM, one click per second. "
        "Switch to 120 BPM and hear the same four clicks twice as fast.",
        examples=(
            _Example(
                "",
                "60 BPM · one beat per second",
                rhythm="quarter quarter quarter quarter",
                bpm=60,
            ),
            _Example(
                "",
                "120 BPM · two beats per second",
                rhythm="quarter quarter quarter quarter",
                bpm=120,
            ),
        ),
        exercises=("RythmicEquations",),
    ),
    "pitch": _Term(
        definition=(
            "Pitch is how high or low a sound seems. For a steady tone, "
            "faster vibrations produce a higher pitch."
        ),
        guide=(
            "Play the two notes and follow them from left to right. A "
            "higher note on this staff also sounds higher."
        ),
        examples=(
            _Example("C4 G4", "From middle C up to G"),
            _Example("G4 C4", "From G down to middle C"),
        ),
        exercises=("NoteNames", "KeyboardNotes"),
        lesson="pitches-and-notes",
    ),
    "octave": _Term(
        definition="An octave is the interval from one note to the next higher"
        " or lower note of the same name. "
        "It spans twelve half steps. The higher pitch has twice the "
        "frequency of the lower one.",
        guide="Count the letter names from C up to the next C, including "
        "both ends: C, D, E, F, G, A, B, C. "
        "Play the pair to hear how two notes can share a name at "
        "different heights.",
        examples=(
            _Example("C4 C5", "Middle C and the C one octave higher"),
            _Example("F4 F5", "F and the F one octave higher"),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="pitches-and-notes",
    ),
    "octave register": _Term(
        definition="An octave register is a band of notes that share an octave"
        " number. "
        "In scientific pitch notation, each band runs from C through "
        "the B above it. Middle C is C4.",
        guide="Follow the letters across the boundary. The number "
        "increases as B rises to C and stays the same "
        "as C rises to D. Accidentals keep the octave number of their "
        "written letter.",
        examples=(
            _Example("B3 C4 D4", "B3 → C4 → D4"),
            _Example("B4 C5 D5", "B4 → C5 → D5"),
        ),
        exercises=("NoteNames", "KeyboardNotes"),
        lesson="pitches-and-notes",
    ),
    "staff": _Term(
        definition="A staff is a set of five horizontal lines. The center of a"
        " notehead sits on a line or in a space. "
        "The clef tells you which letter name belongs to each position.",
        guide="Count from the bottom. In treble clef the first line is E,"
        " the space above it is F, "
        "and the second line is G. Follow the noteheads up one position"
        " at a time.",
        examples=(
            _Example("E4 F4 G4", "E on line 1, F in space 1, G on line 2"),
            _Example("G4 A4 B4", "G on line 2, A in space 2, B on line 3"),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="clef-basics",
    ),
    "ledger lines": _Term(
        definition="Ledger lines are short lines that extend the staff above "
        "or below its five lines. "
        "They keep the same spacing as the staff and are drawn only "
        "where a note needs them.",
        guide="Look at the bottom of the treble staff. D fits in the "
        "space just below it. Middle C sits on "
        "the first ledger line. The A below middle C needs a second "
        "ledger line.",
        examples=(
            _Example(
                "D4 C4 A3",
                "Below the staff: zero, one, then two ledger lines",
            ),
            _Example(
                "G5 A5 C6",
                "Above the staff: zero, one, then two ledger lines",
            ),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="clef-basics",
    ),
    "clef": _Term(
        definition="A clef is a sign that assigns a pitch to a particular "
        "staff line. "
        "Once that line is known, the other lines and spaces follow in "
        "letter order.",
        guide="Find the line marked by each clef. The treble clef curls "
        "around G, the bass clef’s dots straddle F, "
        "and the center of a C clef marks middle C. Count lines from "
        "the bottom.",
        examples=(
            _Example("G4", "Treble clef marks G4 on line 2"),
            _Example("F3", "Bass clef marks F3 on line 4", clef="bass"),
            _Example("C4", "Alto clef marks middle C on line 3", clef="alto"),
            _Example(
                "C4",
                "Tenor clef marks middle C on line 4",
                clef="tenor",
            ),
        ),
        exercises=("ClefBasics", "NoteNames"),
        lesson="clef-basics",
    ),
    "bass": _Term(
        definition=(
            "The bass is the lowest sounding part of a piece of music. "
            "At any moment, the lowest note in a chord is its bass note. "
            "Bass can also mean a low singing voice or an instrument "
            "that plays the low part."
        ),
        guide=(
            "Listen to the single note, then follow it as the chord "
            "sounds. Both examples use the notes of a C major chord. "
            "C is its root, the note the chord is named for. "
            "Switch examples to hear E take over as the bass."
        ),
        examples=(
            _Example("C3 C3+E3+G3", "C in the bass · C major", clef="bass"),
            _Example("E3 E3+G3+C4", "E in the bass · C major", clef="bass"),
        ),
        exercises=("ArpeggioNames", "NoteNames"),
        lesson="clef-basics",
    ),
    "grand staff": _Term(
        definition="A grand staff is a pair of staves joined by a brace and "
        "read together. "
        "Piano scores usually put a treble clef on the upper staff and "
        "a bass clef on the lower one.",
        guide="Follow the notes across the gap. Middle C can be written "
        "on one ledger line below the treble "
        "staff or one above the bass staff. Here it is written just "
        "below the treble staff.",
        examples=(
            _Example(
                "B3 C4 D4",
                "B below middle C, middle C, then D above it",
                clef="grand",
            ),
            _Example(
                "C3 C4 C5",
                "Three Cs, each an octave above the last",
                clef="grand",
            ),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="clef-basics",
    ),
    "major scale": _Term(
        definition="A major scale has seven different letter names. Going up "
        "from its starting note (the tonic) "
        "to the next tonic, the steps are whole, whole, half, whole, "
        "whole, whole, half.",
        guide="Read the marks between the notes. W means a whole step and"
        " H means a half step. "
        "In C major the half steps are E–F and B–C. Switch to G major "
        "and find them in the same two places.",
        examples=(
            _Example(
                "C4 D4 E4 F4 G4 A4 B4 C5",
                "C major · half steps at E–F and B–C",
            ),
            _Example(
                "G4 A4 B4 C5 D5 E5 F#5 G5",
                "G major · half steps at B–C and F♯–G",
                signature=1,
            ),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "half step": _Term(
        definition="A half step, also called a semitone, is the distance from "
        "one piano key to its immediate "
        "neighbor in either direction. Count black keys as well as "
        "white keys.",
        guide="Look for a key between the two highlighted pitches. E and "
        "F touch with no black key between them. "
        "C and C♯ are just as close, even though their keys have "
        "different colors.",
        examples=(
            _Example("E4 F4", "E to F · adjacent white keys"),
            _Example("C4 C#4", "C to C♯ · adjacent white and black keys"),
        ),
        exercises=("KeyboardIntervals", "ScaleConstruction"),
        lesson="scale-identification",
        keyboard=True,
    ),
    "whole step": _Term(
        definition="A whole step, also called a whole tone, is an interval of "
        "two half steps. "
        "On a piano, exactly one key lies between the two pitches.",
        guide="Trace the two half steps between the highlighted keys. "
        "From C to D you pass over C♯. "
        "From E to F♯ you pass over F.",
        examples=(
            _Example("C4 D4", "C to D · C♯ lies between"),
            _Example("E4 F#4", "E to F♯ · F lies between"),
        ),
        exercises=("KeyboardIntervals", "ScaleConstruction"),
        lesson="scale-identification",
        keyboard=True,
    ),
    "tetrachord": _Term(
        definition="A tetrachord is a series of four pitches spanning a "
        "perfect fourth (five half steps). "
        "In a major tetrachord the three steps are whole, whole, half.",
        guide="C major contains two major tetrachords. Read C–D–E–F, then"
        " switch to G–A–B–C. "
        "Each ends with a half step. A whole step from F to G joins the"
        " two groups.",
        examples=(
            _Example("C4 D4 E4 F4", "C–D–E–F · lower tetrachord of C major"),
            _Example("G4 A4 B4 C5", "G–A–B–C · upper tetrachord of C major"),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "accidental": _Term(
        definition="An accidental is a sign before a notehead that raises, "
        "lowers, or restores the pitch of that letter. "
        "A sharp raises the letter’s natural pitch by a half step, a "
        "flat lowers it by a half step, "
        "and a natural sign calls for the unaltered pitch.",
        guide="Compare the two notes in each example. Their staff "
        "position stays the same. "
        "Read the sign before the second note and listen for which way "
        "the pitch moves. "
        "An accidental normally carries through the measure for that "
        "letter in that octave.",
        examples=(
            _Example("F4 F#4", "F to F♯ · the sharp raises the second note"),
            _Example("B4 Bb4", "B to B♭ · the flat lowers the second note"),
            _Example(
                "F#4 F4",
                "F♯ to F♮ · the natural cancels the signature’s F♯",
                signature=1,
            ),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="scale-identification",
    ),
    "key": _Term(
        definition="The key of a passage tells you which note sounds like home"
        " (the tonic) and whether the music "
        "is in major or minor. Melodies and chords establish the key by"
        " moving away from and returning to the tonic.",
        guide="Both examples have an empty key signature. Listen to the "
        "opening chord played one note at a time, "
        "then hear the melody settle back on C in C major or A in A minor.",
        examples=(
            _Example("C4 E4 G4 D4 C4", "C major · hear D settle on C"),
            _Example("A4 C5 E5 B4 A4", "A minor · hear B settle on A"),
        ),
        exercises=("ScaleIdentification", "CircleOfFifths"),
        lesson="circle-of-fifths",
    ),
    "key signature": _Term(
        definition="A key signature is the pattern of sharps or flats written "
        "after the clef. It sets the default "
        "pitch for each affected letter in every octave until the "
        "signature changes. An accidental can override it locally.",
        guide="Compare the same two Fs with an empty signature and with "
        "one sharp. The noteheads stay in place, "
        "but the sharp beside the clef raises both Fs. Then try the "
        "flat signature and listen to the two Bs.",
        examples=(
            _Example("F4 F5", "Empty signature · F4 and F5"),
            _Example(
                "F#4 F#5",
                "One sharp in the signature · F♯4 and F♯5",
                signature=1,
            ),
            _Example(
                "Bb3 Bb4",
                "One flat in the signature · B♭3 and B♭4",
                signature=-1,
            ),
        ),
        exercises=("KeySignatures", "KeySignatureConstruction"),
        lesson="circle-of-fifths",
    ),
    "enharmonic": _Term(
        definition="Enharmonic describes a change in spelling that keeps the "
        "same sounding pitch on an equal-tempered "
        "instrument such as a piano. The spelling can show where a note"
        " is heading.",
        guide="Play both phrases. The middle note sounds the same each "
        "time. C♯ leads up to D in the first "
        "phrase. D♭ leads down to C in the second.",
        examples=(
            _Example("C4 C#4 D4", "C–C♯–D · a rising line"),
            _Example("D4 Db4 C4", "D–D♭–C · a falling line"),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="pitches-and-notes",
    ),
    "enharmonically equivalent": _Term(
        definition="Two notes are enharmonically equivalent when they have "
        "different written names but sound at "
        "the same pitch in equal temperament.",
        guide="Play each pair. The notehead moves to a different staff "
        "position, yet you hear one piano key "
        "struck twice. Even a white key can have two names.",
        examples=(
            _Example("F#4 Gb4", "F♯ and G♭ share a black key"),
            _Example("B#4 C5", "B♯ and C share a white key"),
        ),
        exercises=("NoteNames", "KeyboardNotes"),
        lesson="pitches-and-notes",
    ),
    "transpose": _Term(
        definition="To transpose music is to move every note up or down by the"
        " same interval. "
        "The starting pitch changes while the distances between notes "
        "and their rhythm stay the same.",
        guide="Play the phrase in C, then switch to D. Each note has "
        "moved up a whole step. "
        "The last note moves from E to F♯ so the last step of the "
        "melody keeps its sound.",
        examples=(
            _Example("C4 D4 F4 E4", "Original phrase · C–D–F–E"),
            _Example(
                "D4 E4 G4 F#4",
                "Up a whole step · D–E–G–F♯",
                signature=2,
            ),
        ),
        exercises=("IntervalNames", "NoteConstruction"),
        lesson="intervals",
    ),
    "circle of fifths": _Term(
        definition="The circle of fifths is a diagram of keys arranged by "
        "their tonics. Each clockwise step "
        "takes you up a perfect fifth. Starting at C major, the "
        "signatures gain one sharp per step clockwise "
        "or one flat per step counterclockwise until the sharp and flat"
        " spellings meet.",
        guide="Follow the major keys on the outer ring. Play the two "
        "tonics, then switch examples. "
        "Moving clockwise from C to G to D gives one sharp, then two. "
        "Moving one place the other way from C gives F.",
        examples=(
            _Example(
                "C4 G4",
                "C to G clockwise · G major has one sharp",
                signature=1,
            ),
            _Example(
                "G4 D5",
                "G to D clockwise · D major has two sharps",
                signature=2,
            ),
            _Example(
                "C5 F4",
                "C to F counterclockwise · F major has one flat",
                signature=-1,
            ),
        ),
        exercises=("CircleOfFifths", "KeySignatures"),
        lesson="circle-of-fifths",
        circle=True,
    ),
    "natural minor scale": _Term(
        definition="A natural minor scale rises from its tonic by whole, half,"
        " whole, whole, half, whole, "
        "and whole steps. It uses the notes of the minor key signature.",
        guide="Find the two half steps, marked H. In A minor they fall "
        "between B and C and between E and F. "
        "Switch to E minor and hear the same pattern from a different tonic.",
        examples=(
            _Example(
                "A3 B3 C4 D4 E4 F4 G4 A4",
                "A natural minor · no sharps or flats",
            ),
            _Example(
                "E4 F#4 G4 A4 B4 C5 D5 E5",
                "E natural minor · one sharp",
                signature=1,
            ),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "harmonic minor scale": _Term(
        definition="Harmonic minor raises the seventh degree of natural minor "
        "by a half step. "
        "That seventh degree, the leading tone, is now a half step "
        "below the tonic.",
        guide="Listen to the last three notes. The gap marked 3H spans "
        "three half steps from degree 6 to "
        "degree 7. The leading tone then rises just one half step to "
        "the tonic.",
        examples=(
            _Example(
                "A3 B3 C4 D4 E4 F4 G#4 A4",
                "A harmonic minor · F to G♯ to A",
            ),
            _Example(
                "E4 F#4 G4 A4 B4 C5 D#5 E5",
                "E harmonic minor · C to D♯ to E",
                signature=1,
            ),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "melodic minor scale": _Term(
        definition="In the traditional ascending form, melodic minor raises "
        "the sixth and seventh degrees of "
        "natural minor by a half step each. The traditional descending "
        "form uses natural minor.",
        guide="Follow D minor up, then down. On the way up, B♮ and C♯ "
        "lead to D. On the way down, "
        "listen for C♮ and B♭. The key signature stays the same.",
        examples=(
            _Example(
                "D4 E4 F4 G4 A4 B4 C#5 D5",
                "D melodic minor ascending · B♮ and C♯",
                signature=-1,
            ),
            _Example(
                "D5 C5 Bb4 A4 G4 F4 E4 D4",
                "D melodic minor descending · C♮ and B♭",
                signature=-1,
            ),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "minor pentachord": _Term(
        definition="A minor pentachord consists of the first five notes of a "
        "minor scale. "
        "From the tonic up to the fifth, its steps are whole, half, "
        "whole, whole.",
        guide="Find the H between the second and third notes. All three "
        "forms of the minor scale begin "
        "with this same five-note pattern.",
        examples=(
            _Example(
                "A4 B4 C5 D5 E5",
                "Minor pentachord on A · the half step is B–C",
            ),
            _Example(
                "D4 E4 F4 G4 A4",
                "Minor pentachord on D · the half step is E–F",
                signature=-1,
            ),
        ),
        exercises=("ScaleConstruction", "ScaleIdentification"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "relative keys": _Term(
        definition="Relative keys are a major key and a minor key with the "
        "same key signature. The tonic "
        "of the relative minor lies a minor third below the tonic of "
        "the relative major.",
        guide="Play both phrases. Each has one sharp, F♯. The first "
        "phrase settles on G. "
        "The second settles on E, the tonic of G major’s relative minor.",
        examples=(
            _Example(
                "G4 B4 D5 F#4 G4",
                "G major · listen for the return to G",
                signature=1,
            ),
            _Example(
                "E4 G4 B4 F#4 E4",
                "E minor · listen for the return to E",
                signature=1,
            ),
        ),
        exercises=("CircleOfFifths", "KeySignatures"),
        lesson="key-signatures",
    ),
    "parallel keys": _Term(
        definition=(
            "Parallel keys are a major key and a minor key with the same "
            "tonic. Their key signatures differ."
        ),
        guide="Both phrases start and end on D. Listen to the third note."
        " The F♯ of D major becomes F♮ in D minor, "
        "while D still sounds like home.",
        examples=(
            _Example("D4 E4 F#4 E4 D4", "D major · two sharps", signature=2),
            _Example("D4 E4 F4 E4 D4", "D minor · one flat", signature=-1),
        ),
        exercises=("KeySignatures", "ScaleIdentification"),
        lesson="key-signatures",
    ),
    "interval": _Term(
        definition="An interval is the distance between two pitches. Its name "
        "combines a number, which counts "
        "letter names from the lower note to the upper note with both "
        "ends included, and a quality such as perfect, "
        "major or minor, which tells the exact size in half steps.",
        guide="Count the letters from the lower note: C, D, E is a third,"
        " and C, D, E, F, G is a fifth. "
        "Staff positions count the same way, one line or space at a "
        "time. Play each pair to hear how the distance grows.",
        examples=(
            _Example("C4 E4", "C up to E · a third"),
            _Example("C4 G4", "C up to G · a fifth"),
            _Example("E4 C5", "E up to C · a sixth"),
        ),
        exercises=(
            "IntervalNames",
            "KeyboardIntervals",
            "IntervalConstruction",
        ),
        lesson="intervals",
    ),
    "harmonic interval": _Term(
        definition="A harmonic interval is an interval whose two notes sound "
        "at the same time. "
        "On the staff the notes are stacked in one column, with the "
        "lower note at the bottom.",
        guide="Play each example and listen to the two notes blend into "
        "one sound. Read the interval from the bottom note "
        "to the top note. Notes a second apart sound rough together, "
        "while a fifth sounds open.",
        examples=(
            _Example("C4+E4", "C and E together · a harmonic third"),
            _Example("C4+G4", "C and G together · a harmonic fifth"),
            _Example("D4+C5", "D and C together · a harmonic seventh"),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="intervals",
    ),
    "melodic interval": _Term(
        definition="A melodic interval is an interval whose two notes sound "
        "one after the other. "
        "On the staff the notes are written in separate columns, and "
        "the second can be higher or lower than the first.",
        guide="Play each example from left to right. The interval is the "
        "same size in either direction. "
        "The first example rises a fifth and the second falls a fifth.",
        examples=(
            _Example("C4 G4", "C up to G · a rising melodic fifth"),
            _Example("G4 C4", "G down to C · a falling melodic fifth"),
            _Example("E4 G4", "E up to G · a rising melodic third"),
        ),
        exercises=("IntervalNames", "IntervalConstruction"),
        lesson="intervals",
    ),
    "unison": _Term(
        definition="A unison is the interval between two notes on the same "
        "line or space, with the same letter name. "
        "A perfect unison is the same pitch, zero half steps apart. Its"
        " number is one.",
        guide="Play the first example. The second note is a repeat of the"
        " first. In the second example the note "
        "is raised a half step by a sharp. It stays on the same line or"
        " space, so the number is still one, "
        "but the quality is now augmented.",
        examples=(
            _Example("C4 C4", "C then C · a perfect unison"),
            _Example("C4 C#4", "C then C♯ · an augmented unison"),
        ),
        exercises=("IntervalNames", "IntervalConstruction"),
        lesson="intervals",
    ),
    "simple intervals": _Term(
        definition="A simple interval is no larger than an octave. Its number "
        "runs from one, a unison, to eight, "
        "an octave, and it spans up to twelve half steps.",
        guide="Count the letters from the lower note to the upper one. If"
        " you reach eight or fewer, the interval is simple. "
        "Play each example, and compare the wider one with the compound"
        " intervals.",
        examples=(
            _Example("C4 G4", "C up to G · a fifth"),
            _Example("D4 B4", "D up to B · a sixth"),
            _Example("C4 C5", "C up to C · an octave"),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="intervals",
    ),
    "compound intervals": _Term(
        definition="A compound interval is larger than an octave. Its number "
        "is nine or more. Take away an octave, "
        "which removes seven from the number, and you have the simple "
        "interval it is built on. The quality stays the same.",
        guide="Count from C4 to E5 and you reach ten. Subtract seven to "
        "get three, so a tenth is a third plus an octave. "
        "Play each example, then compare with the same notes brought "
        "within one octave.",
        examples=(
            _Example(
                "C4 D5",
                (
                    "C up to D an octave higher · a ninth, which is a "
                    "second plus an octave"
                ),
            ),
            _Example(
                "C4 E5",
                (
                    "C up to E an octave higher · a tenth, which is a "
                    "third plus an octave"
                ),
            ),
            _Example(
                "C4 G5",
                (
                    "C up to G an octave higher · a twelfth, which is a "
                    "fifth plus an octave"
                ),
            ),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="intervals",
    ),
    "perfect": _Term(
        definition="Perfect is the quality of a unison, fourth, fifth or "
        "octave in its standard size: "
        "zero, five, seven or twelve half steps. These intervals are "
        "never called major or minor.",
        guide="Count the half steps. From C to F is five, from C to G is "
        "seven, and from C to the next C is twelve. "
        "Widen a perfect interval by a half step and it becomes "
        "augmented. Narrow it by a half step and it becomes diminished.",
        examples=(
            _Example("C4 F4", "C up to F · a perfect fourth, five half steps"),
            _Example("C4 G4", "C up to G · a perfect fifth, seven half steps"),
            _Example(
                "C4 C5",
                "C up to C · a perfect octave, twelve half steps",
            ),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="intervals",
    ),
    "major": _Term(
        definition="Major is the larger of the two standard sizes for a "
        "second, third, sixth or seventh. "
        "Each matches the distance from the tonic to that note of the "
        "major scale. Major also names a scale and a key.",
        guide="Count from C and compare with the C major scale. D, E and "
        "A are all in it, so the intervals are major. "
        "A major second is two half steps, a third is four, and a sixth"
        " is nine.",
        examples=(
            _Example("C4 D4", "C up to D · a major second, two half steps"),
            _Example("C4 E4", "C up to E · a major third, four half steps"),
            _Example("C4 A4", "C up to A · a major sixth, nine half steps"),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="intervals",
    ),
    "minor": _Term(
        definition="Minor is the smaller of the two standard sizes for a "
        "second, third, sixth or seventh. "
        "It is one half step narrower than the major interval with the "
        "same number. Minor also names a scale and a key.",
        guide="Lower the top note of a major interval by a half step to "
        "make it minor. The letters stay the same, "
        "so the interval keeps its number. A minor second is one half "
        "step, a third is three, and a sixth is eight.",
        examples=(
            _Example("C4 Db4", "C up to D♭ · a minor second, one half step"),
            _Example("C4 Eb4", "C up to E♭ · a minor third, three half steps"),
            _Example("C4 Ab4", "C up to A♭ · a minor sixth, eight half steps"),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="intervals",
    ),
    "augmented": _Term(
        definition=(
            "An augmented interval is one half step wider than a perfect "
            "or major interval with the same letter span. Its symbol is A."
        ),
        guide=(
            "Follow the upper note as it rises. C to F is a perfect fourth. "
            "Raising F to F♯ widens it to an augmented fourth. The same "
            "idea gives an augmented triad its sound: raise the fifth "
            "of a major chord."
        ),
        examples=(
            _Example("C4+F4 C4+F#4", "Perfect fourth → augmented fourth"),
            _Example("C4+E4+G4 C4+E4+G#4", "C major → C augmented"),
        ),
        exercises=("IntervalConstruction", "ChordQualities"),
        lesson="intervals",
    ),
    "diminished": _Term(
        definition=(
            "A diminished interval is one half step narrower than a perfect "
            "or minor interval with the same letter span. Its symbol is d."
        ),
        guide=(
            "Keep C in place and lower G to G♭. The perfect fifth becomes "
            "a diminished fifth. In the chord example, listen for the "
            "same change above C and E♭: lowering the fifth of a minor "
            "triad makes a diminished triad."
        ),
        examples=(
            _Example("C4+G4 C4+Gb4", "Perfect fifth → diminished fifth"),
            _Example("C4+Eb4+G4 C4+Eb4+Gb4", "C minor → C diminished"),
        ),
        exercises=("IntervalConstruction", "ChordQualities"),
        lesson="intervals",
    ),
    "tritone": _Term(
        definition=(
            "A tritone spans three whole steps, or six half steps. "
            "It divides an octave in half."
        ),
        guide=(
            "Play both examples. F♯ and G♭ share a piano key, so you hear "
            "the same distance above C. The spelling tells you which "
            "interval to write: C up to F♯ spans four letters, while "
            "C up to G♭ spans five."
        ),
        examples=(
            _Example("C4 F#4", "C to F♯ · augmented fourth"),
            _Example("C4 Gb4", "C to G♭ · diminished fifth"),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="intervals",
    ),
    "interval inversion": _Term(
        definition=(
            "To invert an interval within an octave, move its lower note "
            "up an octave or its upper note down an octave. The two "
            "interval numbers add up to nine."
        ),
        guide=(
            "Follow C in the first example. It starts below E and moves "
            "above it while E stays in place. Inversion swaps major with "
            "minor and augmented with diminished. Perfect intervals stay "
            "perfect, as you can hear in the second example."
        ),
        examples=(
            _Example(
                "C4+E4 E4+C5",
                "C–E becomes E–C · major third → minor sixth",
            ),
            _Example(
                "D4+A4 A4+D5",
                "D–A becomes A–D · perfect fifth → perfect fourth",
            ),
        ),
        exercises=("IntervalNames", "IntervalConstruction"),
        lesson="intervals",
    ),
    "consonant": _Term(
        definition=(
            "Two notes are called consonant when they sound relatively "
            "stable together in a musical style. In tonal music a "
            "consonant interval can give a phrase a place to rest."
        ),
        guide=(
            "Listen to C and G together, then switch to C and E. The fifth "
            "sounds open and the third has a different color, but either "
            "can sound settled. Alto’s interval exercise also counts a "
            "perfect fourth as consonant. In a piece, a fourth above "
            "the bass can create tension."
        ),
        examples=(
            _Example("C4+G4", "C with G · a perfect fifth"),
            _Example("C4+E4", "C with E · a major third"),
        ),
        exercises=("IntervalNames",),
        lesson="intervals",
    ),
    "dissonant": _Term(
        definition=(
            "Two notes are called dissonant when they create tension "
            "together in a musical style. Moving to a more settled sound "
            "is called resolution."
        ),
        guide=(
            "Listen to the first pair, then hear where it goes. Over C, "
            "B rises a half step to another C. In the next example, "
            "both notes of a tritone move: F falls to E and B rises to C."
        ),
        examples=(
            _Example("C4+B4 C4+C5", "Major seventh resolving to an octave"),
            _Example("F4+B4 E4+C5", "Tritone resolving to a minor sixth"),
        ),
        exercises=("IntervalNames",),
        lesson="intervals",
    ),
}

for _name in ("duple", "triple", "quadruple"):
    TERMS[_name] = TERMS[f"{_name} meter"]


class _DefinitionArea(QScrollArea):
    """
    Lay out the glossary text and its example in a shared scroll area.
    """

    def __init__(self, *, definition: QTextBrowser, example: QWidget) -> None:
        super().__init__()
        self.definition = definition
        self.example = example
        self.setObjectName("glossaryDefinition")
        self.setWidgetResizable(True)

        definition.setObjectName("glossaryText")
        definition.setFrameShape(QFrame.Shape.NoFrame)
        definition.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        definition.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        definition.document().documentLayout().documentSizeChanged.connect(
            self._fit_text,
        )

        content = QWidget()
        self.content_layout = QBoxLayout(
            QBoxLayout.Direction.TopToBottom,
            content,
        )
        self.content_layout.setContentsMargins(8, 0, 8, 12)
        self.content_layout.setSpacing(12)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(definition, 1, Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(
            example,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        self.setWidget(content)
        self._fit_text(definition.document().size())

    def _fit_text(self, size: QSizeF) -> None:
        """Give the browser enough height for its wrapped document."""
        self.definition.setFixedHeight(ceil(size.height()))

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Place the example alongside the definition when both can fit.
        """
        super().resizeEvent(event)
        available = self.viewport().width() - 16  # content margins
        self.example.setFixedWidth(max(px(280), min(available, px(380))))
        wide = available >= 700
        direction = (
            QBoxLayout.Direction.LeftToRight
            if wide
            else QBoxLayout.Direction.TopToBottom
        )
        self.content_layout.setDirection(direction)


class GlossaryPage(QWidget):
    """Display definitions and links beside a searchable term list."""

    back = Signal()
    lesson_requested = Signal(str)
    exercise_requested = Signal(str)

    def __init__(self) -> None:
        """Build the glossary and select its first term."""
        super().__init__()
        layout = QHBoxLayout(self)
        sidebar = QWidget()
        sidebar.setMaximumWidth(px(210))
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.search = QLineEdit()
        self.search.setObjectName("glossarySearch")
        self.search.setProperty("field", True)
        self.search.setPlaceholderText("Search terms…")
        self.search.setAccessibleName("Search glossary terms")
        self.search.setClearButtonEnabled(True)
        search_action = self.search.addAction(
            QIcon(),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        set_svg_icon(search_action, SEARCH)
        self.terms = QListWidget()
        self.terms.setObjectName("categories")
        self.terms.setProperty("glossaryBox", True)
        self.terms.setSpacing(2)
        listed = [(name, "") for name in TERMS] + [
            (name, entry.pack) for name, entry in PLUGIN_TERMS.items()
        ]
        for name, pack in sorted(
            listed,
            key=lambda pair: (pair[0].casefold(), pair[1]),
        ):
            clash = (
                bool(pack) and name in TERMS
                # a plugin's term that a built-in one already uses
                # carries
                # its plugin's name
            )
            row = QListWidgetItem(f"{name} ({pack})" if clash else name)
            row.setSizeHint(QSize(0, px(40)))
            if pack:
                row.setData(PLUGIN_ROLE, name)
            self.terms.addItem(row)
        sidebar_layout.addWidget(self.search)
        sidebar_layout.addWidget(self.terms)
        layout.addWidget(sidebar)
        self.definition = QTextBrowser()
        self.definition.document().setDocumentMargin(14)
        self.definition.setOpenLinks(False)
        self.definition.setAccessibleName(
            "Term definition and related activities",
        )
        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        demo = QVBoxLayout()
        self.example_circle = ExplorableCircle()
        self.example_circle.set_interactive(False)
        self.example_circle.setFixedHeight(px(280))
        demo.addWidget(self.example_circle)
        self.example_staff = StaffWidget(
            gap=10,
            side=12,
            note_offset=60,
            margin=5,
            compact=True,
        )
        self.example_keyboard = KeyboardWidget()
        self.example_keyboard.max_key_width = px(26)
        demo.addWidget(self.example_staff)
        demo.addWidget(self.example_keyboard)
        self.meter_staff = MeterStaff()
        demo.addWidget(self.meter_staff, alignment=Qt.AlignmentFlag.AlignLeft)
        self.counts = QCheckBox("Show counts")
        self.counts.toggled.connect(self.meter_staff.set_counts_visible)
        self.counts.setChecked(True)
        demo.addWidget(self.counts)
        self.example_board = (
            FingerboardWidget()
        )  # a plugin's term shows its instrument here instead of notation
        self.example_board.setFixedHeight(px(190))
        self.example_board.hide()
        demo.addWidget(self.example_board)
        self.playback = StaffPlayback(
            self,
            highlight=self.example_staff.highlight_column,
        )
        self.playback.step.connect(self.meter_staff.highlight_column)
        self._preview_played = False
        demo_controls = QVBoxLayout()
        self.example_label = QLabel()
        self.example_label.setWordWrap(True)
        demo_controls.addWidget(self.example_label)
        self.next_example = QPushButton("Next example →")
        self.next_example.clicked.connect(self._next_example)
        demo_controls.addWidget(self.next_example)
        self.hear = QPushButton("▶  Hear note")
        self.hear.clicked.connect(self._hear_example)
        demo_controls.addWidget(self.hear)
        demo.addLayout(demo_controls)
        self.demo = QWidget()
        demo.setContentsMargins(0, 0, 0, 0)
        self.demo.setLayout(demo)
        self.definition_area = _DefinitionArea(
            definition=self.definition,
            example=self.demo,
        )
        main.addWidget(self.definition_area, 3)
        self.activity_switch = SegmentedControl(["Exercises", "Lessons"])
        self.activity_switch.chosen.connect(self._show_activities)
        main.addWidget(
            self.activity_switch,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        self.activity_body = QWidget()
        self.activity_tiles = QGridLayout(self.activity_body)
        self.activity_tiles.setContentsMargins(14, 14, 14, 14)
        self.activity_tiles.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        scroll = QScrollArea()
        scroll.setObjectName("glossaryActivities")
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.activity_body)
        main.addWidget(scroll, 2)
        layout.addLayout(main, 1)
        self.search.textChanged.connect(self._filter)
        self.terms.currentItemChanged.connect(self._show_term)
        self.terms.setCurrentRow(0)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.back.emit)

    def _filter(self, text: str) -> None:
        """Filter the term list and select the first visible match."""
        first = None
        for row in range(self.terms.count()):
            item = self.terms.item(row)
            item.setHidden(
                text.casefold().strip() not in item.text().casefold(),
            )
            if first is None and not item.isHidden():
                first = item
        self.terms.setCurrentRow(
            self.terms.row(first) if first is not None else -1,
        )
        if first is None:
            self._stop_preview()
            self.definition.setHtml(
                "<h2>No matching terms</h2><p>Try a different search.</p>",
            )
            self.demo.hide()

    def _show_term(
        self,
        item: QListWidgetItem | None,
        _previous: QListWidgetItem | None = None,
    ) -> None:
        """
        Show a term's definition and related lesson and exercise links.
        """
        if item is None:
            self._show_activities(self.activity_switch.current())
            return
        entry = self._entry(item)
        if isinstance(entry, PluginTerm):
            guide = f"<p>{entry.guide}</p>" if entry.guide else ""
            self.definition.setHtml(
                f"<h2>{entry.name}</h2><p>{entry.definition}</p>{guide}",
            )
        else:
            self.definition.setHtml(
                f"<h2>{item.text()}</h2><p>{entry.definition}</p><p>{entry.guide}</p>",
            )
        self._example_index = 0
        self._update_example()
        self.definition_area.verticalScrollBar().setValue(0)
        self._show_activities(self.activity_switch.current())

    def _show_activities(self, mode: int) -> None:
        """
        Display related exercise or lesson tiles for the selected term.
        """
        while self.activity_tiles.count():
            entry = self.activity_tiles.takeAt(0)
            widget = entry.widget() if entry is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        item = self.terms.currentItem()
        if item is None:
            # noinspection PyUnreachableCode
            return
        entry = self._entry(item)
        if mode == 0:
            keys = entry.exercises
            cards = [cls for cls in REGISTRY if cls.__name__ in keys]
            for column, exercise in enumerate(cards):
                card = ExerciseCard(exercise)
                card.clicked.connect(
                    lambda _checked=False, key=exercise.__name__: (
                        self.exercise_requested.emit(key)
                    ),
                )
                self.activity_tiles.addWidget(card, 0, column)
            if not cards:
                self.activity_tiles.addWidget(
                    QLabel("No exercises go with this term yet."),
                    0,
                    0,
                )
        else:
            keys = (
                entry.lessons
                if isinstance(entry, PluginTerm)
                else (entry.lesson,)
            )
            found = [lesson for lesson in LESSONS if lesson.key in keys]
            for column, lesson in enumerate(found):
                card = lesson_card(lesson)
                card.clicked.connect(
                    lambda _checked=False, key=lesson.key: (
                        self.lesson_requested.emit(key)
                    ),
                )
                self.activity_tiles.addWidget(card, 0, column)
            if not found:
                self.activity_tiles.addWidget(
                    QLabel("No lessons go with this term yet."),
                    0,
                    0,
                )

    @staticmethod
    def _entry(item: QListWidgetItem) -> _Term | PluginTerm:
        """
        Find the entry a row of the list stands for.

        Parameters
        ----------
        item : QListWidgetItem
            A row of the term list.

        Returns
        -------
        _Term or PluginTerm
            The built-in term, or the plugin's entry.
        """
        name = item.data(PLUGIN_ROLE)
        return PLUGIN_TERMS[name] if name else TERMS[item.text()]

    def _next_example(self) -> None:
        """Cycle through the selected term's notation examples."""
        self._example_index += 1
        self._update_example()

    def _update_example(self) -> None:
        """
        Render the notation or keyboard diagram from the same pitches
        used for playback.
        """
        item = self.terms.currentItem()
        if item is None:
            return
        self._stop_preview()
        entry = self._entry(item)
        if isinstance(entry, PluginTerm):
            self._show_plugin_example(entry)
            return
        self.demo.show()
        self.next_example.show()
        self.hear.show()
        self.example_board.hide()
        term = entry
        example = term.examples[self._example_index % len(term.examples)]
        self._example = example
        columns = [
            [Note.parse(name) for name in column.split("+")]
            for column in example.pitches.split()
        ]
        self._example_midis = [
            note.midi for column in columns for note in column
        ]
        self.example_circle.setVisible(term.circle)
        if term.circle:
            self.example_circle.select("outer", place=example.signature)
        self.example_keyboard.setVisible(term.keyboard)
        self.meter_staff.setVisible(bool(example.rhythm))
        self.counts.setVisible(bool(example.rhythm))
        self.example_staff.setVisible(not (term.keyboard or example.rhythm))
        if example.rhythm:
            self.meter_staff.show_score(
                tuple(example.rhythm.split()),
                meter=example.meter or (4, 4),
                counts=example.counts,
                bar_line=example.bar_line,
            )
        elif term.keyboard:
            self.example_keyboard.show_keys(self._example_midis, span=(60, 72))
        else:
            self.example_staff.wedges = (
                [
                    _STEP_LABELS[abs(right - left)]
                    for left, right in pairwise(self._example_midis)
                ]
                if term.label_steps
                else []
            )
            self.example_staff.show_notes(
                columns,
                clef=example.clef,
                key=example.signature,
            )
        self.example_label.setText(example.caption)
        self.hear.setText(
            "▶  Hear rhythm"
            if example.rhythm
            else "▶  Hear note"
            if len(self._example_midis) == 1
            else "▶  Hear example",
        )

    def _show_plugin_example(self, entry: PluginTerm) -> None:
        """
        Show a plugin term's picture with its caption, or nothing if the
        entry has none.

        Parameters
        ----------
        entry : PluginTerm
            The entry being shown.
        """
        for widget in (
            self.example_circle,
            self.example_staff,
            self.example_keyboard,
            self.counts,
            self.meter_staff,
            self.next_example,
            self.hear,
        ):
            widget.hide()
        self.example_label.setText(entry.caption)
        self.example_board.show_position(entry.picture)
        self.example_board.setVisible(entry.picture is not None)
        self.demo.setVisible(entry.picture is not None or bool(entry.caption))

    def _hear_example(self) -> None:
        """Play the displayed rhythm or pitches in reading order."""
        if self._example.rhythm and not self._example.pitches:
            durations = self._example.durations_ms()
            sounds.play_rhythm(
                durations,
                levels=self._example.click_levels or (1.0,) * len(durations),
                force=True,
                on_step=self.playback.step.emit,
            )
        elif self.example_staff.isHidden():
            sounds.preview(
                sounds.instrument,
                midis=self._example_midis,
                step_ms=self._example.durations_ms() or 450,
                beat_ms=self._example.beat_ms,
                on_step=self.playback.step.emit
                if self._example.rhythm
                else None,
            )
            self._preview_played = not self._example.rhythm
        else:
            self.playback.play(
                self.example_staff.columns,
                force=True,
                warmup=True,
            )

    def _stop_preview(self) -> None:
        """
        Silence the previous example when the learner changes the
        display.
        """
        self.playback.stop()
        if self._preview_played:
            sounds.stop_all()
            self._preview_played = False

    def hideEvent(self, event: QHideEvent) -> None:
        """
        End the example when leaving the glossary.

        Parameters
        ----------
        event : QHideEvent
            The notification that the glossary has been hidden.
        """
        self._stop_preview()
        super().hideEvent(event)
