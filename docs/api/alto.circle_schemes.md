---
title: alto.circle_schemes
parent: api
package: alto
permalink: /api/alto.circle_schemes/
---
{% raw %}
The color schemes of the circle of fifths: the presets, and the schemes a user makes.

A scheme says what color each of the 24 cells of the circle is when it is quiet and when it is lit, and whether its wedges
are light, with dark names. The circle blends between the two as a cell brightens. The disc in the middle is not part of a
scheme: it takes the colors of the app's theme. Nothing here needs Qt, so the schemes can be tested, saved and shown anywhere;
`alto.ui.circle` turns them into pictures.

A color is a hue (0 to 360), a saturation and a lightness (both 0 to 1).

**Examples**

```pycon
>>> scheme = preset("cyan-indigo")
>>> scheme.name, scheme.light
('Cyan to indigo', False)
>>> round(scheme.color("outer", place=0, lift=1.0)[2], 2) > round(scheme.color("outer", place=0, lift=0.0)[2], 2)
True
```

## CellMaker

```python
class CellMaker(Protocol)
```

A function that gives the cell at a place on a ring its quiet and lit colors.

## CustomRecord

```python
class CustomRecord(TypedDict)
```

A scheme of the user's own, as it is saved.

**Attributes**

- `id` (*str*): Its key, such as "custom-1".
- `name` (*str*): What the user called it.
- `mode` (*str*): How its colors are made: a key of `MODES`.
- `colors` (*list of str*): The colors the mode takes, as "#rrggbb": what a cell looks like when it is lit.
- `light` (*bool*): Whether the wedges are light, with dark names.

## Scheme

```python
Scheme(
    key: str,
    name: str,
    description: str,
    light: bool,
    cells: dict[str, tuple[Cell, ...]],
)
```

A color scheme for the circle.

**Attributes**

- `key` (*str*): Its identifier, used to save the choice.
- `name` (*str*): Its name, as the settings show it.
- `description` (*str*): A sentence about it.
- `light` (*bool*): Whether the wedges are light, with dark names, instead of dark with white names.
- `cells` (*dict of str to tuple of (tuple of float, tuple of float)*): For each ring ("outer" and "inner"), the 12 cells' quiet and lit colors, clockwise from the top.

### Scheme.color

```python
def color(
    ring: str,
    *,
    place: int,
    lift: float,
) -> tuple[float, float, float]
```

Return the color of a cell as it is lit.

**Parameters**

- `ring` (*str*): "outer" or "inner".
- `place` (*int*): The cell's place, clockwise from the top. Keyword-only.
- `lift` (*float*): How lit it is, from 0 (quiet) to 1 (fully lit). Keyword-only.

**Returns**

- *tuple of float*: Its red, green and blue, each from 0 to 1.

**Examples**

```pycon
>>> red, green, blue = preset("spectrum").color("outer", place=0, lift=1.0)
>>> red > green and red > blue
True
>>> preset("spectrum").color("outer", place=6, lift=0.0)[0] < 0.2
True
```

### Scheme.names

```python
def names() -> dict[str, str]
```

Return the colors of the names written on the wedges.

**Returns**

- *dict of str to str*: "ink" (a key's name) and "muted" (its other name and its numeral), as "#rrggbb".

**Examples**

```pycon
>>> preset("paper").names()["ink"], preset("spectrum").names()["ink"]
('#1b2030', '#f5f5f5')
```

## rgb_of

```python
def rgb_of(
    color: Hsl,
    *,
    capped: bool,
) -> tuple[float, float, float]
```

Turn a color into red, green and blue, keeping a dark circle's cells from getting too bright.

Yellows and greens look far brighter than blues of the same lightness, so on dark wedges a color that is brighter than
white names can stand is brought down to the limit.

**Parameters**

- `color` (*tuple of float*): The hue, saturation and lightness.
- `capped` (*bool*): Whether to bring a too bright color down. Keyword-only.

**Returns**

- *tuple of float*: Red, green and blue, each from 0 to 1.

**Examples**

```pycon
>>> r, g, b = rgb_of((60.0, 0.9, 0.5), capped=True)
>>> 0.299 * r + 0.587 * g + 0.114 * b <= MAX_BRIGHTNESS + 1e-9
True
>>> rgb_of((0.0, 0.0, 1.0), capped=False)
(1.0, 1.0, 1.0)
```

## hex_of

```python
def hex_of(rgb: tuple[float, float, float]) -> str
```

Write a color as "#rrggbb".

**Parameters**

- `rgb` (*tuple of float*): Red, green and blue, each from 0 to 1.

**Returns**

- *str*: The color as hexadecimal.

**Examples**

```pycon
>>> hex_of((1.0, 0.5, 0.0))
'#ff8000'
```

## hsl_of

```python
def hsl_of(text: str) -> Hsl
```

Read a color written as "#rrggbb".

**Parameters**

- `text` (*str*): The color.

**Returns**

- *tuple of float*: Its hue (0 to 360), saturation and lightness.

**Examples**

```pycon
>>> hsl_of("#ff0000")
(0.0, 1.0, 0.5)
```

## signature_of

```python
def signature_of(place: int) -> int
```

Return how far a place is from C, with flats as negative: the key signature of the major key there.

**Parameters**

- `place` (*int*): The place clockwise from the top, 0 to 11.

**Returns**

- *int*: From -5 (five flats) to 6 (six sharps).

**Examples**

```pycon
>>> [signature_of(at) for at in (0, 1, 6, 7, 11)]
[0, 1, 6, -5, -1]
```

## preset

```python
def preset(key: str) -> Scheme
```

Return a preset by its key.

**Parameters**

- `key` (*str*): A key of `PRESETS`.

**Returns**

- *Scheme*: The preset.

**Raises**

- *KeyError*: If there is no such preset.

**Examples**

```pycon
>>> preset("midnight").name
'Midnight'
>>> len(PRESETS)
14
```

## record_of

```python
def record_of(
    key: str,
    *,
    name: str,
    mode: str,
    colors: list[str],
    light: bool = False,
) -> CustomRecord
```

Make the record of a scheme of the user's own.

**Parameters**

- `key` (*str*): Its key, such as "custom-1".
- `name` (*str*): Its name. Keyword-only.
- `mode` (*str*): How its colors are made: a key of `MODES`. Keyword-only.
- `colors` (*list of str*): The colors the mode takes, as "#rrggbb". Keyword-only.
- `light` (*bool, default False*): Whether the wedges are light. Keyword-only.

**Returns**

- *CustomRecord*: The record. Nothing is checked: `clean_record` does that.

**Examples**

```pycon
>>> record_of("custom-1", name="Mine", mode="single", colors=["#2f6bd0"])["light"]
False
```

## clean_record

```python
def clean_record(raw: object) -> CustomRecord | None
```

Check one saved scheme of the user's own, and tidy it.

**Parameters**

- `raw` (*object*): What was read back from the saved data.

**Returns**

- *CustomRecord or None*: The record, with a name of at most 40 characters, or None if anything in it is missing or wrong: an unknown mode, a color that is not "#rrggbb", or the wrong number of colors for the mode.

**Examples**

```pycon
>>> good = record_of("custom-1", name="Mine", mode="rings", colors=["#2f6bd0", "#18a0c0"])
>>> clean_record(good) == good
True
>>> few = record_of("custom-1", name="Mine", mode="rings", colors=["#2f6bd0"])
>>> unknown = record_of("custom-1", name="Mine", mode="nope", colors=["#2f6bd0", "#18a0c0"])
>>> clean_record(few) is None, clean_record(unknown) is None
(True, True)
>>> clean_record("not a record") is None
True
```

## custom_scheme

```python
def custom_scheme(record: CustomRecord) -> Scheme
```

Make a scheme from one of the user's own records.

The colors in a record are what a cell looks like when lit; the quiet cells are the same hue, calmer and darker (or, on a
light wedges, paler).

**Parameters**

- `record` (*CustomRecord*): A record that `clean_record` accepted.

**Returns**

- *Scheme*: The scheme, with the key and name of the record.

**Examples**

```pycon
>>> scheme = custom_scheme(record_of("custom-1", name="Mine", mode="rings", colors=["#2f6bd0", "#18a0c0"]))
>>> scheme.key, scheme.name, scheme.light
('custom-1', 'Mine', False)
>>> scheme.cells["outer"][0][1][0] != scheme.cells["inner"][0][1][0]  # two rings, two hues
True
```

## dump_customs

```python
def dump_customs(records: list[CustomRecord]) -> str
```

Write the user's own schemes as text to save.

**Parameters**

- `records` (*list of CustomRecord*): The schemes.

**Returns**

- *str*: JSON.

**Examples**

```pycon
>>> dump_customs([])
'[]'
```

## load_customs

```python
def load_customs(text: str) -> list[CustomRecord]
```

Read the user's own schemes back, leaving out any that are not valid and any beyond the limit.

**Parameters**

- `text` (*str*): What `dump_customs` wrote.

**Returns**

- *list of CustomRecord*: The valid schemes, each with its own key.

**Examples**

```pycon
>>> load_customs("not json"), load_customs("[1, 2]")
([], [])
>>> one = record_of("custom-1", name="A", mode="single", colors=["#2f6bd0"])
>>> [r["id"] for r in load_customs(dump_customs([one, one]))]  # a repeated key is dropped
['custom-1']
```

## resolve

```python
def resolve(
    key: str,
    *,
    customs: list[CustomRecord],
) -> Scheme
```

Find a scheme by its key, among the presets and the user's own, falling back to the default.

**Parameters**

- `key` (*str*): The saved choice.
- `customs` (*list of CustomRecord*): The user's own schemes. Keyword-only.

**Returns**

- *Scheme*: The scheme, or the default one if the key is unknown (for instance after the scheme was deleted).

**Examples**

```pycon
>>> resolve("midnight", customs=[]).name, resolve("gone", customs=[]).key
('Midnight', 'cyan-indigo')
```

## next_custom_key

```python
def next_custom_key(customs: list[CustomRecord]) -> str
```

Return a key that none of the user's schemes has.

**Parameters**

- `customs` (*list of CustomRecord*): The user's own schemes.

**Returns**

- *str*: "custom-" and the smallest number that is free.

**Examples**

```pycon
>>> taken = [record_of("custom-1", name="", mode="single", colors=[])]
>>> next_custom_key([]), next_custom_key(taken)
('custom-1', 'custom-2')
```
{% endraw %}
