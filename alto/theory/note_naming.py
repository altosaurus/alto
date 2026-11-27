"""Written and spoken names for pitches and scale degrees."""

from __future__ import annotations

from alto.theory.pitch import ACCIDENTAL_SYMBOLS, LETTERS, Note, key_accidental

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


def note_name(
    note: Note,
    *,
    naming: str = "letters",
    key: int | None = None,
    minor: bool = False,
) -> str:
    """
    Return a note's name as it is written, with its octave: F♯4.

    Parameters
    ----------
    note : Note
        The written pitch.
    naming : str, default "letters"
        "letters", "solfege" (fixed do), "degrees", or "functions".
    key : int or None, default None
        The major key signature for scale degrees. Without a key
        context, degrees fall back to letter names. Keyword-only.

    minor : bool, default False
        Use natural minor scale degrees. Keyword-only.

    Returns
    -------
    str
        The label in the requested naming system, including its octave.

    Examples
    --------
    >>> note_name(Note.parse("F#4"))
    'F♯4'
    """
    if naming in DEGREE_NAMINGS and key is None:
        naming = "letters"
    return spell(
        note,
        naming=naming,
        key=key or 0,
        octave=True,
        minor=minor,
    )


def note_words(
    note: Note,
    *,
    naming: str = "letters",
    key: int | None = None,
    minor: bool = False,
) -> str:
    """
    Return a note's name in words, for a screen reader: "F sharp 4".

    Parameters
    ----------
    note : Note
        The written pitch.
    naming : str, default "letters"
        "letters", "solfege" (fixed do), "degrees", or "functions".
    key : int or None, default None
        The major key signature for scale degrees. Without a key
        context, use letter names. Keyword-only.

    minor : bool, default False
        Use natural minor scale degrees. Keyword-only.

    Returns
    -------
    str
        The spoken label and octave, with accidentals written in words.

    Examples
    --------
    >>> (
    ...     note_words(Note.parse("F#4")),
    ...     note_words(Note.parse("Bb3")),
    ...     note_words(Note.parse("C4")),
    ... )
    ('F sharp 4', 'B flat 3', 'C 4')
    """
    if naming in DEGREE_NAMINGS and key is not None:
        if naming == "functions":
            return (
                f"{spell(note, naming=naming, key=key, minor=minor).lower()}"
                ", octave "
                f"{note.octave}"
            )
        degree = spell(note, naming="degrees", key=key, minor=minor).replace(
            "̂",
            "",
        )
        signs = {
            "♯": "sharp ",
            "♭": "flat ",
            "𝄪": "double sharp ",
            "𝄫": "double flat ",
        }
        label = f"degree {degree[-1]}"
        return f"{signs.get(degree[0], '')}{label}, octave {note.octave}"
    if naming in DEGREE_NAMINGS:
        naming = "letters"
    plain = spell(Note(note.octave, letter=note.letter), naming=naming)
    sign = {
        -2: " double flat",
        -1: " flat",
        1: " sharp",
        2: " double sharp",
        0: "",
    }.get(note.accidental, "")
    return f"{plain}{sign} {note.octave}"
