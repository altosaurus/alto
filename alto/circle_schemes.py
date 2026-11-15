"""
The colour schemes of the circle of fifths: the presets, and the schemes a user makes.

A scheme says what colour each of the 24 cells of the circle is when it is quiet and when it is lit, and whether its wedges
are light, with dark names. The circle blends between the two as a cell brightens. The disc in the middle is not part of a
scheme: it takes the colours of the app's theme. Nothing here needs Qt, so the schemes can be tested, saved and shown anywhere;
`alto.ui.circle` turns them into pictures.

A colour is a hue (0 to 360), a saturation and a lightness (both 0 to 1).

Examples
--------
>>> scheme = preset("cyan-indigo")
>>> scheme.name, scheme.light
('Cyan to indigo', False)
>>> round(scheme.colour("outer", place=0, lift=1.0)[2], 2) > round(scheme.colour("outer", place=0, lift=0.0)[2], 2)
True
"""

from __future__ import annotations

import colorsys
import json
import re
from dataclasses import dataclass
from typing import (
    Protocol,
    TypedDict,
)

Hsl = tuple[float, float, float]
Cell = tuple[Hsl, Hsl]  # a cell's colour when it is quiet, and when it is fully lit


class CellMaker(Protocol):
    """A function that gives the cell at a place on a ring its quiet and lit colours."""

    def __call__(
        self,
        place: int,
        /,
        *,
        inner: bool,
    ) -> Cell:
        """
        Return the colours of one cell.

        Parameters
        ----------
        place : int
            The place clockwise from the top, 0 to 11.
        inner : bool
            Whether the cell is on the inner ring. Keyword-only.

        Returns
        -------
        tuple of tuple of float
            The quiet and the lit colour.
        """
        ...


DEFAULT_SCHEME = "cyan-indigo"
MAX_BRIGHTNESS = 0.42  # the brightest a cell looks on dark wedges, so that white names stay easy to read whatever its hue
CUSTOM_LIMIT = 24  # how many schemes of their own a user can keep
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
MODES = {
    "single": ("One colour", ("Colour",)),
    "rings": ("Two rings", ("Outer ring", "Inner ring")),
    "signature": ("By key signature", ("Flat keys", "C", "Sharp keys")),
    "distance": ("Distance from C", ("C", "F♯")),
    "wheel": ("Round the circle", ("First colour",)),
}  # how a scheme of the user's own is made, with the colours each takes
DARK_NAMES = {"ink": "#f5f5f5", "muted": "#b2b2ba"}  # the colours of the names on dark wedges
LIGHT_NAMES = {"ink": "#1b2030", "muted": "#4b5265"}  # and on light ones


class CustomRecord(TypedDict):
    """
    A scheme of the user's own, as it is saved.

    Attributes
    ----------
    id : str
        Its key, such as "custom-1".
    name : str
        What the user called it.
    mode : str
        How its colours are made: a key of `MODES`.
    colours : list of str
        The colours the mode takes, as "#rrggbb": what a cell looks like when it is lit.
    light : bool
        Whether the wedges are light, with dark names.
    """

    id: str
    name: str
    mode: str
    colours: list[str]
    light: bool


@dataclass(frozen=True)
class Scheme:
    """
    A colour scheme for the circle.

    Attributes
    ----------
    key : str
        Its identifier, used to save the choice.
    name : str
        Its name, as the settings show it.
    description : str
        A sentence about it.
    light : bool
        Whether the wedges are light, with dark names, instead of dark with white names.
    cells : dict of str to tuple of (tuple of float, tuple of float)
        For each ring ("outer" and "inner"), the 12 cells' quiet and lit colours, clockwise from the top.
    """

    key: str
    name: str
    description: str
    light: bool
    cells: dict[str, tuple[Cell, ...]]

    def colour(
        self,
        ring: str,
        *,
        place: int,
        lift: float,
    ) -> tuple[float, float, float]:
        """
        Return the colour of a cell as it is lit.

        Parameters
        ----------
        ring : str
            "outer" or "inner".
        place : int
            The cell's place, clockwise from the top. Keyword-only.
        lift : float
            How lit it is, from 0 (quiet) to 1 (fully lit). Keyword-only.

        Returns
        -------
        tuple of float
            Its red, green and blue, each from 0 to 1.

        Examples
        --------
        >>> red, green, blue = preset("spectrum").colour("outer", place=0, lift=1.0)
        >>> red > green and red > blue
        True
        >>> preset("spectrum").colour("outer", place=6, lift=0.0)[0] < 0.2
        True
        """
        quiet, lit = self.cells[ring][place % 12]
        hue = quiet[0] + ((lit[0] - quiet[0] + 180.0) % 360.0 - 180.0) * lift  # by the short way round the wheel
        saturation = quiet[1] + (lit[1] - quiet[1]) * lift
        lightness = quiet[2] + (lit[2] - quiet[2]) * lift
        return rgb_of((hue, saturation, lightness), capped=not self.light)

    def names(self) -> dict[str, str]:
        """
        Return the colours of the names written on the wedges.

        Returns
        -------
        dict of str to str
            "ink" (a key's name) and "muted" (its other name and its numeral), as "#rrggbb".

        Examples
        --------
        >>> preset("paper").names()["ink"], preset("spectrum").names()["ink"]
        ('#1b2030', '#f5f5f5')
        """
        return dict(LIGHT_NAMES if self.light else DARK_NAMES)


def rgb_of(
    colour: Hsl,
    *,
    capped: bool,
) -> tuple[float, float, float]:
    """
    Turn a colour into red, green and blue, keeping a dark circle's cells from getting too bright.

    Yellows and greens look far brighter than blues of the same lightness, so on dark wedges a colour that is brighter than
    white names can stand is brought down to the limit.

    Parameters
    ----------
    colour : tuple of float
        The hue, saturation and lightness.
    capped : bool
        Whether to bring a too bright colour down. Keyword-only.

    Returns
    -------
    tuple of float
        Red, green and blue, each from 0 to 1.

    Examples
    --------
    >>> r, g, b = rgb_of((60.0, 0.9, 0.5), capped=True)
    >>> 0.299 * r + 0.587 * g + 0.114 * b <= MAX_BRIGHTNESS + 1e-9
    True
    >>> rgb_of((0.0, 0.0, 1.0), capped=False)
    (1.0, 1.0, 1.0)
    """
    hue, saturation, lightness = (colour[0] % 360.0) / 360.0, min(max(colour[1], 0.0), 1.0), min(max(colour[2], 0.0), 1.0)
    red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
    for _ in range(6):  # each step gets closer; the first is not enough for a saturated yellow or orange
        seen = (0.299 * red + 0.587 * green + 0.114 * blue) / MAX_BRIGHTNESS
        if not capped or seen <= 1.0:
            break
        lightness /= seen
        red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
    return red, green, blue


def hex_of(rgb: tuple[float, float, float]) -> str:
    """
    Write a colour as "#rrggbb".

    Parameters
    ----------
    rgb : tuple of float
        Red, green and blue, each from 0 to 1.

    Returns
    -------
    str
        The colour as hexadecimal.

    Examples
    --------
    >>> hex_of((1.0, 0.5, 0.0))
    '#ff8000'
    """
    return "#" + "".join(f"{round(min(max(part, 0.0), 1.0) * 255):02x}" for part in rgb)


def hsl_of(text: str) -> Hsl:
    """
    Read a colour written as "#rrggbb".

    Parameters
    ----------
    text : str
        The colour.

    Returns
    -------
    tuple of float
        Its hue (0 to 360), saturation and lightness.

    Examples
    --------
    >>> hsl_of("#ff0000")
    (0.0, 1.0, 0.5)
    """
    red, green, blue = (int(text[at : at + 2], 16) / 255 for at in (1, 3, 5))
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    return hue * 360.0, saturation, lightness


def signature_of(place: int) -> int:
    """
    Return how far a place is from C, with flats as negative: the key signature of the major key there.

    Parameters
    ----------
    place : int
        The place clockwise from the top, 0 to 11.

    Returns
    -------
    int
        From -5 (five flats) to 6 (six sharps).

    Examples
    --------
    >>> [signature_of(at) for at in (0, 1, 6, 7, 11)]
    [0, 1, 6, -5, -1]
    """
    return place if place <= 6 else place - 12


def _scheme(
    key: str,
    *,
    name: str,
    description: str,
    cell: CellMaker,
    light: bool = False,
) -> Scheme:
    """
    Make a scheme from a function that gives each cell its quiet and lit colours.

    Parameters
    ----------
    key : str
        Its identifier.
    name : str
        Its name. Keyword-only.
    description : str
        A sentence about it. Keyword-only.
    cell : CellMaker
        Given a place and whether it is on the inner ring, the cell's quiet and lit colours. Keyword-only.
    light : bool, default False
        Whether the wedges are light. Keyword-only.

    Returns
    -------
    Scheme
        The scheme.

    Examples
    --------
    >>> flat = _scheme("flat", name="Flat", description="", cell=lambda _, *, inner: ((0.0, 0.5, 0.2), (0.0, 0.5, 0.5)))
    >>> flat.cells["inner"][11][1]
    (0.0, 0.5, 0.5)
    """
    cells = {ring: tuple(cell(place, inner=ring == "inner") for place in range(12)) for ring in ("outer", "inner")}
    return Scheme(key=key, name=name, description=description, light=light, cells=cells)


def _glow(
    hue: float,
    *,
    quiet: float,
    lit: float,
    lightness: float,
    rise: float = 0.28,
) -> Cell:
    """
    Make a cell that brightens: one hue, more saturated and lighter when it is lit.

    Parameters
    ----------
    hue : float
        The hue.
    quiet : float
        The saturation when quiet. Keyword-only.
    lit : float
        The saturation when lit. Keyword-only.
    lightness : float
        The lightness when quiet. Keyword-only.
    rise : float, default 0.28
        How much lighter it is when lit (a negative number makes it darker, for light wedges). Keyword-only.

    Returns
    -------
    tuple of tuple of float
        The cell's quiet and lit colours.

    Examples
    --------
    >>> _glow(220.0, quiet=0.3, lit=0.8, lightness=0.2, rise=0.3)
    ((220.0, 0.3, 0.2), (220.0, 0.8, 0.5))
    """
    return (hue, quiet, lightness), (hue, lit, lightness + rise)


def _presets() -> dict[str, Scheme]:
    """
    Make the presets, in the order the settings list them.

    Returns
    -------
    dict of str to Scheme
        Each preset by its key.

    Examples
    --------
    >>> list(_presets())[:3]
    ['cyan-indigo', 'midnight', 'deepening']
    """
    scriabin = [0, 24, 54, 122, 192, 202, 222, 274, 290, 212, 212, 352]
    safe = [205, 38, 164, 327, 56, 14]

    def cyan_indigo(place: int, *, inner: bool) -> Cell:
        sig = signature_of(place)
        amount = abs(sig) / 6
        return _glow(218 - 32 * amount if sig < 0 else 218 + 36 * amount, quiet=0.52, lit=0.82, lightness=0.18 if inner else 0.25)

    def deepening(place: int, *, inner: bool) -> Cell:
        lightness = (0.34 - 0.2 * abs(signature_of(place)) / 6) * (0.78 if inner else 1.0)
        return _glow(218, quiet=0.5, lit=0.8, lightness=lightness, rise=0.26)

    def sharps_flats(place: int, *, inner: bool) -> Cell:
        sig = signature_of(place)
        amount = abs(sig) / 6
        if sig == 0:
            hue, quiet = 214.0, 0.12
        elif sig > 0:
            hue, quiet = 42 - 36 * amount, 0.16 + 0.34 * amount
        else:
            hue, quiet = 188 + 52 * amount, 0.16 + 0.34 * amount
        return _glow(hue, quiet=quiet, lit=quiet + 0.4, lightness=0.18 if inner else 0.25)

    def scriabin_cell(place: int, *, inner: bool) -> Cell:
        steel = place in {9, 10}
        return _glow(
            scriabin[place],
            quiet=0.14 if steel else 0.4,
            lit=0.54 if steel else 0.82,
            lightness=0.17 if inner else 0.24,
        )

    def colour_blind(place: int, *, inner: bool) -> Cell:
        low = place < 6
        return _glow(
            safe[place % 6],
            quiet=0.5,
            lit=0.85,
            lightness=(0.15 if inner else 0.2) if low else (0.25 if inner else 0.31),
        )

    def glacier(_: int, *, inner: bool) -> Cell:
        return _glow(206 if inner else 218, quiet=0.46, lit=0.86, lightness=0.8 if inner else 0.87, rise=-0.34)

    def paper(place: int, *, inner: bool) -> Cell:
        return _glow(place * 30.0, quiet=0.4, lit=0.8, lightness=0.8 if inner else 0.86, rise=-0.32)

    schemes = [
        _scheme(
            "cyan-indigo",
            name="Cyan to indigo",
            description="Royal blue at C, shifting to cyan through the flat keys and to indigo through the sharp keys.",
            cell=cyan_indigo,
        ),
        _scheme(
            "midnight",
            name="Midnight",
            description="Deep navy wedges that glow the royal blue of the website's buttons when lit.",
            cell=lambda _, *, inner: _glow(222, quiet=0.3, lit=0.82, lightness=0.13 if inner else 0.19),
        ),
        _scheme(
            "deepening",
            name="Deepening",
            description="One blue that gets darker with each sharp or flat: C is the lightest cell and F♯ the darkest.",
            cell=deepening,
        ),
        _scheme(
            "two-blues",
            name="Two blues",
            description="Royal blue outside for the major keys, a lighter sky blue inside for the minor ones.",
            cell=lambda _, *, inner: _glow(
                196 if inner else 222,
                quiet=0.5 if inner else 0.56,
                lit=0.85 if inner else 0.86,
                lightness=0.2 if inner else 0.26,
            ),
        ),
        _scheme(
            "chequer",
            name="Chequer",
            description="Two blues that alternate round the circle, flipped on the inner ring, so neighbours never match.",
            cell=lambda place, *, inner: _glow(
                238 if (place + inner) % 2 else 206,
                quiet=0.5,
                lit=0.84,
                lightness=0.19 if inner else 0.26,
            ),
        ),
        _scheme(
            "glacier",
            name="Glacier",
            description="Pastel blue wedges with navy names, which deepen when lit. For a light window.",
            cell=glacier,
            light=True,
        ),
        _scheme(
            "spectrum",
            name="Spectrum",
            description="A full turn of the colour wheel, red at the top, so every key has its own hue.",
            cell=lambda place, *, inner: _glow(place * 30.0, quiet=0.34, lit=0.8, lightness=0.17 if inner else 0.24),
        ),
        _scheme(
            "ink",
            name="Ink",
            description="One blue for the whole circle. Nothing competes with the names; only the lit cells stand out.",
            cell=lambda place, *, inner: _glow(
                218 if inner else 212,
                quiet=0.16,
                lit=0.71,
                lightness=0.15 if inner else 0.21,
                rise=0.3,
            ),
        ),
        _scheme(
            "sharps-flats",
            name="Sharps and flats",
            description="Grey-blue at C, amber to red as sharps pile up, teal to indigo as flats do.",
            cell=sharps_flats,
        ),
        _scheme(
            "major-minor",
            name="Major and minor",
            description="Indigo outside for the major keys, teal inside for the minor ones.",
            cell=lambda _, *, inner: _glow(172 if inner else 236, quiet=0.34, lit=0.8, lightness=0.17 if inner else 0.24),
        ),
        _scheme(
            "scriabin",
            name="After Scriabin",
            description="The key colours the composer Scriabin heard: C red, G orange, D yellow, A green, F♯ bright blue.",
            cell=scriabin_cell,
        ),
        _scheme(
            "colour-blind",
            name="Colour-blind safe",
            description="Six hues from the Okabe and Ito palette, which stay apart for most kinds of colour blindness.",
            cell=colour_blind,
        ),
        _scheme(
            "ember",
            name="Ember",
            description="Dark charcoal wedges that glow amber when lit, like coals.",
            cell=lambda _, *, inner: ((20.0, 0.14, 0.14 if inner else 0.2), (40.0, 0.82, 0.42 if inner else 0.48)),
        ),
        _scheme(
            "paper",
            name="Paper",
            description="Pastel wedges of every hue with dark names, which deepen when lit.",
            cell=paper,
            light=True,
        ),
    ]
    return {scheme.key: scheme for scheme in schemes}


PRESETS = _presets()


def preset(key: str) -> Scheme:
    """
    Return a preset by its key.

    Parameters
    ----------
    key : str
        A key of `PRESETS`.

    Returns
    -------
    Scheme
        The preset.

    Raises
    ------
    KeyError
        If there is no such preset.

    Examples
    --------
    >>> preset("midnight").name
    'Midnight'
    >>> len(PRESETS)
    14
    """
    return PRESETS[key]


def record_of(
    key: str,
    *,
    name: str,
    mode: str,
    colours: list[str],
    light: bool = False,
) -> CustomRecord:
    """
    Make the record of a scheme of the user's own.

    Parameters
    ----------
    key : str
        Its key, such as "custom-1".
    name : str
        Its name. Keyword-only.
    mode : str
        How its colours are made: a key of `MODES`. Keyword-only.
    colours : list of str
        The colours the mode takes, as "#rrggbb". Keyword-only.
    light : bool, default False
        Whether the wedges are light. Keyword-only.

    Returns
    -------
    CustomRecord
        The record. Nothing is checked: `clean_record` does that.

    Examples
    --------
    >>> record_of("custom-1", name="Mine", mode="single", colours=["#2f6bd0"])["light"]
    False
    """
    return {"id": key, "name": name, "mode": mode, "colours": colours, "light": light}


def clean_record(raw: object) -> CustomRecord | None:
    """
    Check one saved scheme of the user's own, and tidy it.

    Parameters
    ----------
    raw : object
        What was read back from the saved data.

    Returns
    -------
    CustomRecord or None
        The record, with a name of at most 40 characters, or None if anything in it is missing or wrong: an unknown mode, a
        colour that is not "#rrggbb", or the wrong number of colours for the mode.

    Examples
    --------
    >>> good = record_of("custom-1", name="Mine", mode="rings", colours=["#2f6bd0", "#18a0c0"])
    >>> clean_record(good) == good
    True
    >>> few = record_of("custom-1", name="Mine", mode="rings", colours=["#2f6bd0"])
    >>> unknown = record_of("custom-1", name="Mine", mode="nope", colours=["#2f6bd0", "#18a0c0"])
    >>> clean_record(few) is None, clean_record(unknown) is None
    (True, True)
    >>> clean_record("not a record") is None
    True
    """
    if not isinstance(raw, dict):
        return None
    key, name, mode, colours, light = (raw.get(field) for field in ("id", "name", "mode", "colours", "light"))
    if not (isinstance(key, str) and isinstance(name, str) and isinstance(mode, str) and isinstance(light, bool)):
        return None
    if mode not in MODES or not isinstance(colours, list) or len(colours) != len(MODES[mode][1]):
        return None
    if not all(isinstance(item, str) and HEX.match(item) for item in colours):
        return None
    return {
        "id": key,
        "name": name.strip()[:40] or "My colours",
        "mode": mode,
        "colours": [item.lower() for item in colours],
        "light": light,
    }


def custom_scheme(record: CustomRecord) -> Scheme:
    """
    Make a scheme from one of the user's own records.

    The colours in a record are what a cell looks like when lit; the quiet cells are the same hue, calmer and darker (or, on a
    light wedges, paler).

    Parameters
    ----------
    record : CustomRecord
        A record that `clean_record` accepted.

    Returns
    -------
    Scheme
        The scheme, with the key and name of the record.

    Examples
    --------
    >>> scheme = custom_scheme(record_of("custom-1", name="Mine", mode="rings", colours=["#2f6bd0", "#18a0c0"]))
    >>> scheme.key, scheme.name, scheme.light
    ('custom-1', 'Mine', False)
    >>> scheme.cells["outer"][0][1][0] != scheme.cells["inner"][0][1][0]  # two rings, two hues
    True
    """
    picked = [hsl_of(item) for item in record["colours"]]
    light, mode = record["light"], record["mode"]

    def lit_of(place: int, *, inner: bool) -> Hsl:
        if mode == "single":
            return picked[0]
        if mode == "rings":
            return picked[1 if inner else 0]
        sig = signature_of(place)
        amount = abs(sig) / 6
        if mode == "signature":
            low, high = (picked[1], picked[0]) if sig < 0 else (picked[1], picked[2])
            return _between(low, end=high, amount=amount)
        if mode == "distance":
            return _between(picked[0], end=picked[1], amount=amount)
        return (picked[0][0] + 30.0 * place) % 360.0, picked[0][1], picked[0][2]

    def cell(place: int, *, inner: bool) -> Cell:
        hue, saturation, lightness = lit_of(place, inner=inner)
        if light:
            return (hue, saturation * 0.5, 0.8 if inner else 0.87), (hue, saturation, lightness)
        return (hue, saturation * 0.45, 0.17 if inner else 0.24), (hue, saturation, lightness)

    return _scheme(
        record["id"],
        name=record["name"],
        description="One of your own.",
        cell=cell,
        light=light,
    )


def _between(
    start: Hsl,
    *,
    end: Hsl,
    amount: float,
) -> Hsl:
    """
    Blend two colours, going the short way round the colour wheel.

    Parameters
    ----------
    start : tuple of float
        The colour at 0.
    end : tuple of float
        The colour at 1. Keyword-only.
    amount : float
        How far from `start` to `end`, from 0 to 1. Keyword-only.

    Returns
    -------
    tuple of float
        The blend.

    Examples
    --------
    >>> _between((350.0, 0.5, 0.4), end=(10.0, 0.5, 0.6), amount=0.5)
    (0.0, 0.5, 0.5)
    """
    hue = (start[0] + ((end[0] - start[0] + 180.0) % 360.0 - 180.0) * amount) % 360.0
    return hue, start[1] + (end[1] - start[1]) * amount, start[2] + (end[2] - start[2]) * amount


def dump_customs(records: list[CustomRecord]) -> str:
    """
    Write the user's own schemes as text to save.

    Parameters
    ----------
    records : list of CustomRecord
        The schemes.

    Returns
    -------
    str
        JSON.

    Examples
    --------
    >>> dump_customs([])
    '[]'
    """
    return json.dumps(records)


def load_customs(text: str) -> list[CustomRecord]:
    """
    Read the user's own schemes back, leaving out any that are not valid and any beyond the limit.

    Parameters
    ----------
    text : str
        What `dump_customs` wrote.

    Returns
    -------
    list of CustomRecord
        The valid schemes, each with its own key.

    Examples
    --------
    >>> load_customs("not json"), load_customs("[1, 2]")
    ([], [])
    >>> one = record_of("custom-1", name="A", mode="single", colours=["#2f6bd0"])
    >>> [r["id"] for r in load_customs(dump_customs([one, one]))]  # a repeated key is dropped
    ['custom-1']
    """
    try:
        found = json.loads(text)
    except ValueError:
        return []
    records: list[CustomRecord] = []
    for raw in found if isinstance(found, list) else []:
        record = clean_record(raw)
        if record is not None and record["id"] not in {r["id"] for r in records} | set(PRESETS) and len(records) < CUSTOM_LIMIT:
            records.append(record)
    return records


def resolve(
    key: str,
    *,
    customs: list[CustomRecord],
) -> Scheme:
    """
    Find a scheme by its key, among the presets and the user's own, falling back to the default.

    Parameters
    ----------
    key : str
        The saved choice.
    customs : list of CustomRecord
        The user's own schemes. Keyword-only.

    Returns
    -------
    Scheme
        The scheme, or the default one if the key is unknown (for instance after the scheme was deleted).

    Examples
    --------
    >>> resolve("midnight", customs=[]).name, resolve("gone", customs=[]).key
    ('Midnight', 'cyan-indigo')
    """
    if key in PRESETS:
        return PRESETS[key]
    for record in customs:
        if record["id"] == key:
            return custom_scheme(record)
    return PRESETS[DEFAULT_SCHEME]


def next_custom_key(customs: list[CustomRecord]) -> str:
    """
    Return a key that none of the user's schemes has.

    Parameters
    ----------
    customs : list of CustomRecord
        The user's own schemes.

    Returns
    -------
    str
        "custom-" and the smallest number that is free.

    Examples
    --------
    >>> taken = [record_of("custom-1", name="", mode="single", colours=[])]
    >>> next_custom_key([]), next_custom_key(taken)
    ('custom-1', 'custom-2')
    """
    used = {record["id"] for record in customs}
    number = 1
    while f"custom-{number}" in used:
        number += 1
    return f"custom-{number}"
