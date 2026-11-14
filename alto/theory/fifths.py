"""
The circle of fifths: the twelve keys in order, each major with its relative minor.

Going clockwise from C at the top, each key is a fifth above the one before, so it has one more sharp (or one fewer flat).
The relative minor of a major key has the same key signature and starts on its sixth note: A minor goes with C major.

A key has six chords that fit on the circle: the major triads I, IV and V on the outer ring, and the minor triads ii, iii and
vi on the inner ring. They are the key's own wedge and the wedge on each side of it, on both rings. (The seventh chord, vii°,
is diminished and has no wedge.)

Examples
--------
>>> MAJORS[3], MINORS[3], SIGNATURES[3]
(('A',), ('F♯m',), 3)
>>> relative_minor("A")
'F♯m'
>>> numeral_chords(1)
{'I': 'G', 'ii': 'Am', 'iii': 'Bm', 'IV': 'C', 'V': 'D', 'vi': 'Em'}
>>> accidentals_of(-2)
['B♭', 'E♭']
"""

from __future__ import annotations

from alto.theory.pitch import (
    Note,
)
from alto.theory.scales import (
    SCALES,
    build,
)

MAJORS: tuple[tuple[str, ...], ...] = (
    ("C",),
    ("G",),
    ("D",),
    ("A",),
    ("E",),
    ("B", "C♭"),
    ("F♯", "G♭"),
    ("D♭", "C♯"),
    ("A♭",),
    ("E♭",),
    ("B♭",),
    ("F",),
)  # the major key at each place, clockwise from the top; a key with two names is written both ways on the circle
MINORS: tuple[tuple[str, ...], ...] = (
    ("Am",),
    ("Em",),
    ("Bm",),
    ("F♯m",),
    ("C♯m",),
    ("G♯m", "A♭m"),
    ("D♯m", "E♭m"),
    ("B♭m", "A♯m"),
    ("Fm",),
    ("Cm",),
    ("Gm",),
    ("Dm",),
)  # the relative minor at each place: the minor with the same key signature as the major
SIGNATURES = (0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1)  # sharps (+) or flats (-) at each place, by the key's first name
NUMERALS: tuple[str, ...] = (
    "I",
    "ii",
    "iii",
    "IV",
    "V",
    "vi",
)  # the chords of a key that are on the circle, capitals for major and small for minor
ORDER_OF_SHARPS = "FCGDAEB"  # the sharps of a key signature are added in this order, and the flats in the order backwards
INTRO = (
    "The circle of fifths puts the twelve keys in order. Each step clockwise is a fifth higher and adds a sharp to the key "
    "signature (or takes away a flat); each step the other way adds a flat. The outer ring has the major keys and the inner "
    "ring their relative minors. Click a key, or use the arrow keys."
)
CELLS_OF_A_KEY = {
    ("outer", -1): "IV",
    ("outer", 0): "I",
    ("outer", 1): "V",
    ("inner", -1): "ii",
    ("inner", 0): "vi",
    ("inner", 1): "iii",
}  # which wedge of which ring holds each chord, as steps round the circle from the key's own wedge: IV is a step to the left


def place_of_major(name: str) -> int:
    """
    Return where a major key is on the circle, by either of its names.

    Parameters
    ----------
    name : str
        The key's name, such as "A", "B♭" or "C♭".

    Returns
    -------
    int
        The place, clockwise from C at 0.

    Raises
    ------
    ValueError
        If no key has that name.

    Examples
    --------
    >>> place_of_major("A"), place_of_major("C♭"), place_of_major("G♭")
    (3, 5, 6)
    """
    for place, names in enumerate(MAJORS):
        if name in names:
            return place
    raise ValueError(f"no major key is called {name}")


def relative_minor(name: str) -> str:
    """
    Return the relative minor of a major key.

    Parameters
    ----------
    name : str
        The major key's name.

    Returns
    -------
    str
        The first name of its relative minor, such as "F♯m" for A.

    Examples
    --------
    >>> relative_minor("C"), relative_minor("E♭"), relative_minor("C♯")
    ('Am', 'Cm', 'B♭m')
    """
    return MINORS[place_of_major(name)][0]


def cells_of_key(place: int) -> dict[tuple[str, int], str]:
    """
    Return the six wedges that hold the chords of a major key, and the Roman numeral of each.

    Parameters
    ----------
    place : int
        The key's own place on the circle, clockwise from C at 0.

    Returns
    -------
    dict of tuple of (str, int) to str
        For each of the six cells, its ring ("outer" or "inner") and place, the numeral of its chord.

    Examples
    --------
    >>> cells = cells_of_key(0)
    >>> cells[("outer", 11)], cells[("inner", 0)], cells[("inner", 1)]  # F is IV; Am is vi; Em is iii
    ('IV', 'vi', 'iii')
    >>> cells[("outer", 1)]  # G is V
    'V'
    >>> len(cells_of_key(11)), cells_of_key(11)[("outer", 10)]  # in F major, B♭ is IV
    (6, 'IV')
    """
    return {(ring, (place + step) % 12): numeral for (ring, step), numeral in CELLS_OF_A_KEY.items()}


def numeral_chords(place: int) -> dict[str, str]:
    """
    Return the six chords of a major key that are on the circle, spelt as that key spells them.

    A wedge with two names, such as D♭ and C♯, is the same chord, but the key decides which name is right: C♯ is the V of F♯.

    Parameters
    ----------
    place : int
        The key's own place on the circle.

    Returns
    -------
    dict of str to str
        The chord's name for each numeral, in the order of `NUMERALS`: "G", "Am" and so on.

    Examples
    --------
    >>> numeral_chords(0)
    {'I': 'C', 'ii': 'Dm', 'iii': 'Em', 'IV': 'F', 'V': 'G', 'vi': 'Am'}
    >>> numeral_chords(6)["V"], numeral_chords(7)["IV"]  # in F♯ major the V is C♯; in D♭ major the IV is G♭
    ('C♯', 'G♭')
    """
    tonic = Note.parse(MAJORS[place][0].replace("♯", "#").replace("♭", "b") + "4")
    scale = build(tonic, intervals=SCALES["Major (Ionian)"])
    degree = {"I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5}
    return {numeral: scale[degree[numeral]].name + ("m" if numeral.islower() else "") for numeral in NUMERALS}


def display_major(place: int) -> str:
    """
    Return the major key of a place as it is written to ask about it: "A major", or "B major / C♭ major".

    Parameters
    ----------
    place : int
        The place on the circle.

    Returns
    -------
    str
        The name, with both names when the wedge has two.

    Examples
    --------
    >>> display_major(3), display_major(5)
    ('A major', 'B major / C♭ major')
    """
    return " / ".join(f"{name} major" for name in MAJORS[place])


def display_minor(place: int) -> str:
    """
    Return the minor key of a place as it is written to ask about it: "F♯ minor", or "G♯ minor / A♭ minor".

    Parameters
    ----------
    place : int
        The place on the circle.

    Returns
    -------
    str
        The name, with both names when the wedge has two.

    Examples
    --------
    >>> display_minor(3), display_minor(5)
    ('F♯ minor', 'G♯ minor / A♭ minor')
    """
    return " / ".join(f"{name[:-1]} minor" for name in MINORS[place])


def accidentals_of(signature: int) -> list[str]:
    """
    Return the sharps or flats of a key signature, in the order they are written.

    Parameters
    ----------
    signature : int
        The number of sharps (positive) or flats (negative).

    Returns
    -------
    list of str
        The notes that are altered: "F♯", "C♯" and so on, or "B♭", "E♭" and so on.

    Examples
    --------
    >>> accidentals_of(3), accidentals_of(0)
    (['F♯', 'C♯', 'G♯'], [])
    """
    if signature >= 0:
        return [f"{letter}♯" for letter in ORDER_OF_SHARPS[:signature]]
    return [f"{letter}♭" for letter in ORDER_OF_SHARPS[::-1][:-signature]]


def _count(signature: int) -> str:
    """
    Say a key signature in words.

    Parameters
    ----------
    signature : int
        The number of sharps (positive) or flats (negative).

    Returns
    -------
    str
        "no sharps or flats", "1 sharp: F♯", "2 flats: B♭, E♭" and so on.

    Examples
    --------
    >>> _count(0), _count(1), _count(-2)
    ('no sharps or flats', '1 sharp: F♯', '2 flats: B♭, E♭')
    """
    if signature == 0:
        return "no sharps or flats"
    word = "sharp" if signature > 0 else "flat"
    n = abs(signature)
    return f"{n} {word}{'s' if n > 1 else ''}: {', '.join(accidentals_of(signature))}"


def explain(ring: str, *, place: int) -> str:
    """
    Explain a cell of the circle: its key signature, where it comes from, its relative key and its chords.

    Parameters
    ----------
    ring : str
        "outer" for the major key at the place, "inner" for its relative minor.
    place : int
        The place on the circle, clockwise from C at 0. Keyword-only.

    Returns
    -------
    str
        Simple HTML, a few short paragraphs.

    Examples
    --------
    >>> text = explain("outer", place=1)
    >>> "<b>G major</b>" in text and "1 sharp: F♯" in text and "a fifth above C" in text
    True
    >>> "relative major, <b>C major</b>" in explain("inner", place=0)
    True
    >>> "<b>C♭ major</b>" in explain("outer", place=5) and "7 flats" in explain("outer", place=5)
    True
    """
    major, minor = MAJORS[place][0], MINORS[place][0][:-1]
    signature = SIGNATURES[place]
    outer = ring == "outer"
    own = f"{major} major" if outer else f"{minor} minor"
    paragraphs = [f"<b>{own}</b> has {_count(signature)}."]
    other = (MAJORS if outer else MINORS)[place]
    if len(other) == 2:  # the same key spelt the other way has the other signature
        spelt = f"{other[1]} major" if outer else f"{other[1][:-1]} minor"
        flipped = signature - 12 if signature > 0 else signature + 12
        paragraphs.append(f"It can also be spelt <b>{spelt}</b>, which has {_count(flipped)}.")
    mode = "major" if outer else "minor"
    if place == 0:
        paragraphs.append(
            f"{own} is where the circle starts. Going clockwise, each key is a fifth higher than the one before, "
            "and its signature gains a sharp.",
        )
    else:
        before = (MAJORS if outer else MINORS)[(place - 1) % 12][0]
        before = before if outer else before[:-1]
        paragraphs.append(
            f"It is a fifth above {before}, one step clockwise: its first note is five notes up from {before}'s, which is why "
            f"each step round the circle changes the signature by one. {before} {mode} is one step back.",
        )
    relative = (
        f"Its relative minor, <b>{minor} minor</b>, is just inside it."
        if outer
        else f"Its relative major, <b>{major} major</b>, is just outside it."
    )
    paragraphs.append(f"{relative} The two share a key signature: {minor} is the sixth note of the {major} major scale.")
    chords = numeral_chords(place)
    paragraphs.append(
        f"The chords of {major} major that sit on the circle are lit. On the outer ring, the key and its two neighbours are "
        f"the major chords I ({chords['I']}), IV ({chords['IV']}, a fifth below) and V ({chords['V']}, a fifth above). On the "
        f"inner ring, the minor chords ii ({chords['ii']}), iii ({chords['iii']}) and vi ({chords['vi']}) sit under them.",
    )
    return "".join(f"<p>{text}</p>" for text in paragraphs)
