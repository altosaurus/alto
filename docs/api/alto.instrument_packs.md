---
title: alto.instrument_packs
parent: api
package: alto
permalink: /api/alto.instrument_packs/
---
{% raw %}
Media and fingerboard geometry supplied by third-party instrument packs.

## PackString

```python
PackString(
    pitch: str,
    nut: Point,
    bridge: Point,
)
```

One open pitch with its nut and bridge locations in the original
image pixels.

### PackString.point

```python
def point(half_steps: int) -> Point
```

Locate the pitch along the photographed string.

**Returns**

- *tuple of float*: Image coordinates measured from the top left.

## AnswerAnimation

```python
AnswerAnimation(
    file: Path,
    anchor: str,
)
```

An author-supplied animated overlay and its alignment on the
instrument.

## PackView

```python
PackView(
    name: str,
    image: Path,
    size: tuple[int, int],
)
```

Another picture of an instrument, such as its back, with its own
pixel size.

## PackKeyboard

```python
PackKeyboard(
    name: str,
    lowest: str,
    highest: str,
)
```

One keyboard of an instrument, drawn by Alto from the range of keys
the plugin gives it.

**Attributes**

- `name` (*str*): What the plugin calls this keyboard, such as "Lower manual".
- `lowest` (*str*): The pitch of the lowest key, a natural such as "E1".
- `highest` (*str*): The pitch of the highest key, a natural such as "F6".

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keys = PackKeyboard("Manual", "C4", "E4")
>>> keys.naturals
3
>>> keys.has("C#4"), keys.has("E#4")
(True, False)
```

### PackKeyboard.naturals

```python
@property
def naturals() -> int
```

Count the natural keys.

**Returns**

- *int*: The number of natural keys from the lowest to the highest, both included.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PackKeyboard("M", "C4", "C5").naturals
8
```

### PackKeyboard.has

```python
def has(name: str) -> bool
```

Report whether a pitch is a key on this keyboard.

**Parameters**

- `name` (*str*): A pitch such as "F#3".

**Returns**

- *bool*: True when the keyboard has that key, natural or sharp.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> board = PackKeyboard("M", "C4", "E4")
>>> (
...     board.has("C#4"),
...     board.has("E#4"),
...     board.has("F4"),
...     board.has("Db4"),
... )
(True, False, False, False)
```

## PackKeyboardStyle

```python
PackKeyboardStyle(
    colors: tuple[tuple[str, str | tuple[str, str]], ...] = (),
    numbers: tuple[tuple[str, float], ...] = (),
)
```

How a plugin's keyboards look: the colors of the keys and case, and
the proportions of the keys.

**Attributes**

- `colors` (*tuple of tuple of str and str or tuple of str*): Each color field the plugin set, with its value as ``#rrggbb``. A natural or sharp key has two, for its top and bottom.
- `numbers` (*tuple of tuple of str and float*): Each numeric field the plugin set, with its value.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> style = PackKeyboardStyle(
...     (("cap", "#eee3c8"),),
...     (("length", 4.5),),
... )
>>> dict(style.colors), dict(style.numbers)
({'cap': '#eee3c8'}, {'length': 4.5})
```

## read_keyboard_style

```python
def read_keyboard_style(
    value: object,
    *,
    where: str,
) -> PackKeyboardStyle | None
```

Validate the optional look of an instrument's keyboards.

**Parameters**

- `value` (*object*): The instrument's ``keyboard_style`` entry, an object, or None.
- `where` (*str*): The instrument's qualified key, used in messages. Keyword-only.

**Returns**

- *PackKeyboardStyle or None*: The style, or None to draw the keyboards in the learner's own keyboard style.

**Raises**

- *ValueError*: If a field is unknown, or a color or number is invalid.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_keyboard_style(
...     None, where="pack.v.va"
... ) is None
True
>>> # noinspection PyUnresolvedReferences
>>> read_keyboard_style(
...     {
...         "cap": "#eee3c8",
...         "white": ["#2a211c", "#120d0a"],
...     },
...     where="pack.v.va",
... ).colors[1]
('white', ('#2a211c', '#120d0a'))
```

## PackInstrument

```python
PackInstrument(
    key: str,
    image: Path,
    size: tuple[int, int],
    strings: tuple[PackString, ...],
    sound: Instrument | None,
    correct_answer_animation: AnswerAnimation | None = None,
    sound_info: InstrumentInfo | None = None,
    positions: tuple[tuple[int, str], ...] = (),
    views: tuple[PackView, ...] = (),
    keyboards: tuple[PackKeyboard, ...] = (),
    keyboard_style: PackKeyboardStyle | None = None,
)
```

A pack-qualified identity and the resources shared by its exercises.

### PackInstrument.keyboard

```python
def keyboard(name: str) -> PackKeyboard | None
```

Find one of the instrument's keyboards by name.

**Parameters**

- `name` (*str*): The keyboard's name as the plugin wrote it.

**Returns**

- *PackKeyboard or None*: The keyboard, or None if the instrument has no keyboard with that name.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keys = PackKeyboard("Manual", "C4", "E4")
>>> board = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (10, 20),
...     (),
...     None,
...     keyboards=(keys,),
... )
>>> (
...     board.keyboard("Manual") is keys,
...     board.keyboard("Pedals"),
... )
(True, None)
```

### PackInstrument.picture

```python
def picture(view: str = '') -> tuple[Path, tuple[int, int]] | None
```

Find the picture for a view: the instrument's main picture for
an empty name, otherwise the named extra picture.

**Parameters**

- `view` (*str, default ""*): The view's name, or an empty string for the main picture.

**Returns**

- *tuple of Path and tuple of int, or None*: The image file and its size in pixels, or None if the instrument has no such view.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> back = PackView(
...     "back", Path("back.png"), (30, 40)
... )
>>> board = PackInstrument(
...     "pack.x.y",
...     Path("front.png"),
...     (10, 20),
...     (),
...     None,
...     views=(back,),
... )
>>> (
...     board.picture(),
...     board.picture("back"),
...     board.picture("side"),
... )
((PosixPath('front.png'), (10, 20)), (PosixPath('back.png'),
(30, 40)), None)
```

## identifier

```python
def identifier(value: object) -> str
```

Validate one component of a pack-qualified id.

**Returns**

- *str*: The validated id.

**Raises**

- *ValueError*: If the id includes an unsupported character.

## pitch

```python
def pitch(value: object) -> Note
```

Read a pitch spelled with an octave.

**Returns**

- *Note*: The pitch used for playback and grading.

**Raises**

- *ValueError*: If the pitch has an unsupported spelling.

## PackFiles

```python
PackFiles(
    manifest: Path,
    *,
    archive: ZipFile | None,
)
```

Resolve only manifest-declared assets, from a folder or the root of
a ZIP.

**Constructor**

Keep folder assets in place and give ZIP assets private,
generated filenames.

**Raises**

- *ValueError*: If the ZIP lacks a root manifest or repeats an entry name.

### PackFiles.asset

```python
def asset(
    name: object,
    *,
    extensions: tuple[str, ...],
) -> Path
```

Resolve a regular asset from this pack.

**Returns**

- *Path*: A local file usable by the image and audio readers.

**Raises**

- *ValueError*: If the path is missing, outside the pack, or has an unsupported type or size.

### PackFiles.manifest

```python
def manifest() -> dict
```

Read the API version and top-level pack object.

**Returns**

- *dict*: Version two manifest.

**Raises**

- *ValueError*: If the format is unsupported or the pack lacks a display name.

## image_point

```python
def image_point(
    value: object,
    *,
    width: int,
    height: int,
) -> Point
```

Validate a marker or string endpoint against the image dimensions.

**Returns**

- *tuple of float*: Coordinates in original image pixels.

**Raises**

- *ValueError*: If either coordinate is missing or outside the picture.

## read_sound_info

```python
def read_sound_info(
    value: object,
    *,
    where: str,
    pack_name: str,
) -> InstrumentInfo | None
```

Validate the optional facts a pack gives about where its recordings
came from.

**Parameters**

- `value` (*object*): The instrument's ``sound_info`` entry, or None when it has none.
- `where` (*str*): The instrument's qualified key, used in error messages. Keyword-only.
- `pack_name` (*str*): The pack's display name, shown as the source when the entry gives none. Keyword-only.

**Returns**

- *InstrumentInfo or None*: The facts for the Sound settings, or None when the instrument declared none.

**Raises**

- *ValueError*: If an entry is not text, is too long, contains markup, or if the link is not an https address.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> info = read_sound_info(
...     {"summary": "A viola."},
...     where="pack.v.va",
...     pack_name="Viola",
... )
>>> info.source if info else None
'Viola'
>>> read_sound_info(
...     None,
...     where="pack.v.va",
...     pack_name="Viola",
... ) is None
True
```

## plain_text

```python
def plain_text(
    value: object,
    *,
    limit: int,
) -> bool
```

Check that a manifest entry is nonblank plain text of a reasonable
length.

**Parameters**

- `value` (*object*): The manifest entry.
- `limit` (*int*): The most characters allowed. Keyword-only.

**Returns**

- *bool*: True for a nonblank string with no markup characters and at most ``limit`` characters.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     plain_text("Name the note.", limit=40),
...     plain_text("<b>Name</b>", limit=40),
...     plain_text(None, limit=40),
... )
(True, False, False)
```

## read_text

```python
def read_text(
    value: object,
    *,
    limit: int,
    what: str,
    where: str,
) -> str
```

Check one piece of plain text and return it trimmed.

**Parameters**

- `value` (*object*): The manifest entry.
- `limit` (*int*): The most characters allowed. Keyword-only.
- `what` (*str*): What the entry is, for the message. Keyword-only.
- `where` (*str*): Which lesson or step it belongs to, for the message. Keyword-only.

**Returns**

- *str*: The entry without surrounding space.

**Raises**

- *ValueError*: If it is not nonblank plain text within the limit.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_text(
...     "  Hello ",
...     limit=10,
...     what="title",
...     where="lesson demo",
... )
'Hello'
```

## read_focus

```python
def read_focus(
    value: object,
    *,
    width: int,
    height: int,
) -> tuple[float, float, float, float]
```

Validate a picture question's region to show.

**Parameters**

- `value` (*object*): The manifest entry: a list of left, top, width and height in picture pixels.
- `width` (*int*): The picture's width in pixels. Keyword-only.
- `height` (*int*): The picture's height in pixels. Keyword-only.

**Returns**

- *tuple of float*: Left, top, width and height.

**Raises**

- *ValueError*: If the entry is not four numbers describing a region of at least 40 pixels inside the picture.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_focus(
...     [0, 10, 200, 100], width=400, height=300
... )
(0.0, 10.0, 200.0, 100.0)
```

## read_marker_size

```python
def read_marker_size(value: object) -> float
```

Validate a picture's marker size.

**Parameters**

- `value` (*object*): The manifest entry: a diameter in picture pixels, or 0 for the default size.

**Returns**

- *float*: The diameter.

**Raises**

- *ValueError*: If the entry is not 0 or a number from 6 to 200.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_marker_size(0), read_marker_size(24)
(0.0, 24.0)
```

## read_icon

```python
def read_icon(
    files: PackFiles,
    *,
    name: object,
) -> str
```

Read a plugin's tile icon: a plain SVG of simple shapes, redrawn in
the theme's ink.

**Parameters**

- `files` (*PackFiles*): The pack's files.
- `name` (*object*): The manifest entry: a pack-relative path to an SVG file with the viewBox ``0 0 24 24``. Keyword-only.

**Returns**

- *str*: The shapes, with COLOR wherever the theme's ink goes, ready for `alto.ui.icons.svg_icon`.

**Raises**

- *ValueError*: If the file is missing, too large, not an SVG of the right box, or uses anything but simple shapes (no scripts, images, styles, or links).

**Examples**

```text
The viola's icon is its own silhouette traced from the museum
photograph.
```

## read_picture_file

```python
def read_picture_file(
    files: PackFiles,
    *,
    name: object,
) -> tuple[Path, tuple[int, int]]
```

Find and check a picture in the pack.

**Parameters**

- `files` (*PackFiles*): The pack's files.
- `name` (*object*): The manifest entry: a pack-relative path to a PNG, WebP, or JPEG picture. Keyword-only.

**Returns**

- *tuple of Path and tuple of int*: The picture file and its width and height in pixels.

**Raises**

- *ValueError*: If the picture is missing, unreadable, or larger than 16 megapixels.

## read_views

```python
def read_views(
    value: object,
    *,
    files: PackFiles,
    where: str,
) -> tuple[PackView, ...]
```

Validate the optional extra pictures of an instrument, such as a
view of its back.

**Parameters**

- `value` (*object*): The instrument's ``views`` entry, an object from a view name to a pack-relative picture path, or None.
- `files` (*PackFiles*): The pack's files. Keyword-only.
- `where` (*str*): The instrument's qualified key, used in error messages. Keyword-only.

**Returns**

- *tuple of PackView*: The views, in the order the manifest lists them. Empty when none were declared.

**Raises**

- *ValueError*: If the entry is not a short object of valid names and readable pictures.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # noinspection PyTypeChecker
>>> read_views(
...     None, files=None, where="pack.v.va"
... )
()
```

## read_keyboards

```python
def read_keyboards(
    value: object,
    *,
    where: str,
) -> tuple[PackKeyboard, ...]
```

Validate the optional keyboards of an instrument, which Alto draws
from their ranges.

**Parameters**

- `value` (*object*): The instrument's ``keyboards`` entry, a list of objects, or None.
- `where` (*str*): The instrument's qualified key, used in messages. Keyword-only.

**Returns**

- *tuple of PackKeyboard*: The keyboards in the order the manifest lists them, which is the order Alto draws them from top to bottom. Empty when none were declared.

**Raises**

- *ValueError*: If the entry is not a short list of keyboards with distinct names and natural end keys.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_keyboards(None, where="pack.v.va")
()
>>> read_keyboards(
...     [
...         {
...             "name": "Manual",
...             "lowest": "C4",
...             "highest": "E4",
...         }
...     ],
...     where="pack.v.va",
... )[0].naturals
3
```

## read_positions

```python
def read_positions(
    value: object,
    *,
    where: str,
) -> tuple[tuple[int, str], ...]
```

Validate the optional named positions along a string, which label
the ruler beside the fingerboard.

**Parameters**

- `value` (*object*): The instrument's ``positions`` entry, a list of ``{"name": ..., "half_steps": ...}``, or None when it has none.
- `where` (*str*): The instrument's qualified key, used in error messages. Keyword-only.

**Returns**

- *tuple of (int, str)*: Each position's half steps above the open string and its name, in ascending order. Empty when none were declared.

**Raises**

- *ValueError*: If the entry is not a short list of named, ascending positions with plain-text names.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_positions(
...     [
...         {"name": "1st", "half_steps": 2},
...         {"name": "2nd", "half_steps": 3},
...     ],
...     where="pack.v.va",
... )
((2, '1st'), (3, '2nd'))
>>> read_positions(None, where="pack.v.va")
()
```

## read_instrument

```python
def read_instrument(
    row: object,
    *,
    pack: str,
    files: PackFiles,
    pack_name: str = '',
) -> PackInstrument
```

Validate one declared instrument against its own artwork and
recordings.

**Returns**

- *PackInstrument*: The calibrated instrument available to exercises in this pack.

**Raises**

- *ValueError*: If a required field, string, image, or recording is invalid.
{% endraw %}
