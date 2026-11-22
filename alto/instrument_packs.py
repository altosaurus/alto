"""Media and fingerboard geometry supplied by third-party instrument packs."""

from __future__ import annotations

import json
import re
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PySide6.QtCore import QSize
from PySide6.QtGui import QImageReader

from alto.audio import Instrument
from alto.instrument_info import InstrumentInfo
from alto.theory.pitch import Note

Point = tuple[float, float]


@dataclass(frozen=True)
class PackString:
    """One open pitch with its nut and bridge locations in the original image pixels."""

    pitch: str
    nut: Point
    bridge: Point

    def point(self, half_steps: int) -> Point:
        """
        Locate the pitch along the photographed string.

        Returns
        -------
        tuple of float
            Image coordinates measured from the top left.
        """
        fraction = 1 - 2 ** (-half_steps / 12)
        x, y = self.nut
        return x + (self.bridge[0] - x) * fraction, y + (self.bridge[1] - y) * fraction


@dataclass(frozen=True)
class AnswerAnimation:
    """An author-supplied animated overlay and its alignment on the instrument."""

    file: Path
    anchor: str


@dataclass(frozen=True)
class PackView:
    """Another picture of an instrument, such as its back, with its own pixel size."""

    name: str
    image: Path
    size: tuple[int, int]


SHARP_LETTERS = frozenset({0, 1, 3, 4, 5})  # C, D, F, G and A: the letters with a sharp key above them
KEYBOARD_LIMIT = 4  # keyboards on one instrument
STYLE_COLORS = ("white_edge", "black_edge", "case", "cap")  # the style fields that are one color
STYLE_GRADIENTS = ("white", "black")  # the style fields that are a color at the top of a key and one at the bottom
STYLE_NUMBERS = {  # the style fields that are numbers, with the range each may take
    "narrow": (0.5, 1.5),
    "gap": (0.0, 4.0),
    "round": (0.0, 10.0),
    "length": (2.0, 6.5),
}


@dataclass(frozen=True)
class PackKeyboard:
    """
    One keyboard of an instrument, drawn by Alto from the range of keys the plugin gives it.

    Attributes
    ----------
    name : str
        What the plugin calls this keyboard, such as "Lower manual".
    lowest : str
        The pitch of the lowest key, a natural such as "E1".
    highest : str
        The pitch of the highest key, a natural such as "F6".

    Examples
    --------
    >>> keys = PackKeyboard("Manual", "C4", "E4")
    >>> keys.naturals
    3
    >>> keys.has("C#4"), keys.has("E#4")
    (True, False)
    """

    name: str
    lowest: str
    highest: str

    @property
    def naturals(self) -> int:
        """
        Count the natural keys.

        Returns
        -------
        int
            The number of natural keys from the lowest to the highest, both included.

        Examples
        --------
        >>> PackKeyboard("M", "C4", "C5").naturals
        8
        """
        return _diatonic(Note.parse(self.highest)) - _diatonic(Note.parse(self.lowest)) + 1

    def has(self, name: str) -> bool:
        """
        Report whether a pitch is a key on this keyboard.

        Parameters
        ----------
        name : str
            A pitch such as "F#3".

        Returns
        -------
        bool
            True when the keyboard has that key, natural or sharp.

        Examples
        --------
        >>> board = PackKeyboard("M", "C4", "E4")
        >>> board.has("C#4"), board.has("E#4"), board.has("F4"), board.has("Db4")
        (True, False, False, False)
        """
        try:
            note = Note.parse(name)
        except (ValueError, KeyError):
            return False
        offset = _diatonic(note) - _diatonic(Note.parse(self.lowest))
        if note.accidental:
            return note.accidental == 1 and note.letter in SHARP_LETTERS and 0 <= offset < self.naturals - 1
        return 0 <= offset < self.naturals


@dataclass(frozen=True)
class PackKeyboardStyle:
    """
    How a plugin's keyboards look: the colors of the keys and case, and the proportions of the keys.

    Attributes
    ----------
    colors : tuple of tuple of str and str or tuple of str
        Each color field the plugin set, with its value as ``#rrggbb``. A natural or sharp key has two, for its top and bottom.
    numbers : tuple of tuple of str and float
        Each numeric field the plugin set, with its value.

    Examples
    --------
    >>> style = PackKeyboardStyle((("cap", "#eee3c8"),), (("length", 4.5),))
    >>> dict(style.colors), dict(style.numbers)
    ({'cap': '#eee3c8'}, {'length': 4.5})
    """

    colors: tuple[tuple[str, str | tuple[str, str]], ...] = ()
    numbers: tuple[tuple[str, float], ...] = ()


def read_keyboard_style(value: object, *, where: str) -> PackKeyboardStyle | None:
    """
    Validate the optional look of an instrument's keyboards.

    Parameters
    ----------
    value : object
        The instrument's ``keyboard_style`` entry, an object, or None.
    where : str
        The instrument's qualified key, used in messages. Keyword-only.

    Returns
    -------
    PackKeyboardStyle or None
        The style, or None to draw the keyboards in the learner's own keyboard style.

    Raises
    ------
    ValueError
        If a field is unknown, or a color or number is invalid.

    Examples
    --------
    >>> read_keyboard_style(None, where="pack.v.va") is None
    True
    >>> # noinspection PyUnresolvedReferences
    >>> read_keyboard_style({"cap": "#eee3c8", "white": ["#2a211c", "#120d0a"]}, where="pack.v.va").colors[1]
    ('white', ('#2a211c', '#120d0a'))
    """
    if value is None:
        return None
    allowed = (*STYLE_COLORS, *STYLE_GRADIENTS, *STYLE_NUMBERS)
    if not isinstance(value, dict) or not value or set(value) - set(allowed):
        raise ValueError(f"Give the keyboard_style of {where} as an object with any of: {', '.join(allowed)}.")

    colors: list[tuple[str, str | tuple[str, str]]] = []
    numbers = []
    for name, entry in value.items():
        if name in STYLE_COLORS:
            colors.append((name, _color(entry, where=where)))
        elif name in STYLE_GRADIENTS:
            if not isinstance(entry, list) or len(entry) != 2:
                raise ValueError(f"Give {name} in the keyboard_style of {where} as two colors: the top and the bottom of a key.")
            colors.append((name, (_color(entry[0], where=where), _color(entry[1], where=where))))
        else:
            low, high = STYLE_NUMBERS[name]
            if type(entry) not in (int, float) or not low <= entry <= high:
                raise ValueError(f"Set {name} in the keyboard_style of {where} to a number from {low} to {high}.")
            numbers.append((name, float(entry)))
    return PackKeyboardStyle(tuple(colors), tuple(numbers))


def _color(text: object, *, where: str) -> str:
    """
    Check one ``#rrggbb`` color.

    Parameters
    ----------
    text : object
        The color from the manifest.
    where : str
        The instrument's qualified key, used in messages. Keyword-only.

    Returns
    -------
    str
        The color.

    Raises
    ------
    ValueError
        If the text is not a color written as ``#`` and six hexadecimal digits.

    Examples
    --------
    >>> _color("#eee3c8", where="pack.v.va")
    '#eee3c8'
    """
    if not isinstance(text, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        raise ValueError(f"Write each keyboard_style color of {where} as #rrggbb, not {text!r}.")
    return text


def _diatonic(note: Note) -> int:
    """
    Count a note's letter name on a staff, so keys can be counted.

    Parameters
    ----------
    note : Note
        A pitch.

    Returns
    -------
    int
        Seven for each octave plus the position of the letter, with C as 0.

    Examples
    --------
    >>> _diatonic(Note.parse("D4")) - _diatonic(Note.parse("C4"))
    1
    """
    return note.octave * 7 + note.letter


@dataclass(frozen=True)
class PackInstrument:
    """A pack-qualified identity and the resources shared by its exercises."""

    key: str
    image: Path
    size: tuple[int, int]
    strings: tuple[PackString, ...]
    sound: Instrument | None
    correct_answer_animation: AnswerAnimation | None = None
    sound_info: InstrumentInfo | None = None
    positions: tuple[tuple[int, str], ...] = ()
    views: tuple[PackView, ...] = ()
    keyboards: tuple[PackKeyboard, ...] = ()
    keyboard_style: PackKeyboardStyle | None = None

    def keyboard(self, name: str) -> PackKeyboard | None:
        """
        Find one of the instrument's keyboards by name.

        Parameters
        ----------
        name : str
            The keyboard's name as the plugin wrote it.

        Returns
        -------
        PackKeyboard or None
            The keyboard, or None if the instrument has no keyboard with that name.

        Examples
        --------
        >>> keys = PackKeyboard("Manual", "C4", "E4")
        >>> board = PackInstrument("pack.x.y", Path("a.png"), (10, 20), (), None, keyboards=(keys,))
        >>> board.keyboard("Manual") is keys, board.keyboard("Pedals")
        (True, None)
        """
        return next((keys for keys in self.keyboards if keys.name == name), None)

    def picture(self, view: str = "") -> tuple[Path, tuple[int, int]] | None:
        """
        Find the picture for a view: the instrument's main picture for an empty name, otherwise the named extra picture.

        Parameters
        ----------
        view : str, default ""
            The view's name, or an empty string for the main picture.

        Returns
        -------
        tuple of Path and tuple of int, or None
            The image file and its size in pixels, or None if the instrument has no such view.

        Examples
        --------
        >>> back = PackView("back", Path("back.png"), (30, 40))
        >>> board = PackInstrument("pack.x.y", Path("front.png"), (10, 20), (), None, views=(back,))
        >>> board.picture(), board.picture("back"), board.picture("side")
        ((PosixPath('front.png'), (10, 20)), (PosixPath('back.png'), (30, 40)), None)
        """
        if not view:
            return self.image, self.size
        found = next((candidate for candidate in self.views if candidate.name == view), None)
        return None if found is None else (found.image, found.size)


INSTALLED: dict[str, PackInstrument] = {}


def identifier(value: object) -> str:
    """
    Validate one component of a pack-qualified id.

    Returns
    -------
    str
        The validated id.

    Raises
    ------
    ValueError
        If the id includes an unsupported character.
    """
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError("Use lowercase letters, digits and single hyphens for each id.")
    return value


def pitch(value: object) -> Note:
    """
    Read a pitch spelled with an octave.

    Returns
    -------
    Note
        The pitch used for playback and grading.

    Raises
    ------
    ValueError
        If the pitch has an unsupported spelling.
    """
    if not isinstance(value, str) or not re.fullmatch(r"[A-G][#b]?[0-8]", value):
        raise ValueError(f"Expected a note such as D4, F#4 or Bb3, got {value!r}.")
    return Note.parse(value)


class PackFiles:
    """Resolve only manifest-declared assets, from a folder or the root of a ZIP."""

    def __init__(self, manifest: Path, *, archive: ZipFile | None) -> None:
        """
        Keep folder assets in place and give ZIP assets private, generated filenames.

        Raises
        ------
        ValueError
            If the ZIP lacks a root manifest or repeats an entry name.
        """
        self.root = manifest.parent.resolve()
        self.archive = archive
        self.cache = tempfile.TemporaryDirectory(prefix="alto-pack-") if archive is not None else None
        self._files: dict[str, Path] = {}
        self._size = 0
        if archive is not None:
            names = archive.namelist()
            if len(names) != len(set(names)) or "pack.json" not in names:
                raise ValueError("Place pack.json at the root of the ZIP and give each entry a unique name.")

    def asset(self, name: object, *, extensions: tuple[str, ...]) -> Path:
        """
        Resolve a regular asset from this pack.

        Returns
        -------
        Path
            A local file usable by the image and audio readers.

        Raises
        ------
        ValueError
            If the path is missing, outside the pack, or has an unsupported type or size.
        """
        if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
            raise ValueError(f"Expected a relative file path in the pack, got {name!r}.")
        parts = name.split("/")
        if any(part in ("", ".", "..") for part in parts) or PureWindowsPath(name).drive:
            raise ValueError(f"{name!r} must be a relative file path inside the pack.")
        suffix = PurePosixPath(name).suffix.lower()
        if suffix not in extensions:
            raise ValueError(f"Use {' or '.join(extensions)} for {name!r}.")
        if name in self._files:
            return self._files[name]
        if self.archive is None:
            path = (self.root / name).resolve()
            if not path.is_relative_to(self.root) or not path.is_file():
                raise ValueError(f"Missing file inside the pack: {name}.")
            size = path.stat().st_size
        else:
            try:
                info = self.archive.getinfo(name)
            except KeyError as error:
                raise ValueError(f"Missing file in ZIP: {name}.") from error
            size = info.file_size
            assert self.cache is not None
            path = Path(self.cache.name) / f"{len(self._files)}{suffix}"
        self._size += size
        if size > 64 * 1024**2 or self._size > 256 * 1024**2:
            raise ValueError("Pack assets must fit within 64 MiB per file and 256 MiB in total.")
        if self.archive is not None:
            path.write_bytes(self.archive.read(name))
        self._files[name] = path
        return path

    def manifest(self) -> dict:
        """
        Read the API version and top-level pack object.

        Returns
        -------
        dict
            Version two manifest.

        Raises
        ------
        ValueError
            If the format is unsupported or the pack lacks a display name.
        """
        path = self.asset("pack.json", extensions=(".json",))
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict) or type(data.get("format")) is not int or data["format"] != 2:
            raise ValueError('Use "format": 2 and declare the pack’s instruments, media files and exercises.')
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Add a nonempty top-level "name" to pack.json, such as "Viola Instrument Pack".')
        data["name"] = name.strip()
        return data


def image_point(value: object, *, width: int, height: int) -> Point:
    """
    Validate a marker or string endpoint against the image dimensions.

    Returns
    -------
    tuple of float
        Coordinates in original image pixels.

    Raises
    ------
    ValueError
        If either coordinate is missing or outside the picture.
    """
    if not isinstance(value, list) or len(value) != 2 or not all(type(n) in (int, float) for n in value):
        raise ValueError("Give each point as [x, y] image pixels.")
    x, y = value
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"Point {value} is outside the {width} × {height} image.")
    return x, y


SOUND_INFO_FIELDS = ("summary", "source", "source_url", "performer", "recorded", "includes", "terms", "note")
SOUND_INFO_LIMIT = 800  # characters in one field


def read_sound_info(value: object, *, where: str, pack_name: str) -> InstrumentInfo | None:
    """
    Validate the optional facts a pack gives about where its recordings came from.

    Parameters
    ----------
    value : object
        The instrument's ``sound_info`` entry, or None when it has none.
    where : str
        The instrument's qualified key, used in error messages. Keyword-only.
    pack_name : str
        The pack's display name, shown as the source when the entry gives none. Keyword-only.

    Returns
    -------
    InstrumentInfo or None
        The facts for the Sound settings, or None when the instrument declared none.

    Raises
    ------
    ValueError
        If an entry is not text, is too long, contains markup, or if the link is not an https address.

    Examples
    --------
    >>> info = read_sound_info({"summary": "A viola."}, where="pack.v.va", pack_name="Viola")
    >>> info.source if info else None
    'Viola'
    >>> read_sound_info(None, where="pack.v.va", pack_name="Viola") is None
    True
    """
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) - set(SOUND_INFO_FIELDS):
        raise ValueError(f"Give {where} a sound_info object with only these fields: {', '.join(SOUND_INFO_FIELDS)}.")
    text = {}
    for field, entry in value.items():
        if not isinstance(entry, str) or len(entry) > SOUND_INFO_LIMIT or any(c in entry for c in "<>"):
            raise ValueError(f"Make sound_info {field} for {where} plain text of at most {SOUND_INFO_LIMIT} characters.")
        text[field] = entry.strip()
    url = text.get("source_url", "")
    if url and (not url.startswith("https://") or any(c in url for c in " \t\n\"'")):
        raise ValueError(f"Make sound_info source_url for {where} an https address.")
    return InstrumentInfo(
        text.get("summary") or "Recordings supplied by an installed instrument pack.",
        source=text.get("source") or pack_name,
        source_url=url,
        performer=text.get("performer", ""),
        recorded=text.get("recorded", ""),
        includes=text.get("includes", ""),
        terms=text.get("terms", ""),
        note=text.get("note", ""),
    )


def plain_text(value: object, *, limit: int) -> bool:
    """
    Check that a manifest entry is nonblank plain text of a reasonable length.

    Parameters
    ----------
    value : object
        The manifest entry.
    limit : int
        The most characters allowed. Keyword-only.

    Returns
    -------
    bool
        True for a nonblank string with no markup characters and at most ``limit`` characters.

    Examples
    --------
    >>> plain_text("Name the note.", limit=40), plain_text("<b>Name</b>", limit=40), plain_text(None, limit=40)
    (True, False, False)
    """
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit and "<" not in value and ">" not in value


def read_text(value: object, *, limit: int, what: str, where: str) -> str:
    """
    Check one piece of plain text and return it trimmed.

    Parameters
    ----------
    value : object
        The manifest entry.
    limit : int
        The most characters allowed. Keyword-only.
    what : str
        What the entry is, for the message. Keyword-only.
    where : str
        Which lesson or step it belongs to, for the message. Keyword-only.

    Returns
    -------
    str
        The entry without surrounding space.

    Raises
    ------
    ValueError
        If it is not nonblank plain text within the limit.

    Examples
    --------
    >>> read_text("  Hello ", limit=10, what="title", where="lesson demo")
    'Hello'
    """
    if not plain_text(value, limit=limit):
        raise ValueError(f"Give {where} a plain-text {what} of at most {limit} characters.")
    assert isinstance(value, str)
    return value.strip()


def read_focus(value: object, *, width: int, height: int) -> tuple[float, float, float, float]:
    """
    Validate a picture question's region to show.

    Parameters
    ----------
    value : object
        The manifest entry: a list of left, top, width and height in picture pixels.
    width : int
        The picture's width in pixels. Keyword-only.
    height : int
        The picture's height in pixels. Keyword-only.

    Returns
    -------
    tuple of float
        Left, top, width and height.

    Raises
    ------
    ValueError
        If the entry is not four numbers describing a region of at least 40 pixels inside the picture.

    Examples
    --------
    >>> read_focus([0, 10, 200, 100], width=400, height=300)
    (0.0, 10.0, 200.0, 100.0)
    """
    if not isinstance(value, list) or len(value) != 4 or any(type(v) not in (int, float) for v in value):
        raise ValueError("Give focus as four numbers: left, top, width and height.")
    left, top, span_x, span_y = (float(v) for v in value)
    if span_x < 40 or span_y < 40 or left < 0 or top < 0 or left + span_x > width or top + span_y > height:
        raise ValueError("Keep focus at least 40 pixels wide and tall, and inside the picture.")
    return left, top, span_x, span_y


def read_marker_size(value: object) -> float:
    """
    Validate a picture's marker size.

    Parameters
    ----------
    value : object
        The manifest entry: a diameter in picture pixels, or 0 for the default size.

    Returns
    -------
    float
        The diameter.

    Raises
    ------
    ValueError
        If the entry is not 0 or a number from 6 to 200.

    Examples
    --------
    >>> read_marker_size(0), read_marker_size(24)
    (0.0, 24.0)
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not (value == 0 or 6 <= value <= 200):
        raise ValueError("Give marker_size as a diameter from 6 to 200 picture pixels, or leave it out.")
    return float(value)


VIEW_LIMIT = 4  # extra pictures of one instrument


ICON_TAGS = {"g", "path", "circle", "ellipse", "rect", "line", "polyline", "polygon"}
ICON_ATTRIBUTES = {
    "d", "cx", "cy", "r", "rx", "ry", "x", "y", "width", "height", "x1", "y1", "x2", "y2", "points", "transform",
    "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "fill-rule", "clip-rule", "opacity",
}  # fmt: skip
ICON_LIMIT = 100_000  # bytes in an icon file


def read_icon(files: PackFiles, *, name: object) -> str:
    """
    Read a plugin's tile icon: a plain SVG of simple shapes, redrawn in the theme's ink.

    Parameters
    ----------
    files : PackFiles
        The pack's files.
    name : object
        The manifest entry: a pack-relative path to an SVG file with the viewBox ``0 0 24 24``. Keyword-only.

    Returns
    -------
    str
        The shapes, with COLOR wherever the theme's ink goes, ready for `alto.ui.icons.svg_icon`.

    Raises
    ------
    ValueError
        If the file is missing, too large, not an SVG of the right box, or uses anything but simple shapes (no scripts, images,
        styles, or links).

    Examples
    --------
    The viola's icon is its own silhouette traced from the museum photograph.
    """
    path = files.asset(name, extensions=(".svg",))
    if path.stat().st_size > ICON_LIMIT:
        raise ValueError(f"Keep the icon {name} under {ICON_LIMIT // 1000} KB.")
    try:
        text = path.read_text(encoding="utf-8")
        if "<!" in text.replace("<!--", ""):
            raise ValueError(f"The icon {name} may not declare entities or document types.")
        root = ET.fromstring(text)
    except (ET.ParseError, UnicodeDecodeError) as error:
        raise ValueError(f"Cannot read {name} as an SVG file.") from error

    def local(tag: str) -> str:
        """
        Drop the XML namespace from a tag.

        Parameters
        ----------
        tag : str
            An element tag such as ``{http://www.w3.org/2000/svg}path``.

        Returns
        -------
        str
            The tag without the namespace.

        Examples
        --------
        >>> local("{http://www.w3.org/2000/svg}path")
        'path'
        """
        return tag.rsplit("}", 1)[-1]

    if local(root.tag) != "svg" or root.get("viewBox", "").split() != ["0", "0", "24", "24"]:
        raise ValueError(f'Give the icon {name} the root <svg viewBox="0 0 24 24">.')

    def draw(element: ET.Element) -> str:
        """
        Write a simple shape and what is inside it with every color replaced by the theme's ink.

        Parameters
        ----------
        element : ET.Element
            A shape or group from the icon.

        Returns
        -------
        str
            SVG markup.

        Raises
        ------
        ValueError
            If it is not one of the simple shapes, or has an attribute that is not about its geometry or its paint.
        """
        tag = local(element.tag)
        if tag not in ICON_TAGS or set(element.attrib) - ICON_ATTRIBUTES:
            raise ValueError(
                f"The icon {name} may use only simple shapes with geometry and paint: {', '.join(sorted(ICON_TAGS))}.",
            )
        attributes = dict(element.attrib)
        for paint in ("fill", "stroke"):
            if paint in attributes and attributes[paint] != "none":
                attributes[paint] = "COLOR"
        if tag != "g" and "fill" not in attributes and "stroke" not in attributes:
            attributes["fill"] = "COLOR"
        inner = "".join(draw(child) for child in element)
        text = "".join(f' {key}="{value}"' for key, value in attributes.items() if re.fullmatch(r"[A-Za-z0-9 .,#%+\-()]*", value))
        return f"<{tag}{text}>{inner}</{tag}>"

    shapes = "".join(draw(child) for child in root)
    if not shapes:
        raise ValueError(f"The icon {name} has no shapes.")
    return shapes


def read_picture_file(files: PackFiles, *, name: object) -> tuple[Path, tuple[int, int]]:
    """
    Find and check a picture in the pack.

    Parameters
    ----------
    files : PackFiles
        The pack's files.
    name : object
        The manifest entry: a pack-relative path to a PNG, WebP, or JPEG picture. Keyword-only.

    Returns
    -------
    tuple of Path and tuple of int
        The picture file and its width and height in pixels.

    Raises
    ------
    ValueError
        If the picture is missing, unreadable, or larger than 16 megapixels.
    """
    image = files.asset(name, extensions=(".png", ".webp", ".jpg", ".jpeg"))
    assert isinstance(name, str)  # asset() accepted it, so it is the pack-relative path
    reader = QImageReader(str(image))
    size = reader.size()
    if not size.isValid() or size.width() * size.height() > 16_000_000 or reader.read().isNull():
        raise ValueError(f"Cannot read {name} as an image of at most 16 megapixels.")
    return image, (size.width(), size.height())


def read_views(value: object, *, files: PackFiles, where: str) -> tuple[PackView, ...]:
    """
    Validate the optional extra pictures of an instrument, such as a view of its back.

    Parameters
    ----------
    value : object
        The instrument's ``views`` entry, an object from a view name to a pack-relative picture path, or None.
    files : PackFiles
        The pack's files. Keyword-only.
    where : str
        The instrument's qualified key, used in error messages. Keyword-only.

    Returns
    -------
    tuple of PackView
        The views, in the order the manifest lists them. Empty when none were declared.

    Raises
    ------
    ValueError
        If the entry is not a short object of valid names and readable pictures.

    Examples
    --------
    >>> # noinspection PyTypeChecker
    >>> read_views(None, files=None, where="pack.v.va")
    ()
    """
    if value is None:
        return ()
    if not isinstance(value, dict) or not value or len(value) > VIEW_LIMIT:
        raise ValueError(f"Give {where} up to {VIEW_LIMIT} views, as an object from each view's name to its picture.")
    views = []
    for name, path in value.items():
        identifier(name)
        image, size = read_picture_file(files, name=path)
        views.append(PackView(name, image, size))
    return tuple(views)


def read_keyboards(value: object, *, where: str) -> tuple[PackKeyboard, ...]:
    """
    Validate the optional keyboards of an instrument, which Alto draws from their ranges.

    Parameters
    ----------
    value : object
        The instrument's ``keyboards`` entry, a list of objects, or None.
    where : str
        The instrument's qualified key, used in messages. Keyword-only.

    Returns
    -------
    tuple of PackKeyboard
        The keyboards in the order the manifest lists them, which is the order Alto draws them from top to bottom. Empty
        when none were declared.

    Raises
    ------
    ValueError
        If the entry is not a short list of keyboards with distinct names and natural end keys.

    Examples
    --------
    >>> read_keyboards(None, where="pack.v.va")
    ()
    >>> read_keyboards([{"name": "Manual", "lowest": "C4", "highest": "E4"}], where="pack.v.va")[0].naturals
    3
    """
    if value is None:
        return ()
    if not isinstance(value, list) or not value or len(value) > KEYBOARD_LIMIT:
        raise ValueError(f"Give {where} up to {KEYBOARD_LIMIT} keyboards, as a list of objects.")
    keyboards = []
    for row in value:
        if not isinstance(row, dict) or set(row) - {"name", "lowest", "highest"}:
            raise ValueError(f"Give each keyboard of {where} as an object with only a name, a lowest key, and a highest key.")
        name = read_text(row.get("name"), limit=40, what="name", where=f"each keyboard of {where}")
        if any(existing.name == name for existing in keyboards):
            raise ValueError(f"Give each keyboard of {where} its own name. Check {name!r}.")
        ends = []
        for field in ("lowest", "highest"):
            end = pitch(row.get(field))
            if end.accidental:
                raise ValueError(f"Set {field} for {name!r} to a natural key such as E1.")
            ends.append(end)
        if _diatonic(ends[0]) >= _diatonic(ends[1]):
            raise ValueError(f"Put the lowest key of {name!r} below its highest key.")
        keyboards.append(PackKeyboard(name, row["lowest"], row["highest"]))
    return tuple(keyboards)


POSITION_LIMIT = 12  # named positions on one instrument
POSITION_STEPS = 36  # the highest half step a position may sit at


def read_positions(value: object, *, where: str) -> tuple[tuple[int, str], ...]:
    """
    Validate the optional named positions along a string, which label the ruler beside the fingerboard.

    Parameters
    ----------
    value : object
        The instrument's ``positions`` entry, a list of ``{"name": ..., "half_steps": ...}``, or None when it has none.
    where : str
        The instrument's qualified key, used in error messages. Keyword-only.

    Returns
    -------
    tuple of (int, str)
        Each position's half steps above the open string and its name, in ascending order. Empty when none were declared.

    Raises
    ------
    ValueError
        If the entry is not a short list of named, ascending positions with plain-text names.

    Examples
    --------
    >>> read_positions([{"name": "1st", "half_steps": 2}, {"name": "2nd", "half_steps": 3}], where="pack.v.va")
    ((2, '1st'), (3, '2nd'))
    >>> read_positions(None, where="pack.v.va")
    ()
    """
    if value is None:
        return ()
    if not isinstance(value, list) or len(value) > POSITION_LIMIT:
        raise ValueError(f"Give {where} a list of at most {POSITION_LIMIT} positions, each with a name and half_steps.")
    found: list[tuple[int, str]] = []
    for row in value:
        if not isinstance(row, dict) or set(row) != {"name", "half_steps"}:
            raise ValueError(f"Give each position of {where} exactly a name and half_steps.")
        name, steps = row["name"], row["half_steps"]
        if not isinstance(name, str) or not name.strip() or len(name) > 12 or any(c in name for c in "<>"):
            raise ValueError(f"Make each position name for {where} plain text of at most 12 characters.")
        if type(steps) is not int or not 1 <= steps <= POSITION_STEPS:
            raise ValueError(f"Give each position of {where} whole half_steps from 1 to {POSITION_STEPS}.")
        if found and steps <= found[-1][0]:
            raise ValueError(f"List the positions of {where} in ascending order of half_steps, with no repeats.")
        found.append((steps, name.strip()))
    return tuple(found)


def read_instrument(row: object, *, pack: str, files: PackFiles, pack_name: str = "") -> PackInstrument:
    """
    Validate one declared instrument against its own artwork and recordings.

    Returns
    -------
    PackInstrument
        The calibrated instrument available to exercises in this pack.

    Raises
    ------
    ValueError
        If a required field, string, image, or recording is invalid.
    """
    if not isinstance(row, dict):
        raise ValueError("Each instrument must be an object.")
    key = f"pack.{pack}.{identifier(row.get('id'))}"
    label = row.get("name")
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"Give {key} an instrument name.")
    image, picture_size = read_picture_file(files, name=row.get("image"))
    size = QSize(*picture_size)
    strings = row.get("strings", [])
    if not isinstance(strings, list) or len(strings) == 1:
        raise ValueError(f"List at least two strings for {key}, from lowest pitch to highest.")
    calibrated = []
    midis = []
    for string in strings:
        if not isinstance(string, dict):
            raise ValueError("Each string needs open, nut and bridge.")
        midis.append(pitch(string.get("open")).midi)
        nut, bridge = (image_point(string.get(field), width=size.width(), height=size.height()) for field in ("nut", "bridge"))
        if nut == bridge:
            raise ValueError("The nut and bridge must be different points on each string.")
        calibrated.append(PackString(string["open"], nut, bridge))
    if midis != sorted(set(midis)):
        raise ValueError("List distinct strings from lowest to highest.")
    if len({s.nut for s in calibrated}) != len(strings) or len({s.bridge for s in calibrated}) != len(strings):
        raise ValueError("Give each string its own nut and bridge points.")
    gain = row.get("gain", 1)
    if type(gain) not in (float, int) or not 0 < gain <= 1:
        raise ValueError("Use an instrument gain greater than zero and at most one.")
    samples = row.get("samples", {})
    if not isinstance(samples, dict):
        raise ValueError("Map each recorded pitch to a WAV file under samples.")
    recordings = {}
    for name, filename in samples.items():
        midi = pitch(name).midi
        if midi in recordings:
            raise ValueError(f"Duplicate recorded pitch {name}.")
        sample = files.asset(filename, extensions=(".wav",))
        try:
            with wave.open(str(sample), "rb") as recording:
                if recording.getnchannels() != 1 or recording.getsampwidth() != 2 or recording.getnframes() < 1:
                    raise ValueError(f"{filename} must contain mono 16-bit PCM audio.")
                recording.setpos(recording.getnframes() - 1)
                if len(recording.readframes(1)) != 2:
                    raise ValueError(f"Incomplete WAV recording: {filename}.")
        except (wave.Error, EOFError) as error:
            raise ValueError(f"Invalid WAV recording: {filename}.") from error
        recordings[midi] = sample
    sustained = row.get("sustained", False)
    if not isinstance(sustained, bool):
        raise ValueError(f"Set sustained for {key} to true or false.")
    kind = row.get("kind", "")
    if "kind" in row and (not isinstance(kind, str) or not kind.strip() or not plain_text(kind, limit=30)):
        raise ValueError(f"Give the kind of {key} as plain text of at most 30 characters, such as harpsichord.")
    sound = (
        Instrument(
            key,
            label=label,
            folder="",
            gain=gain,
            sustained=sustained,
            samples=tuple(recordings.items()),
            pack_name=pack_name or pack,
            kind=kind.strip(),
        )
        if recordings
        else None
    )
    animation = None
    if "correct_answer_animation" in row:
        spec = row["correct_answer_animation"]
        if not isinstance(spec, dict):
            raise ValueError("Give correct_answer_animation an object with a GIF file and an optional anchor.")
        anchor = spec.get("anchor", "image")
        if anchor not in ("image", "string"):
            raise ValueError('Set the correct_answer_animation anchor to "image" or "string".')
        if anchor == "string" and not calibrated:
            raise ValueError('Declare strings to use a "string" animation anchor.')
        file = files.asset(spec.get("file"), extensions=(".gif",))
        animation_reader = QImageReader(str(file), b"gif")
        canvas = animation_reader.size()
        if (
            not canvas.isValid()
            or canvas.width() * canvas.height() > 16_000_000
            or animation_reader.imageCount() < 2
            or animation_reader.read().isNull()
        ):
            raise ValueError(f"Supply an animated GIF with at least two frames and at most 16 megapixels: {spec.get('file')}.")
        animation = AnswerAnimation(file, anchor)
    info = read_sound_info(row.get("sound_info"), where=key, pack_name=pack_name or pack)
    positions = read_positions(row.get("positions"), where=key)
    views = read_views(row.get("views"), files=files, where=key)
    keyboards = read_keyboards(row.get("keyboards"), where=key)
    keyboard_style = read_keyboard_style(row.get("keyboard_style"), where=key)
    if keyboard_style is not None and not keyboards:
        raise ValueError(f"Declare keyboards on {key} to give it a keyboard_style.")
    return PackInstrument(
        key,
        image,
        (size.width(), size.height()),
        tuple(calibrated),
        sound,
        animation,
        info,
        positions,
        views,
        keyboards,
        keyboard_style,
    )
