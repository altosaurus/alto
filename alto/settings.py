"""
User settings. Pure Python (no Qt); persistence lives in
ui/exercise_settings.py.

Each exercise with settings has a small dataclass here
(`NoteNameSettings`, `KeyboardSettings` and so on) and one shared
instance of it (`note_names`, `keyboard` ...) that the exercise and its
settings panel both read and write.

Examples
--------
>>> NoteNameSettings().active_clefs()
['treble', 'bass']
>>> spell(Note.parse("F#4"))
'F♯'
"""

from __future__ import annotations

from dataclasses import (
    KW_ONLY,
    dataclass,
    field,
)
from typing import ClassVar

from alto.circle_schemes import (
    DEFAULT_SCHEME,
    CustomRecord,
    Scheme,
    resolve,
)
from alto.notation_terms import MARKS
from alto.theory.pitch import (
    ACCIDENTAL_SYMBOLS,
    LETTERS,
    Interval,
    Note,
    key_accidental,
)

# The clefs with a single staff. The C clefs differ only in the line the
# clef sits on: soprano on the bottom line, mezzo-soprano
# on the second, alto on the middle, tenor on the fourth and baritone on
# the top line.
CLEFS = (
    "treble",
    "bass",
    "alto",
    "tenor",
    "soprano",
    "mezzo",
    "baritone",
)
CLEF_NAMES = {
    "treble": "Treble",
    "bass": "Bass",
    "alto": "Alto",
    "tenor": "Tenor",
    "soprano": "Soprano",
    "mezzo": "Mezzo-soprano",
    "baritone": "Baritone",
    "french": "French violin",
    "subbass": "Subbass",
    # what each of `CLEFS` is called, and the two more that only the
    # clef
    # exercise has
}
# How the clefs are grouped on the settings pages: the grand staff, the
# four in everyday use, and the three rarer ones.
CLEF_GROUPS = (
    ("grand",),
    (
        "treble",
        "bass",
        "alto",
        "tenor",
    ),
    ("soprano", "mezzo", "baritone"),
    (
        "french",
        "subbass",
        # only the clef exercise has these, so the other pages leave the
        # group out
    ),
)
CLEF_BASICS_CLEFS = (
    *CLEFS,
    "french",
    "subbass",
)  # the clef exercise also has the French violin clef and the subbass clef
RANGE_KEYS = (*CLEFS, "grand")  # clefs that can have a note range
# Inclusive diatonic range of notes that may be asked, per clef
# (defaults sit comfortably on the staff).
DEFAULT_RANGES = {
    "treble": (
        Note(3, letter=1).diatonic,
        Note(7, letter=3).diatonic,
    ),  # D3..F7
    "bass": (Note(1, letter=3).diatonic, Note(5, letter=5).diatonic),  # F1..A5
    "alto": (Note(3, letter=0).diatonic, Note(5, letter=0).diatonic),  # C3..C5
    "tenor": (
        Note(2, letter=5).diatonic,
        Note(4, letter=5).diatonic,
    ),  # A2..A4
    "soprano": (
        Note(3, letter=4).diatonic,
        Note(5, letter=4).diatonic,
    ),  # G3..G5
    "mezzo": (
        Note(3, letter=2).diatonic,
        Note(5, letter=2).diatonic,
    ),  # E3..E5
    "baritone": (
        Note(2, letter=3).diatonic,
        Note(4, letter=3).diatonic,
    ),  # F2..F4
    "grand": (
        Note(2, letter=0).diatonic,
        Note(6, letter=0).diatonic,
    ),  # C2..C6
}
# Bounds for the range pickers: C1..C7.
MIN_DIATONIC, MAX_DIATONIC = (
    Note(1, letter=0).diatonic,
    Note(7, letter=0).diatonic,
)


NOTE_VALUES = (
    "breve",
    "whole",
    "half",
    "quarter",
    "eighth",
    "sixteenth",
    "thirty_second",
)
NAMINGS = {
    "letters": "Letters (C D E)",
    "solfege": "Solfège (Do Re Mi)",
    "degrees": "Caret (1̂ 2̂ 3̂)",
    "functions": "Function (Tonic, Supertonic, Mediant)",
}
DEGREE_NAMINGS = ("degrees", "functions")
FUNCTION_ALTERATIONS = {
    -2: "Doubly lowered ",
    -1: "Lowered ",
    0: "",
    1: "Raised ",
    2: "Doubly raised ",
}
DEGREE_FUNCTIONS = (
    "Tonic",
    "Supertonic",
    "Mediant",
    "Subdominant",
    "Dominant",
    "Submediant",
    "Leading tone",
)
SOLFEGE = (
    "Do",
    "Re",
    "Mi",
    "Fa",
    "Sol",
    "La",
    "Si",
)


# The note on the bottom line of each single staff. The range arrows may
# go up to 5 ledger lines (10 steps) beyond the staff.
BOTTOM_LINES = {
    "treble": Note(4, letter=2),
    "bass": Note(2, letter=4),
    "alto": Note(3, letter=3),
    "tenor": Note(3, letter=1),  # E4 G2 F3 D3
    "soprano": Note(4, letter=0),
    "mezzo": Note(3, letter=5),
    "baritone": Note(2, letter=6),
}  # C4 A3 B2
RANGE_LIMITS = {
    **{
        c: (
            max(MIN_DIATONIC, n.diatonic - 10),
            min(MAX_DIATONIC, n.diatonic + 8 + 10),
        )
        for c, n in BOTTOM_LINES.items()
    },
    "grand": (
        max(MIN_DIATONIC, BOTTOM_LINES["bass"].diatonic - 10),
        min(MAX_DIATONIC, BOTTOM_LINES["treble"].diatonic + 8 + 10),
    ),
    # The treble range runs from D3 to F7 and the bass range from F1 to
    # A5. These are also the furthest the pickers go.
    "treble": DEFAULT_RANGES["treble"],
    "bass": DEFAULT_RANGES["bass"],
}


def spell(
    note: Note,
    *,
    naming: str = "letters",
    key: int = 0,
    octave: bool = False,
    minor: bool = False,
) -> str:
    """
    Return a note name in the chosen naming system, optionally including
    its octave.

    Parameters
    ----------
    note : Note
        The note.
    naming : str, default "letters"
        "letters" for C D E, "solfege" for Do Re Mi, "degrees" for caret
        scale degrees, or "functions" for function names.
        Keyword-only.
    key : int, default 0
        The major key signature for scale degrees: sharps if positive,
        flats if negative. Zero means C major. Keyword-only.
    octave : bool, default False
        Include the note's octave, separated from a scale degree by " /
        ". Keyword-only.

    minor : bool, default False
        Use the relative natural minor as the scale degree reference.
        Keyword-only.

    Returns
    -------
    str
        The name and, if requested, octave. Carets use accidental
        prefixes; function names use Raised or Lowered prefixes.

    Examples
    --------
    >>> spell(Note.parse("F#4"))
    'F♯'
    >>> spell(Note.parse("F#4"), naming="solfege")
    'Fa♯'
    >>> spell(
    ...     Note.parse("F#4"),
    ...     naming="degrees",
    ...     key=1,
    ... )
    '7̂'
    >>> spell(
    ...     Note.parse("F4"),
    ...     naming="degrees",
    ...     key=1,
    ... )
    '♭7̂'
    >>> spell(Note.parse("Eb4"), naming="degrees")
    '♭3̂'
    >>> spell(
    ...     Note.parse("G4"),
    ...     naming="functions",
    ...     key=1,
    ... )
    'Tonic'
    >>> spell(
    ...     Note.parse("F4"),
    ...     naming="functions",
    ...     key=1,
    ... )
    'Lowered Leading tone'
    >>> spell(
    ...     Note.parse("G4"),
    ...     naming="degrees",
    ...     key=1,
    ...     octave=True,
    ... )
    '1̂ / 4'
    """
    if naming in DEGREE_NAMINGS:
        degree = (note.letter - 4 * key - (5 if minor else 0)) % 7 + 1
        alteration = note.accidental - key_accidental(note.letter, count=key)
        if naming == "functions":
            if minor and degree == 7:
                name = (
                    "Leading tone"
                    if alteration == 1
                    else FUNCTION_ALTERATIONS[alteration] + "Subtonic"
                )
            else:
                name = (
                    FUNCTION_ALTERATIONS[alteration]
                    + DEGREE_FUNCTIONS[degree - 1]
                )
        else:
            name = f"{ACCIDENTAL_SYMBOLS[alteration]}{degree}̂"
        return f"{name} / {note.octave}" if octave else name
    base = (
        SOLFEGE[note.letter] if naming == "solfege" else LETTERS[note.letter]
    )
    name = base + ACCIDENTAL_SYMBOLS[note.accidental]
    return f"{name}{note.octave}" if octave else name


def diatonic_name(d: int) -> str:
    """
    Return the name and octave of the natural note on a staff step.

    Parameters
    ----------
    d : int
        The staff-step index (see `Note.diatonic`).

    Returns
    -------
    str
        For example 'E4'.

    Examples
    --------
    >>> diatonic_name(30)
    'E4'
    """
    n = Note.from_diatonic(d)
    return f"{n.name}{n.octave}"


class ClefChoice:
    """
    Settings with a set of chosen clefs, which are always used in the
    same order.

    Attributes
    ----------
    CLEF_ORDER : tuple of str
        Every clef the settings may hold, in the order they are offered
        and used. Each subclass sets it.
    clefs : set of str
        The chosen clefs. The dataclass that uses this mixin declares
        the field and its default.

    Examples
    --------
    >>> ArpeggioSettings(
    ...     clefs={"tenor", "alto"}
    ... ).active_clefs()
    ['alto', 'tenor']
    """

    CLEF_ORDER: ClassVar[tuple[str, ...]] = CLEFS
    clefs: set[str]

    def active_clefs(self) -> list[str]:
        """
        Return the clefs to use, in canonical order.

        Returns
        -------
        list of str
            The chosen clefs in the order of `CLEF_ORDER`, or the treble
            clef if none are chosen.

        Examples
        --------
        >>> NoteNameSettings(
        ...     clefs={"grand", "tenor"}
        ... ).active_clefs()
        ['tenor', 'grand']
        >>> ClefBasicsSettings(
        ...     clefs={"subbass", "treble"}
        ... ).active_clefs()
        ['treble', 'subbass']
        >>> NoteNameSettings(clefs=set()).active_clefs()
        ['treble']
        """
        return [c for c in self.CLEF_ORDER if c in self.clefs] or ["treble"]


class KeyChoice:
    """
    Settings with a set of chosen key signatures.

    Attributes
    ----------
    keys : set of int
        The chosen key signatures, as sharps (positive) or flats
        (negative). The dataclass that uses this mixin declares the
        field and its default.

    Examples
    --------
    >>> KeyboardSettings(keys={3, -2}).active_keys()
    [-2, 3]
    """

    keys: set[int]

    def active_keys(self) -> list[int]:
        """
        Return the key signatures to draw from, lowest first.

        Returns
        -------
        list of int
            Sharps (positive) or flats (negative); no sharps or flats if
            none are chosen.

        Examples
        --------
        >>> ConstructionSettings(
        ...     keys={2, -1}
        ... ).active_keys()
        [-1, 2]
        >>> KeySignatureSettings(
        ...     keys=set()
        ... ).active_keys()
        [0]
        """
        return sorted(self.keys) or [0]


@dataclass
class StaffRangeSettings(ClefChoice):
    """
    Selected clefs and inclusive pitch limits for each staff.

    Examples
    --------
    >>> StaffRangeSettings().active_clefs()
    ['treble', 'bass']
    """

    CLEF_ORDER: ClassVar[tuple[str, ...]] = RANGE_KEYS

    clefs: set[str] = field(
        default_factory=lambda: {"treble", "bass"},
    )  # any of RANGE_KEYS, so "grand" is allowed
    _: KW_ONLY
    ranges: dict[str, tuple[int, int]] = field(
        default_factory=dict,
    )  # overrides of DEFAULT_RANGES

    note_values: set[str] = field(default_factory=lambda: {"whole"})

    def active_values(self) -> list[str]:
        """
        Return the note values to draw, from longest to shortest.

        Returns
        -------
        list of str
            The chosen values in the order of `NOTE_VALUES`, or whole
            notes if none are chosen.

        Examples
        --------
        >>> NoteNameSettings(
        ...     note_values={"half", "whole"}
        ... ).active_values()
        ['whole', 'half']
        """
        return [v for v in NOTE_VALUES if v in self.note_values] or ["whole"]

    def range_for(self, clef: str) -> tuple[int, int]:
        """
        Return the range of notes that may be asked on a clef.

        Parameters
        ----------
        clef : str
            A key of `DEFAULT_RANGES`.

        Returns
        -------
        tuple of (int, int)
            The lowest and highest staff step, inclusive; the user's
            override if there is one, otherwise the default.

        Examples
        --------
        >>> NoteNameSettings().range_for("treble")
        (22, 52)
        >>> NoteNameSettings(
        ...     ranges={"treble": (40, 30)}
        ... ).range_for(
        ...     "treble"
        ... )  # given in the wrong order
        (30, 40)
        """
        lo, hi = self.ranges.get(clef, DEFAULT_RANGES[clef])
        return (lo, hi) if lo <= hi else (hi, lo)


@dataclass
class NoteNameSettings(StaffRangeSettings):
    """
    The settings of the note identification exercise.

    Attributes
    ----------
    clefs : set of str
        The clefs to ask on, any of `RANGE_KEYS`, so "grand" is allowed.
    ranges : dict of str to tuple of (int, int)
        Overrides of `DEFAULT_RANGES`, as inclusive staff-step ranges.
        Keyword-only.
    key_signatures : set of int
        The keys to use, as sharps (positive) or flats (negative).
        Keyword-only.
    note_values : set of str
        The note values to draw, from `NOTE_VALUES`. Keyword-only.
    naming : str, default "letters"
        A key of `NAMINGS`. Keyword-only.
    accidentals : bool, default False
        Also ask notes with explicit sharps, flats and naturals.
        Keyword-only.
    require_octave : bool, default False
        Also require the written octave as part of the answer.
        Keyword-only.

    Examples
    --------
    >>> cfg = NoteNameSettings(
    ...     clefs={"bass"}, key_signatures={2}
    ... )
    >>> cfg.active_clefs(), cfg.active_keys()
    (['bass'], [2])
    """

    _: KW_ONLY
    key_signatures: set[int] = field(
        default_factory=lambda: {0},
    )  # sharps (+) / flats (-) of the keys to use
    naming: str = "letters"  # key of NAMINGS
    minor_degrees: bool = (
        False  # Use the relative natural minor for degree answers.
    )
    accidentals: bool = (
        False  # also ask notes with explicit sharps/flats/naturals
    )
    require_octave: bool = (
        False  # the answer also includes the note's written octave
    )

    def active_keys(self) -> list[int]:
        """
        Return the key signatures to draw from, lowest first.

        The field is named `key_signatures` rather than `keys`, as in
        `KeyChoice`, because the name is part of the practice
        signature that stored questions are matched by; renaming it
        would orphan every learner's saved questions.

        Returns
        -------
        list of int
            Sharps (positive) or flats (negative); no sharps or flats if
            none are chosen.

        Examples
        --------
        >>> NoteNameSettings(
        ...     key_signatures={2, -1}
        ... ).active_keys()
        [-1, 2]
        """
        return sorted(self.key_signatures) or [0]


note_names = NoteNameSettings()


@dataclass
class PackExerciseSettings(StaffRangeSettings):
    """
    The options a plugin's exercise offers the learner, such as its
    range and whether to ask accidentals.

    Only the options the plugin declares for the exercise are shown and
    used; the rest keep their defaults.

    Attributes
    ----------
    clefs : set of str
        The one clef the exercise's range is drawn on.
    ranges : dict of str to tuple of (int, int)
        The range of notes asked, as staff steps, under the clef.
    sound : str or None, default None
        The key of the instrument that sounds in this exercise instead
        of the plugin's own, or None for the plugin's own.
        Keyword-only.
    accidentals : bool, default False
        Also ask the notes between the listed ones, written with sharps
        or flats. Keyword-only.
    require_octave : bool, default False
        The answer also includes the note's written octave.
        Keyword-only.
    keys : tuple of int or None, default None
        For a keyboard interval exercise, the lowest and highest key
        asked, as MIDI numbers. None asks the plugin's own
        default range. Keyword-only.
    intervals : frozenset of str or None, default None
        For a keyboard interval exercise, the names of the intervals
        asked. None asks every interval the plugin lists.
        Keyword-only.
    manuals : frozenset of str or None, default None
        For a keyboard interval exercise, the names of the keyboards the
        highlighted keys may sit on. None uses them
        all. Keyword-only.

    Examples
    --------
    >>> PackExerciseSettings(
    ...     clefs={"alto"}
    ... ).sound is None
    True
    >>> PackExerciseSettings(
    ...     clefs={"alto"}
    ... ).keys is None
    True
    """

    _: KW_ONLY
    sound: str | None = None
    accidentals: bool = False
    require_octave: bool = False
    keys: tuple[int, int] | None = None
    intervals: frozenset[str] | None = None
    manuals: frozenset[str] | None = None


pack_exercises: dict[
    str,
    PackExerciseSettings,
] = {}  # by exercise class name; filled in as plugin exercises are used

INTERVAL_DISPLAYS = ("Harmonic", "Melodic")
MELODIC_DIRECTIONS = ("ascending", "descending")
INTERVAL_QUALITY_MODES = {
    "interval": "Interval Only",
    "combined": "Interval and Quality",
    "quality": "Quality Only",
}
INTERVAL_ACCIDENTALS = {
    0: "Natural (no accidentals)",
    -1: "Flat",
    -2: "Double flat",
    1: "Sharp",
    2: "Double sharp",
}
DEFAULT_INTERVAL_ACCIDENTALS = frozenset({-1, 0, 1})
INTERVAL_QUALITY_ORDER = {"A": 0, "M": 1, "P": 1, "m": 2, "d": 3}
WRITTEN_INTERVALS = {
    f"{quality}{number}": Interval(number, quality=quality)
    for number in range(2, 16)
    for quality in (
        ("P", "A", "d") if number % 7 in (1, 4, 5) else ("m", "M", "A", "d")
    )
}


@dataclass
class IntervalSettings(StaffRangeSettings):
    """
    Staff signatures, presentations, answer format and spelled intervals
    for Interval Identification.

    Examples
    --------
    >>> IntervalSettings().quality_mode
    'combined'
    """

    _: KW_ONLY
    staff_keys: set[int] = field(default_factory=lambda: {0})
    displays: set[str] = field(default_factory=lambda: {"Harmonic"})
    directions: set[str] = field(default_factory=lambda: {"ascending"})
    button_mode: str = "limited"
    button_count: int = 6
    accidentals: set[int] = field(
        default_factory=lambda: set(DEFAULT_INTERVAL_ACCIDENTALS),
    )
    quality_mode: str = "combined"
    inversions: bool = False  # Identify the inversion of the written interval.
    consonance: bool = (
        False  # Classify the interval as consonant or dissonant.
    )
    intervals: set[str] = field(
        default_factory=lambda: {
            name
            for name, iv in WRITTEN_INTERVALS.items()
            if 2 <= iv.number <= 7 or name == "P8"
        },
    )

    def staff_span(self, clef: str) -> int:
        """
        Count the written staff positions in a clef's selected range,
        including both endpoints.

        Parameters
        ----------
        clef : str
            The clef whose range to measure.

        Returns
        -------
        int
            The largest diatonic interval number that fits.

        Examples
        --------
        >>> IntervalSettings(
        ...     ranges={"treble": (28, 30)}
        ... ).staff_span("treble")
        3
        """
        low, high = self.range_for(clef)
        return high - low + 1


intervals = IntervalSettings()
interval_construction = IntervalSettings()

RHYTHM_OPERATORS = {
    "+": "Addition (+)",
    "−": "Subtraction (−)",
    "×": "Multiplication (×)",
    "÷": "Division (÷)",
}
DEFAULT_RHYTHM_OPERATORS = {"+", "−"}
RHYTHM_DURATIONS = {
    "breve": 32,
    "whole": 16,
    "half": 8,
    "quarter": 4,
    "eighth": 2,
    "sixteenth": 1,
    "thirty_second": 0.5,
}
DEFAULT_RHYTHM_SYMBOLS = set(RHYTHM_DURATIONS) - {"breve", "thirty_second"}
RHYTHM_DURATIONS.update(
    {f"{name}-rest": duration for name, duration in RHYTHM_DURATIONS.items()},
)
RHYTHM_DURATIONS.update(
    {
        f"dotted-{name}": duration * 1.5
        for name, duration in RHYTHM_DURATIONS.items()
        if not name.endswith("-rest")
    },
)
rhythm_operators = DEFAULT_RHYTHM_OPERATORS.copy()
rhythm_symbols = DEFAULT_RHYTHM_SYMBOLS.copy()
rhythm_ties = False
rhythm_beams = False
RHYTHM_BEAM_COUNTS = {"eighth": 1, "sixteenth": 2, "thirty_second": 3}

# Keyboard exercise: the whole piano is A0..C8 (MIDI 21..108); by
# default it asks C3..C5.
KEYBOARD_FULL = (21, 108)
KEYBOARD_DEFAULT = (48, 72)
_SHARP_NAMES = (
    "C",
    "C♯",
    "D",
    "D♯",
    "E",
    "F",
    "F♯",
    "G",
    "G♯",
    "A",
    "A♯",
    "B",
)


def key_name(midi: int) -> str:
    """
    Return the name of a MIDI note with its octave, black keys as
    sharps.

    Parameters
    ----------
    midi : int
        The MIDI note number.

    Returns
    -------
    str
        For example 'C4' for 60 and 'C♯4' for 61.

    Examples
    --------
    >>> key_name(60), key_name(61)
    ('C4', 'C♯4')
    """
    return f"{_SHARP_NAMES[midi % 12]}{midi // 12 - 1}"


@dataclass
class KeyboardSettings(KeyChoice):
    """
    The settings of the keyboard identification exercise.

    Attributes
    ----------
    naming : str, default "letters"
        Naming system for the highlighted key. Keyword-only.
    black_keys : bool, default True
        Also ask the black keys, answered by either enharmonic name.
    require_octave : bool, default False
        The answer must include the octave number as well. Keyword-only.
    low : int
        The lowest key asked, as a MIDI number. Keyword-only.
    high : int
        The highest key asked, as a MIDI number, inclusive.
        Keyword-only.
    key_signature : bool, default False
        Show a key signature, and require the name that fits it (no
        enharmonic spelling). Keyword-only.
    keys : set of int
        The key signatures to draw from, as sharps (positive) or flats
        (negative). Keyword-only.

    Examples
    --------
    >>> cfg = KeyboardSettings()
    >>> key_name(cfg.low), key_name(cfg.high)
    ('C3', 'C5')
    """

    black_keys: bool = (
        True  # also ask the black keys, answered by either enharmonic name
    )
    _: KW_ONLY
    naming: str = "letters"
    require_octave: bool = (
        False  # the answer must include the octave number as well
    )
    low: int = KEYBOARD_DEFAULT[
        0
    ]  # lowest and highest key asked (MIDI numbers, inclusive)
    high: int = KEYBOARD_DEFAULT[1]
    # show a key signature, and require the name that fits it (no
    # enharmonic spelling)
    key_signature: bool = False
    keys: set[int] = field(
        default_factory=lambda: {
            -3,
            -2,
            -1,
            0,
            1,
            2,
            3,
        },
    )  # sharps (+) / flats (-) to draw from


keyboard = KeyboardSettings()


_SIMPLE_KEYBOARD_INTERVAL_NAMES = (
    "m2",
    "M2",
    "m3",
    "M3",
    "P4",
    "A4 / d5",
    "P5",
    "m6",
    "M6",
    "m7",
    "M7",
    "P8",
)


def keyboard_interval_name(distance: int) -> str:
    """
    Name a keyboard interval by its distance, including compound
    intervals.

    Parameters
    ----------
    distance : int
        The distance in half steps, from 1 through the full piano span.

    Returns
    -------
    str
        A conventional interval name, with both spellings for tritones.

    Raises
    ------
    ValueError
        If the distance cannot occur between two distinct piano keys.

    Examples
    --------
    >>> (
    ...     keyboard_interval_name(13),
    ...     keyboard_interval_name(18),
    ...     keyboard_interval_name(24),
    ... )
    ('m9', 'A11 / d12', 'P15')
    >>> keyboard_interval_name(87)
    'm52'
    """
    if not 1 <= distance <= KEYBOARD_FULL[1] - KEYBOARD_FULL[0]:
        raise ValueError(
            "The interval must fit between two distinct piano keys.",
        )
    octaves, offset = divmod(distance - 1, 12)
    return " / ".join(
        f"{name[0]}{int(name[1:]) + 7 * octaves}"
        for name in _SIMPLE_KEYBOARD_INTERVAL_NAMES[offset].split(" / ")
    )


KEYBOARD_INTERVAL_NAMES = tuple(
    keyboard_interval_name(distance)
    for distance in range(1, KEYBOARD_FULL[1] - KEYBOARD_FULL[0] + 1)
)


@dataclass(kw_only=True)
class KeyboardIntervalSettings:
    """
    The keyboard range and interval distances used for keyboard interval
    identification.

    Attributes
    ----------
    low : int
        The lowest key, as a MIDI number. Keyword-only.
    high : int
        The highest key, inclusive. Keyword-only.
    intervals : set of int
        Selected distances in half steps, up to the full piano span.
        Keyword-only.

    button_count : int, default 6
        Maximum answer buttons in limited mode. Keyword-only.
    compact_buttons : bool, default False
        Answer with separate quality-letter and interval-number buttons.
        Keyword-only.
    all_interval_buttons : bool, default False
        Show a fixed answer button for every selected interval instead
        of a limited number of choices. Keyword-only.

    Examples
    --------
    >>> KeyboardIntervalSettings().bounds()
    (48, 72)
    """

    low: int = KEYBOARD_DEFAULT[0]
    high: int = KEYBOARD_DEFAULT[1]
    intervals: set[int] = field(default_factory=lambda: set(range(1, 13)))
    all_interval_buttons: bool = False
    compact_buttons: bool = False
    button_count: int = 6

    def answer_button_limit(self) -> int:
        """
        Return the requested count within the supported range of 1 to 87
        buttons.

        Returns
        -------
        int
            The bounded maximum number of answer buttons in limited
            mode.

        Examples
        --------
        >>> KeyboardIntervalSettings().answer_button_limit()
        6
        >>> KeyboardIntervalSettings(
        ...     button_count=0
        ... ).answer_button_limit()
        1
        """
        return max(1, min(len(KEYBOARD_INTERVAL_NAMES), self.button_count))

    def bounds(self) -> tuple[int, int]:
        """
        Return a piano range containing at least two distinct keys.

        Returns
        -------
        tuple of (int, int)
            Sorted bounds within the full piano range, widened by one
            key if necessary.

        Examples
        --------
        >>> KeyboardIntervalSettings(
        ...     low=60, high=60
        ... ).bounds()
        (60, 61)
        """
        first, last = KEYBOARD_FULL
        low, high = sorted(
            min(max(value, first), last) for value in (self.low, self.high)
        )
        if low == high:
            if high < last:
                high += 1
            else:
                low -= 1
        return low, high

    def active_intervals(self) -> list[int]:
        """
        Return selected interval distances that fit the keyboard range.

        Returns
        -------
        list of int
            Sorted positive distances that fit; empty if none are
            selected. Invalid nonempty selections use a minor second.

        Examples
        --------
        >>> KeyboardIntervalSettings(
        ...     low=60, high=64, intervals={3, 4, 12}
        ... ).active_intervals()
        [3, 4]
        >>> KeyboardIntervalSettings(
        ...     intervals=set()
        ... ).active_intervals()
        []
        """
        if not self.intervals:
            return []
        low, high = self.bounds()
        return sorted(
            distance
            for distance in self.intervals
            if 1 <= distance <= high - low
        ) or [1]


keyboard_intervals = KeyboardIntervalSettings()


@dataclass
class ConstructionSettings(ClefChoice, KeyChoice):
    """
    The settings of the note construction exercise.

    Attributes
    ----------
    clefs : set of str
        The clefs to ask on, any of `RANGE_KEYS`, so "grand" is allowed.
    accidentals : bool, default False
        Also ask for sharps and flats, which the answer then has to
        include. Keyword-only.
    key_signature : bool, default False
        Draw a key signature; it applies to the note unless the note is
        given its own sign. Keyword-only.
    question_type : str, default "scale"
        Use the selected scale keys or ask for notes without a scale
        key. Keyword-only.
    degrees : set of int
        Scale degrees to ask for in Scale and Degree mode. Keyword-only.
    octave : bool, default True
        Require the note to be placed in a specific octave.
        Keyword-only.
    staff_keys : set of int or None
        Staff signatures chosen independently. None uses the question
        key. Keyword-only.
    major : bool, default True
        Use major keys. With key signatures off, use C major.
        Keyword-only.
    minor : bool, default False
        Use relative minor keys. With key signatures off, use A minor.
        Keyword-only.
    keys : set of int
        The key signatures to draw from, as sharps (positive) or flats
        (negative). Keyword-only.

    minor_keys : set of int or None
        Signatures selected for minor keys. None uses the original
        shared selection. Keyword-only.

    Examples
    --------
    >>> ConstructionSettings(
    ...     clefs={"grand"}
    ... ).active_clefs()
    ['grand']
    """

    CLEF_ORDER: ClassVar[tuple[str, ...]] = RANGE_KEYS

    clefs: set[str] = field(
        default_factory=lambda: {"treble", "bass"},
    )  # any of RANGE_KEYS, so "grand" is allowed
    _: KW_ONLY
    # also ask for sharps and flats, which the answer then has to
    # include
    accidentals: bool = False
    # draw a key signature; it applies to the note unless you give the
    # note its own sign
    key_signature: bool = False
    question_type: str = "scale"
    degrees: set[int] = field(default_factory=lambda: set(range(1, 8)))
    octave: bool = True
    staff_keys: set[int] | None = None
    major: bool = True
    minor: bool = False
    keys: set[int] = field(
        default_factory=lambda: {
            -3,
            -2,
            -1,
            0,
            1,
            2,
            3,
        },
    )  # sharps (+) / flats (-) to draw from

    minor_keys: set[int] | None = None


construction = ConstructionSettings()


# Arpeggio exercise. The chord types are the names in
# theory.scales.CHORDS, triads first and then seventh chords.
ARPEGGIO_TRIADS = (
    "major",
    "minor",
    "diminished",
    "augmented",
)
ARPEGGIO_SEVENTHS = (
    "dominant 7th",
    "major 7th",
    "minor 7th",
    "half-diminished 7th",
    "diminished 7th",
)
ARPEGGIO_TYPES = ARPEGGIO_TRIADS + ARPEGGIO_SEVENTHS
INVERSIONS = (
    0,
    1,
    2,
    3,
    # root position, 1st, 2nd and 3rd inversion (the 3rd only exists for
    # seventh chords)
)


@dataclass
class ArpeggioSettings(ClefChoice, KeyChoice):
    """
    The settings of the arpeggio identification exercise.

    Attributes
    ----------
    clefs : set of str
        The clefs to draw on, any of `CLEFS`.
    types : set of str
        The chord types to ask, from `ARPEGGIO_TYPES`. Keyword-only.
    inversions : set of int
        The inversions to ask: 0 for root position up to 3 for the third
        inversion. Keyword-only.
    key_signature : bool, default False
        Draw a key signature, so the arpeggio only gets signs where it
        differs from it. Keyword-only.
    keys : set of int
        The key signatures to draw from, as sharps (positive) or flats
        (negative). Keyword-only.

    Examples
    --------
    >>> ArpeggioSettings().active_types()
    ['major', 'minor', 'dominant 7th', 'diminished 7th']
    """

    clefs: set[str] = field(
        default_factory=lambda: {"treble", "bass"},
    )  # any of CLEFS
    _: KW_ONLY
    types: set[str] = field(
        default_factory=lambda: {
            "major",
            "minor",
            "dominant 7th",
            "diminished 7th",
        },
    )
    inversions: set[int] = field(default_factory=lambda: set(INVERSIONS))
    # draw a key signature, so the arpeggio only gets signs where it
    # differs from it
    key_signature: bool = False
    keys: set[int] = field(
        default_factory=lambda: {
            -3,
            -2,
            -1,
            0,
            1,
            2,
            3,
        },
    )  # sharps (+) / flats (-) to draw from

    def active_types(self) -> list[str]:
        """
        Return the chord types to ask, triads first and then seventh
        chords.

        Returns
        -------
        list of str
            The chosen types in the order of `ARPEGGIO_TYPES`, or
            "major" if none are chosen.

        Examples
        --------
        >>> ArpeggioSettings(
        ...     types={"minor 7th", "major"}
        ... ).active_types()
        ['major', 'minor 7th']
        """
        return [t for t in ARPEGGIO_TYPES if t in self.types] or ["major"]

    def active_inversions(self) -> list[int]:
        """
        Return the inversions to ask, root position first.

        Returns
        -------
        list of int
            The chosen inversions, or root position (0) if none are
            chosen.

        Examples
        --------
        >>> ArpeggioSettings(
        ...     inversions={2, 0}
        ... ).active_inversions()
        [0, 2]
        """
        return [i for i in INVERSIONS if i in self.inversions] or [0]

    def inversions_for(self, chord_type: str) -> list[int]:
        """
        Return the inversions that can be asked for a chord type.

        A triad has no third inversion. If none of the chosen inversions
        applies (only the third, for a triad), root position is
        used.

        Parameters
        ----------
        chord_type : str
            A key of `CHORDS`, such as "major" or "dominant 7th".

        Returns
        -------
        list of int
            The inversions to choose from.

        Examples
        --------
        >>> cfg = ArpeggioSettings()
        >>> (
        ...     cfg.inversions_for("major"),
        ...     cfg.inversions_for("dominant 7th"),
        ... )
        ([0, 1, 2], [0, 1, 2, 3])
        >>> ArpeggioSettings(
        ...     inversions={3}
        ... ).inversions_for("major")
        [0]
        """
        allowed = [
            i
            for i in self.active_inversions()
            if i < (3 if chord_type in ARPEGGIO_TRIADS else 4)
        ]
        return allowed or [0]


arpeggio = ArpeggioSettings()


# Key signature identification: read the signature on a staff and name
# the key.
KEY_MODES = (
    "Major (Ionian)",
    "Dorian",
    "Phrygian",
    "Lydian",
    "Mixolydian",
    "Natural minor (Aeolian)",
    "Locrian",
)
MODE_LABELS = {
    "Major (Ionian)": "Major (Ionian)",
    "Dorian": "Dorian",
    "Phrygian": "Phrygian",
    "Lydian": "Lydian",
    "Mixolydian": "Mixolydian",
    "Natural minor (Aeolian)": "Minor (Aeolian)",
    "Locrian": "Locrian",
}


@dataclass
class KeySignatureSettings(ClefChoice, KeyChoice):
    """
    The settings of the key signature identification exercise.

    Attributes
    ----------
    clefs : set of str
        The clefs a signature is drawn on, any of `CLEFS`. Keyword-only.
    modes : set of str
        The scales to ask about, from `KEY_MODES`. Keyword-only.
    keys : set of int
        The key signatures asked, as sharps (positive) or flats
        (negative). Keyword-only.

    Examples
    --------
    >>> cfg = KeySignatureSettings()
    >>> cfg.active_clefs(), len(cfg.active_keys())
    (['treble', 'bass'], 15)
    """

    _: KW_ONLY
    clefs: set[str] = field(
        default_factory=lambda: {"treble", "bass"},
    )  # any of CLEFS: the clef the signature is drawn on
    modes: set[str] = field(
        default_factory=lambda: {"Major (Ionian)", "Natural minor (Aeolian)"},
    )  # of KEY_MODES
    keys: set[int] = field(
        default_factory=lambda: set(range(-7, 8)),
    )  # the key signatures asked: sharps (+) / flats (-)

    def active_modes(self) -> list[str]:
        """
        Return the scales to ask about, in the order of `KEY_MODES`.

        Returns
        -------
        list of str
            The chosen modes, or major if none are chosen.

        Examples
        --------
        >>> KeySignatureSettings().active_modes()
        ['Major (Ionian)', 'Natural minor (Aeolian)']
        """
        return [m for m in KEY_MODES if m in self.modes] or ["Major (Ionian)"]


key_signatures = KeySignatureSettings()


@dataclass
class OrderOfKeysSettings(KeySignatureSettings):
    """
    Choose the starting signs for writing a key signature.

    Attributes
    ----------
    starting_accidentals : set of int
        Allowed counts of given signs. Negative counts represent flats
        and positive counts represent sharps.

    Examples
    --------
    >>> OrderOfKeysSettings(
    ...     keys={-2, 4}
    ... ).available_starts()
    range(-2, 5)
    """

    _: KW_ONLY
    starting_accidentals: set[int] = field(default_factory=lambda: {0})

    def available_starts(self) -> range:
        """
        Return starting counts that fit at least one selected signature.

        Returns
        -------
        range
            Counts from the flattest eligible start through the
            sharpest, always including zero.

        Examples
        --------
        >>> list(
        ...     OrderOfKeysSettings(
        ...         keys={-2}
        ...     ).available_starts()
        ... )
        [-2, -1, 0]
        """
        keys = self.active_keys()
        return range(min(0, keys[0]), max(0, keys[-1]) + 1)


order_of_keys = OrderOfKeysSettings()


@dataclass
class KeyConstructionSettings(KeySignatureSettings):
    """
    The settings of the key signature construction exercise: the same
    choices as key signature identification.

    Attributes
    ----------
    clefs : set of str
        The clefs the blank staff is drawn in, any of `CLEFS`.
        Keyword-only.
    modes : set of str
        The scales to ask for, from `KEY_MODES`. Keyword-only.
    keys : set of int
        The key signatures to build, as sharps (positive) or flats
        (negative). Keyword-only.

    Examples
    --------
    >>> cfg = KeyConstructionSettings(keys={-2})
    >>> cfg.active_keys(), cfg.active_modes()
    ([-2], ['Major (Ionian)', 'Natural minor (Aeolian)'])
    """


key_construction = KeyConstructionSettings()


@dataclass
class ScaleIdentificationSettings(KeySignatureSettings):
    """
    Choose the clefs, scale types and independent staff and scale key
    signatures for identification.

    Attributes
    ----------
    staff_keys : set of int
        Signatures drawn on the staff, independently of the scale's own
        signature. Keyword-only.

    motion : str, default "ascending"
        Direction of the scale, "ascending" or "descending".
        Keyword-only.

    button_mode : str, default "limited"
        Show a limited set of complete answers or separate tonic and
        mode buttons in "all" mode. Keyword-only.
    button_count : int, default 6
        Maximum number of answer buttons in limited mode. Keyword-only.

    question_type : str, default "combined"
        Ask for the mode, the tonic (key), or both. Keyword-only.

    minor_keys : set of int or None
        Signatures for natural minor. None uses the shared key
        selection. Keyword-only.

    Examples
    --------
    >>> cfg = ScaleIdentificationSettings(
    ...     keys={2}, staff_keys={-3}
    ... )
    >>> cfg.active_keys(), cfg.active_staff_keys()
    ([2], [-3])
    """

    _: KW_ONLY
    question_type: str = "combined"
    button_mode: str = "limited"
    button_count: int = 6
    minor_keys: set[int] | None = None
    motion: str = "ascending"
    staff_keys: set[int] = field(default_factory=lambda: {0})

    def active_staff_keys(self) -> list[int]:
        """
        Return the selected staff signatures, falling back to no
        signature.

        Returns
        -------
        list of int
            Signature counts in ascending order.

        Examples
        --------
        >>> ScaleIdentificationSettings(
        ...     staff_keys=set()
        ... ).active_staff_keys()
        [0]
        """
        return sorted(self.staff_keys) or [0]


scale_identification = ScaleIdentificationSettings()


@dataclass
class ScaleConstructionSettings(KeySignatureSettings):
    """
    The settings of the scale construction exercise: the same choices as
    key signature identification.

    Here "keys" chooses the scale by the signature it has: G major and E
    minor both have one sharp. `staff_keys` is a
    separate choice: the key signature drawn on the staff, which need
    not be the scale's. On a staff with two flats a C
    major scale has to be placed with naturals where the staff would
    otherwise flatten the notes.

    Attributes
    ----------
    clefs : set of str
        The clefs the scale is placed on, any of `CLEFS`. Keyword-only.
    modes : set of str
        The kinds of scale to ask for, from `KEY_MODES`. Keyword-only.
    keys : set of int
        The key signatures the scales have, as sharps (positive) or
        flats (negative). Keyword-only.
    steps : bool, default False
        Also mark the whole and half steps between the notes, once the
        notes are placed. Keyword-only.
    staff_keys : set of int
        The key signatures that may be drawn on the staff, as sharps
        (positive) or flats (negative); 0 is none.
        Keyword-only.
    octave : bool, default False
        Name the octave of the first note, such as "G2 Major", and
        require the scale to start there; any scale asked then
        fits on the staff and its ledger lines. Without it any octave is
        accepted. Keyword-only.

    motion : str, default "ascending"
        Direction of the scale, "ascending" or "descending".
        Keyword-only.

    minor_keys : set of int or None
        Signatures for natural minor. None uses the shared key
        selection. Keyword-only.

    Examples
    --------
    >>> cfg = ScaleConstructionSettings(keys={3})
    >>> (
    ...     cfg.active_keys(),
    ...     cfg.active_clefs(),
    ...     cfg.steps,
    ...     cfg.octave,
    ...     cfg.active_staff_keys(),
    ... )
    ([3], ['treble', 'bass'], False, False, [0])
    """

    _: KW_ONLY
    minor_keys: set[int] | None = None
    motion: str = "ascending"
    steps: bool = False  # also mark the whole and half steps between the notes
    # name the octave of the first note, and require the scale to start
    # there
    octave: bool = False
    staff_keys: set[int] = field(
        default_factory=lambda: {0},
    )  # the key signatures drawn on the staff: sharps (+) / flats (-)

    def active_staff_keys(self) -> list[int]:
        """
        Return the key signatures that may be drawn on the staff, lowest
        first.

        Returns
        -------
        list of int
            Sharps (positive) or flats (negative); no sharps or flats if
            none are chosen.

        Examples
        --------
        >>> ScaleConstructionSettings(
        ...     staff_keys={-2, 3}
        ... ).active_staff_keys()
        [-2, 3]
        >>> ScaleConstructionSettings(
        ...     staff_keys=set()
        ... ).active_staff_keys()
        [0]
        """
        return sorted(self.staff_keys) or [0]


scale_construction = ScaleConstructionSettings()


# The three clef symbols: the G clef, the C clef and the F clef. Every
# clef is one of them, put on a particular line.
CLEF_SYMBOLS = ("G", "C", "F")
CLEF_SYMBOL_NAMES = {"G": "G clef", "C": "C clef", "F": "F clef"}


CLEF_QUESTION_TYPES = {
    "construction": "Clef Construction",
    "identification": "Clef Identification",
    # what the clef exercise asks: to put a named clef on a blank staff,
    # or
    # to name the clef on a staff
}


@dataclass
class ClefBasicsSettings(ClefChoice):
    """
    The settings of the clef basics exercise: what kind of question is
    asked, and which clefs.

    Every clef is one of three symbols, the G, C or F clef, put on a
    line of the staff: the mezzo-soprano clef is the C clef
    on the second line. The three symbols can always be chosen from.

    Attributes
    ----------
    clefs : set of str
        The clefs that are asked for, any of `CLEF_BASICS_CLEFS`.
        Keyword-only.
    question_type : str, default "construction"
        "construction" to put a named clef on a blank staff, or
        "identification" to name the clef shown on a staff by pressing
        a button. Keyword-only.

    Examples
    --------
    >>> ClefBasicsSettings(
    ...     clefs={"subbass", "alto"}
    ... ).active_clefs()
    ['alto', 'subbass']
    >>> ClefBasicsSettings().question_type
    'construction'
    """

    CLEF_ORDER: ClassVar[tuple[str, ...]] = CLEF_BASICS_CLEFS

    _: KW_ONLY
    clefs: set[str] = field(
        default_factory=lambda: {"treble", "bass"},
    )  # any of CLEF_BASICS_CLEFS: the clefs that are asked for
    question_type: str = "construction"  # a key of CLEF_QUESTION_TYPES

    def active_type(self) -> str:
        """
        Return the kind of question to ask.

        Returns
        -------
        str
            "construction" or "identification"; construction if the
            setting is anything else.

        Examples
        --------
        >>> ClefBasicsSettings(
        ...     question_type="identification"
        ... ).active_type()
        'identification'
        >>> ClefBasicsSettings(
        ...     question_type="nonsense"
        ... ).active_type()
        'construction'
        """
        return (
            self.question_type
            if self.question_type in CLEF_QUESTION_TYPES
            else "construction"
        )

    def answer_clefs(self) -> list[str]:
        """
        Return the clefs to offer as buttons when a clef is to be named:
        those asked for, and enough others to have a choice.

        Returns
        -------
        list of str
            In canonical order; at least two, the treble and bass clefs
            being added if only one is asked for.

        Examples
        --------
        >>> ClefBasicsSettings(
        ...     clefs={"alto", "tenor"}
        ... ).answer_clefs()
        ['alto', 'tenor']
        >>> ClefBasicsSettings(
        ...     clefs={"alto"}
        ... ).answer_clefs()
        ['treble', 'alto']
        """
        chosen = set(self.active_clefs())
        for extra in ("treble", "bass", "alto"):
            if len(chosen) >= 2:
                break
            chosen.add(extra)
        return [c for c in CLEF_BASICS_CLEFS if c in chosen]


clef_basics = ClefBasicsSettings()

NOTATION_TERMS = tuple(MARKS)


@dataclass
class NotationSettings:
    """
    Terms eligible to be highlighted in Notation Identification.

    Examples
    --------
    >>> "Notehead" in NotationSettings().terms
    True
    """

    terms: set[str] = field(default_factory=lambda: set(NOTATION_TERMS))
    question_type: str = "button"


NOTATION_QUESTION_TYPES = {
    "staff": "Click on Staff",
    "button": "Answer Button",
}

notation = NotationSettings()


# Circle of fifths exercise: what to ask about the circle.
CIRCLE_QUESTIONS = {
    "major": "Relative major",
    "minor": "Relative minor",
    "numeral": "Roman numerals",
}


@dataclass
class CircleSettings:
    """
    The settings of the circle of fifths exercise.

    Attributes
    ----------
    questions : set of str
        The kinds of question to ask, keys of `CIRCLE_QUESTIONS`: the
        relative major of a minor key, the relative minor of a
        major key, and the Roman numeral of a chord of a key.
    scheme : str
        The key of the color scheme the circle is drawn in: a preset of
        `alto.circle_schemes` or one of `customs`.
    customs : list of CustomRecord
        The color schemes the user made.

    Examples
    --------
    >>> CircleSettings().active_questions()
    ['major', 'minor', 'numeral']
    >>> CircleSettings(
    ...     questions={"numeral"}
    ... ).active_questions()
    ['numeral']
    >>> CircleSettings().active_scheme().name
    'Cyan to indigo'
    """

    questions: set[str] = field(
        default_factory=lambda: set(CIRCLE_QUESTIONS),
    )  # keys of CIRCLE_QUESTIONS
    scheme: str = DEFAULT_SCHEME
    customs: list[CustomRecord] = field(default_factory=list)

    def active_questions(self) -> list[str]:
        """
        Return the kinds of question to ask, in the order they are
        listed.

        Returns
        -------
        list of str
            The chosen kinds, or all of them if none is chosen.

        Examples
        --------
        >>> CircleSettings(
        ...     questions=set()
        ... ).active_questions()
        ['major', 'minor', 'numeral']
        >>> CircleSettings(
        ...     questions={"minor", "nonsense"}
        ... ).active_questions()
        ['minor']
        """
        return [q for q in CIRCLE_QUESTIONS if q in self.questions] or list(
            CIRCLE_QUESTIONS,
        )

    def active_scheme(self) -> Scheme:
        """
        Return the color scheme to draw the circle in.

        Returns
        -------
        Scheme
            The chosen scheme, or the default if the saved choice is no
            longer available, such as a deleted custom scheme.

        Examples
        --------
        >>> CircleSettings(
        ...     scheme="midnight"
        ... ).active_scheme().name
        'Midnight'
        >>> CircleSettings(
        ...     scheme="deleted"
        ... ).active_scheme().key
        'cyan-indigo'
        """
        return resolve(self.scheme, customs=self.customs)


circle = CircleSettings()
