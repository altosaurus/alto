---
title: alto.ui.pictures
parent: api
package: alto.ui
permalink: /api/alto.ui.pictures/
---
{% raw %}
Small pictures of musical things (clefs, note values, key signatures,
note ranges ...) for the settings panes.

Each picture is drawn in fixed units and then scaled, so the same
picture serves as a summary in a menu row and, larger,
as the label of a choice. Colors come from the palette, so they work in
light and dark themes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     CLEF_NAMES["treble"],
...     VALUE_NAMES["sixteenth"],
... )
('Treble', '16th')
>>> ClefPictures(["treble", "bass"]).toolTip()
'Treble, Bass'
```

## symbol_icon

<div class="api-signature" markdown="1">

```python
def symbol_icon(
    symbol: str,
    *,
    color: QColor,
    height: int = 56,
) -> QIcon
```

{% endraw %}{% include api-source.html name="symbol_icon" line=103 %}{% raw %}

</div>

Draw a clef symbol on its own, without a staff, as an icon.

The G, C and F clefs are drawn the same size as they are on a staff,
so the three look alike beside one another, and centered.

**Parameters**

- `symbol` (*str*): "G", "C" or "F".
- `color` (*QColor*): The color to draw it in. Keyword-only.
- `height` (*int, default 56*): The icon's height in pixels, which is also as wide as it is. Keyword-only.

**Returns**

- *QIcon*: The icon, in the notation font chosen in the settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> symbol_icon(
...     "F", color=QColor("black")
... ).isNull()
False
```

## ClefPictures

<div class="api-signature" markdown="1">

```python
ClefPictures(
    clefs: list[str] | None = None,
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ClefPictures" line=560 %}{% raw %}

</div>

Bases: `_Picture`

The selected clefs, each on its own five-line staff, and a two-stave
picture with a brace for the grand staff.

Showing each clef on its own staff lets alto and tenor, which share
a symbol, look different.

**Attributes**

- `H, W, GAP, SPACING` (*float*): The picture's height, the width of one clef, the distance between staff lines and the space between clefs.
- `NAMES` (*dict of str to str*): The name of each clef.
- `clefs` (*list of str*): The clefs shown.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures(["alto", "tenor"]).toolTip()
'Alto, Tenor'
```

**Constructor**

Create the picture.

**Parameters**

- `clefs` (*list of str or None, default None*): The clefs to show, any of `CLEF_NAMES`.
- `scale` (*float, default 1.0*): How much to enlarge it. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures(["treble"], scale=2.0).width()
60
```

### ClefPictures.set_clefs

<div class="api-signature" markdown="1">

```python
def set_clefs(clefs: list[str]) -> None
```

{% endraw %}{% include api-source.html name="ClefPictures.set_clefs" line=616 %}{% raw %}

</div>

Show different clefs and size the picture for them.

**Parameters**

- `clefs` (*list of str*): The clefs to show, any of `CLEF_NAMES`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = ClefPictures()
>>> pictures.set_clefs(
...     ["treble", "bass", "alto"]
... )
>>> pictures.width()  # three clefs and the space between them
106
>>> pictures.toolTip()
'Treble, Bass, Alto'
```

### ClefPictures.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    clef: str,
    *,
    scale: float = 1.8,
) -> QIcon
```

{% endraw %}{% include api-source.html name="ClefPictures.icon" line=643 %}{% raw %}

</div>

Return one clef as an icon.

**Parameters**

- `clef` (*str*): A key of `CLEF_NAMES`.
- `scale` (*float, default 1.8*): How much to enlarge it. Keyword-only.

**Returns**

- *QIcon*: The icon.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures.icon("grand").isNull()
False
```

### ClefPictures.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="ClefPictures.paintEvent" line=671 %}{% raw %}

</div>

Draw each clef on its staff, or the grand staff with its brace.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefPictures(
...     ["treble", "grand"]
... ).grab().isNull()
False
```

## ValuePictures

<div class="api-signature" markdown="1">

```python
ValuePictures(
    values: list[str] | None = None,
    *,
    scale: float = 1.0,
    center_stemless: bool = False,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ValuePictures" line=800 %}{% raw %}

</div>

Bases: `_Picture`

Note values as engraved symbols (no staff), each with its head on
the same baseline so they line up.

**Attributes**

- `values` (*list of str*): The note values shown, keys of `VALUE_NAMES`.
- `center_stemless` (*bool*): Whether the double whole note and whole note sit at the picture's vertical center.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = ValuePictures(
...     ["whole", "quarter", "eighth"]
... )
>>> pictures.values
['whole', 'quarter', 'eighth']
```

**Constructor**

Create the picture.

**Parameters**

- `values` (*list of str or None, default None*): The note values to show.
- `scale` (*float, default 1.0*): How much to enlarge it. Keyword-only.
- `center_stemless` (*bool, default False*): Center double whole notes and whole notes vertically so they align with the middle of adjacent text. Other notes keep their heads low so their stems fit above. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ValuePictures(
...     ["half"], center_stemless=True
... ).center_stemless
True
```

### ValuePictures.set_values

<div class="api-signature" markdown="1">

```python
def set_values(values: list[str]) -> None
```

{% endraw %}{% include api-source.html name="ValuePictures.set_values" line=870 %}{% raw %}

</div>

Show different note values and size the picture for them.

**Parameters**

- `values` (*list of str*): The note values to show.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = ValuePictures()
>>> pictures.set_values(["breve", "whole"])
>>> pictures.values
['breve', 'whole']
```

### ValuePictures.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    value: str,
    *,
    scale: float = 1.7,
) -> QIcon
```

{% endraw %}{% include api-source.html name="ValuePictures.icon" line=898 %}{% raw %}

</div>

Return one note value as an icon.

**Parameters**

- `value` (*str*): A key of `VALUE_NAMES`.
- `scale` (*float, default 1.7*): How much to enlarge it. Keyword-only.

**Returns**

- *QIcon*: The icon.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ValuePictures.icon("quarter").isNull()
False
```

### ValuePictures.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="ValuePictures.paintEvent" line=926 %}{% raw %}

</div>

Draw each note value.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ValuePictures(
...     ["whole", "half", "quarter"]
... ).grab().isNull()
False
```

## rhythm_picture

<div class="api-signature" markdown="1">

```python
def rhythm_picture(term: str) -> ValuePictures | None
```

{% endraw %}{% include api-source.html name="rhythm_picture" line=1027 %}{% raw %}

</div>

Render a single note, rest, tied pair, or beamed pair from an
equation term.

**Parameters**

- `term` (*str*): The stored term, with a tilde between tied notes or a bar between beamed notes.

**Returns**

- *ValuePictures or None*: The engraved term, or None for an operator, numeral, or blank.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> rhythm_picture("eighth|eighth").beam_count
1
```

## KeySignaturePicture

<div class="api-signature" markdown="1">

```python
KeySignaturePicture(
    key: int = 0,
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeySignaturePicture" line=1059 %}{% raw %}

</div>

Bases: `_Picture`

A key signature as a plain row of its sharps or flats, with no staff
or clef.

Each sign sits at the height it has after a treble clef, and C
major, which has none, shows a natural sign.

**Attributes**

- `H, GAP, STEP` (*float*): The picture's height, the distance between staff lines and the space between signs.
- `ORDER` (*dict of int to str*): Where each sign is written, in order, for sharps (1) and flats (-1).
- `key` (*int*): The key signature: sharps if positive, flats if negative.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture(2).toolTip()
'D major: 2 sharps'
```

**Constructor**

Create the picture.

**Parameters**

- `key` (*int, default 0*): The key signature: that many sharps if positive, flats if negative.
- `scale` (*float, default 1.0*): How much to enlarge it. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture(0).toolTip()
'C major: no sharps or flats'
>>> KeySignaturePicture(-1).toolTip()
'F major: 1 flat'
```

### KeySignaturePicture.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    key: int,
    *,
    scale: float = 1.2,
) -> QIcon
```

{% endraw %}{% include api-source.html name="KeySignaturePicture.icon" line=1140 %}{% raw %}

</div>

Return a key signature as an icon.

**Parameters**

- `key` (*int*): Sharps if positive, flats if negative.
- `scale` (*float, default 1.2*): How much to enlarge it. Keyword-only.

**Returns**

- *QIcon*: The icon.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture.icon(3).isNull()
False
```

### KeySignaturePicture.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="KeySignaturePicture.paintEvent" line=1234 %}{% raw %}

</div>

Draw the row of sharps or flats, or a natural sign for C major.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePicture(-3).grab().isNull()
False
```

## RangePictures

<div class="api-signature" markdown="1">

```python
RangePictures(
    items: list[tuple[str, int, int]] | None = None,
    *,
    scale: float = 1.0,
    max_width: float | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="RangePictures" line=1272 %}{% raw %}

</div>

Bases: `_Picture`

For each clef, a staff with its lowest and highest note, so the
range can be read off at a glance.

**Attributes**

- `H, W, SPACING` (*float*): The picture's height, the width of one staff and the space between staves.
- `MAX_SCALE` (*float*): The most the picture is enlarged to fit `max_width`.
- `max_width` (*float or None*): The width to enlarge the picture to, if any.
- `items` (*list of tuple of (str, int, int)*): Each clef with its lowest and highest note, as staff steps (`Note.diatonic`).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = RangePictures(
...     [("treble", 22, 52)]
... )
>>> pictures.toolTip()
'Treble: D3 to F7'
```

**Constructor**

Create the picture.

**Parameters**

- `items` (*list of tuple of (str, int, int) or None, default None*): Each clef with its lowest and highest note.
- `scale` (*float, default 1.0*): How much to enlarge it. Keyword-only.
- `max_width` (*float or None, default None*): Enlarge the picture to use this width (up to `MAX_SCALE`) however many clefs there are. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RangePictures(
...     [("treble", 22, 52)], max_width=238
... ).scale
1.9
```

### RangePictures.set_items

<div class="api-signature" markdown="1">

```python
def set_items(items: list[tuple[str, int, int]]) -> None
```

{% endraw %}{% include api-source.html name="RangePictures.set_items" line=1337 %}{% raw %}

</div>

Show the ranges of some clefs and size the picture for them.

**Parameters**

- `items` (*list of tuple of (str, int, int)*): Each clef with its lowest and highest note, as staff steps (`Note.diatonic`).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pictures = RangePictures()
>>> pictures.set_items(
...     [("bass", 10, 40), ("alto", 21, 35)]
... )
>>> pictures.toolTip().splitlines()
['Bass: F1 to A5', 'Alto: C3 to C5']
```

### RangePictures.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="RangePictures.paintEvent" line=1457 %}{% raw %}

</div>

Draw a staff for each clef with its lowest and highest note.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RangePictures(
...     [("treble", 22, 52), ("bass", 10, 40)]
... ).grab().isNull()
False
```

## NamePicture

<div class="api-signature" markdown="1">

```python
NamePicture(
    naming: str = 'letters',
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="NamePicture" line=1569 %}{% raw %}

</div>

Bases: `_Picture`

How notes are named: C, D and E on a staff, labeled with letters,
solfège syllables or scale degrees.

**Attributes**

- `H, W` (*float*): The picture's height and width.
- `LETTERS, SYLLABLES` (*tuple of str*): The two sets of labels.
- `naming` (*str*): "letters", "solfege", "degrees" (caret) or "functions".

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture("solfege").toolTip()
'Solfège (Do Re Mi)'
```

**Constructor**

Create the picture.

**Parameters**

- `naming` (*str, default "letters"*): "letters", "solfege", "degrees" (caret) or "functions".
- `scale` (*float, default 1.0*): How much to enlarge it. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture().naming
'letters'
```

### NamePicture.set_naming

<div class="api-signature" markdown="1">

```python
def set_naming(naming: str) -> None
```

{% endraw %}{% include api-source.html name="NamePicture.set_naming" line=1621 %}{% raw %}

</div>

Choose which labels are drawn.

**Parameters**

- `naming` (*str*): "letters" for C D E, "solfege" for Do Re Mi, or "degrees" for 1̂ 2̂ 3̂, or "functions" for function names.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picture = NamePicture()
>>> picture.set_naming("solfege")
>>> picture.toolTip()
'Solfège (Do Re Mi)'
```

### NamePicture.icon

<div class="api-signature" markdown="1">

```python
@classmethod
def icon(
    naming: str,
    *,
    scale: float = 1.6,
) -> QIcon
```

{% endraw %}{% include api-source.html name="NamePicture.icon" line=1647 %}{% raw %}

</div>

Return the picture as an icon.

**Parameters**

- `naming` (*str*): "letters", "solfege", "degrees" (caret) or "functions".
- `scale` (*float, default 1.6*): How much to enlarge it. Keyword-only.

**Returns**

- *QIcon*: The icon.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture.icon("letters").isNull()
False
```

### NamePicture.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="NamePicture.paintEvent" line=1675 %}{% raw %}

</div>

Draw the staff, the clef, the three notes and their labels.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole widget is always redrawn.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NamePicture("letters").grab().isNull()
False
```
{% endraw %}
