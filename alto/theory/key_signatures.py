"""Staff positions for written key signatures."""

from alto.theory.pitch import Note

# Diatonic index of the bottom staff line.
BOTTOM_LINE = {
    "treble": Note(4, letter=2).diatonic,  # E4
    "bass": Note(2, letter=4).diatonic,  # G2
    "alto": Note(3, letter=3).diatonic,  # F3
    "tenor": Note(3, letter=1).diatonic,  # D3
    "soprano": Note(4, letter=0).diatonic,  # C4
    "mezzo": Note(3, letter=5).diatonic,  # A3
    "baritone": Note(2, letter=6).diatonic,  # B2
}

# Where each key-signature accidental sits, in order of appearance. Each
# is a fourth up or a fifth down from the one before
# (sharps: F C G D A E B, flats: B E A D G C F), and the pattern is
# chosen so that all seven stay on the staff, or one step
# above or below it. This gives the usual signatures for the treble,
# bass, alto and tenor clefs, and works out the rest.
_SHARP_PATTERNS = (
    (
        -3,
        4,
        -3,
        -3,
        4,
        -3,
    ),
    (
        4,
        -3,
        4,
        -3,
        4,
        -3,
    ),
)
_FLAT_PATTERNS = (
    (
        3,
        -4,
        3,
        -4,
        3,
        -4,
    ),
    (
        -4,
        3,
        -4,
        3,
        -4,
        3,
    ),
)


def key_signature_positions(
    clef: str,
    *,
    sign: int,
) -> list[str]:
    """
    Return the notes the sharps or flats of a key signature are written
    on, in a clef.

    Each accidental is a fourth up or a fifth down from the one before
    (sharps: F C G D A E B, flats: B E A D G C F), and the
    pattern is chosen so that all seven stay on the staff, or one step
    above or below it. This gives the usual signatures for
    the treble, bass, alto and tenor clefs, and works out the rest.

    Parameters
    ----------
    clef : str
        A key of `BOTTOM_LINE`.
    sign : int
        1 for sharps, -1 for flats. Keyword-only.

    Returns
    -------
    list of str
        Seven note names with octaves, in the order the accidentals
        appear.

    Raises
    ------
    ValueError
        If no placement keeps all seven accidentals on the staff.

    Examples
    --------
    >>> key_signature_positions("treble", sign=1)
    ['F5', 'C5', 'G5', 'D5', 'A4', 'E5', 'B4']
    >>> key_signature_positions("bass", sign=-1)
    ['B2', 'E3', 'A2', 'D3', 'G2', 'C3', 'F2']
    """
    bottom = BOTTOM_LINE[clef]
    first, patterns = (
        ("F", _SHARP_PATTERNS) if sign > 0 else ("B", _FLAT_PATTERNS)
    )
    for steps in patterns:
        for start in range(bottom - 1, bottom + 10):
            offsets = [0]
            for s in steps:
                offsets.append(offsets[-1] + s)
            places = [start + o for o in offsets]
            if Note.from_diatonic(start).name == first and all(
                bottom - 1 <= d <= bottom + 9 for d in places
            ):
                return [
                    f"{n.name}{n.octave}"
                    for n in [Note.from_diatonic(d) for d in places]
                ]
    raise ValueError(f"no key signature fits the {clef} clef")


def written_signature(clef: str, *, key: int) -> list[Note]:
    """
    Spell a key signature at its conventional staff positions, from left
    to right.

    Parameters
    ----------
    clef : str
        The clef the signature is written in.
    key : int
        Signed count of sharps or flats.

    Returns
    -------
    list of Note
        Pitches of the printed accidentals, including their octaves and
        signs.

    Examples
    --------
    >>> [
    ...     str(note)
    ...     for note in written_signature(
    ...         "bass", key=-2
    ...     )
    ... ]
    ['B♭2', 'E♭3']
    """
    sign = 1 if key > 0 else -1
    positions = key_signature_positions(clef, sign=sign)[: abs(key)]
    return [
        Note.from_diatonic(Note.parse(pos).diatonic, accidental=sign)
        for pos in positions
    ]
