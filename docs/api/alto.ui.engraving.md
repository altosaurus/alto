---
title: alto.ui.engraving
parent: api
package: alto.ui
permalink: /api/alto.ui.engraving/
---
{% raw %}
Drawing notation with SMuFL music fonts (Bravura, Leland, Petaluma,
MuseJazz and others).

A SMuFL font has the parts of a note rather than whole notes: the head,
the flag, and the clef and accidental glyphs,
all measured in staff spaces (four to the em). The stem is a plain
rectangle that the code draws, placed using the stem
anchors the font publishes for each head. Heights are measured upward,
so they are flipped on screen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sorted(HEADS)
['breve', 'half', 'whole']
>>> ACCIDENTALS[1]
'accidentalSharp'
```

## notation_glyph

<div class="api-signature" markdown="1">

```python
@cache
def notation_glyph(
    font: str,
    *,
    codepoint: int,
) -> QPainterPath
```

{% endraw %}{% include api-source.html name="notation_glyph" line=362 %}{% raw %}

</div>

Read a score marking from a bundled font at four staff spaces per
em.

**Parameters**

- `font` (*str*): Preferred SMuFL font key.
- `codepoint` (*int*): Standard Music Font Layout code point.

**Returns**

- *QPainterPath*: Outline at 100 pixels per em. Bravura supplies markings missing in the selected font.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> notation_glyph(
...     "bravura", codepoint=0xE260
... ).isEmpty()
False
```

## staff_line_width

<div class="api-signature" markdown="1">

```python
def staff_line_width(
    font: str,
    *,
    gap: float,
) -> float
```

{% endraw %}{% include api-source.html name="staff_line_width" line=394 %}{% raw %}

</div>

Return the thickness of a staff line, as the font specifies.

**Parameters**

- `font` (*str*): A key of `_FILES`.
- `gap` (*float*): The distance between staff lines in pixels. Keyword-only.

**Returns**

- *float*: The thickness in pixels, at least 1.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff_line_width("bravura", gap=16) >= 1.0
True
```

## ledger_width

<div class="api-signature" markdown="1">

```python
def ledger_width(
    font: str,
    *,
    gap: float,
) -> float
```

{% endraw %}{% include api-source.html name="ledger_width" line=422 %}{% raw %}

</div>

Return the thickness of a ledger line, as the font specifies.

**Parameters**

- `font` (*str*): A key of `_FILES`.
- `gap` (*float*): The distance between staff lines in pixels. Keyword-only.

**Returns**

- *float*: The thickness in pixels, at least 1.2.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ledger_width("bravura", gap=16) >= 1.2
True
```

## fill_path

<div class="api-signature" markdown="1">

```python
def fill_path(
    p: QPainter,
    *,
    path: QPainterPath,
    color: QColor,
) -> None
```

{% endraw %}{% include api-source.html name="fill_path" line=450 %}{% raw %}

</div>

Fill a path with a color and no outline.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `path` (*QPainterPath*): What to fill. Keyword-only.
- `color` (*QColor*): The color. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     20, 20, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("white"))
>>> painter = QPainter(image)
>>> square = QPainterPath()
>>> square.addRect(QRectF(5, 5, 10, 10))
>>> fill_path(
...     painter,
...     path=square,
...     color=QColor("black"),
... )
>>> painter.end()
True
>>> image.pixelColor(10, 10).lightness() < 128
True
```

## draw_note

<div class="api-signature" markdown="1">

```python
def draw_note(
    p: QPainter,
    *,
    font: str,
    value: str,
    x: float,
    y: float,
    gap: float,
    color: QColor,
    stem_down: bool = False,
    flag_color: QColor | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="draw_note" line=495 %}{% raw %}

</div>

Draw a note with its head centered on a point.

The head, then a stem and (for the short values) a flag, placed on
the font's anchors.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `font` (*str*): A key of `_FILES`. Keyword-only.
- `value` (*str*): "breve", "whole", "half", "quarter", "eighth", "sixteenth" or "thirty_second". Keyword-only.
- `x` (*float*): The head's center, in pixels. Keyword-only.
- `y` (*float*): The head's center, in pixels. Keyword-only.
- `gap` (*float*): The distance between staff lines in pixels. Keyword-only.
- `color` (*QColor*): The color. Keyword-only.
- `flag_color` (*QColor or None*): Optional highlight for the flag alone. Keyword-only.
- `stem_down` (*bool, default False*): Draw the stem down. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("white"))
>>> painter = QPainter(image)
>>> draw_note(
...     painter,
...     font="bravura",
...     value="eighth",
...     x=50,
...     y=60,
...     gap=16,
...     color=QColor("black"),
... )
>>> painter.end()
True
>>> image.pixelColor(50, 60).lightness() < 128
True
```

## draw_beamed_notes

<div class="api-signature" markdown="1">

```python
def draw_beamed_notes(
    p: QPainter,
    *,
    font: str,
    heads: list[QPointF],
    colors: list[QColor],
    gap: float,
    middle: float,
    ink: QColor,
    beams: int = 1,
) -> None
```

{% endraw %}{% include api-source.html name="draw_beamed_notes" line=622 %}{% raw %}

</div>

Draw a group with one beam for eighths or more for shorter notes.

**Parameters**

- `p` (*QPainter*): Score painter.
- `font` (*str*): Selected SMuFL font.
- `heads` (*list of QPointF*): Notehead centers in reading order.
- `colors` (*list of QColor*): Ink for each notehead and its stem.
- `gap` (*float*): Staff space in pixels.
- `middle` (*float*): Height of the middle staff line, for choosing stem direction.
- `ink` (*QColor*): Color of the shared beams.
- `beams` (*int*): Number of beams for the written duration.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QPicture
>>> with QPainter(QPicture()) as painter:  # doctest: +SKIP
...     draw_beamed_notes(
...         painter, font="bravura", gap=8, middle=40,
...         heads=[QPointF(20, 48), QPointF(40, 44)],
...         colors=[QColor("black")] * 2, ink=QColor("black"),
...     )
```

## draw_clef

<div class="api-signature" markdown="1">

```python
def draw_clef(
    p: QPainter,
    *,
    font: str,
    clef: str,
    x: float,
    bottom: float,
    gap: float,
    color: QColor,
) -> None
```

{% endraw %}{% include api-source.html name="draw_clef" line=738 %}{% raw %}

</div>

Draw a clef with its left edge at a point.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `font` (*str*): A key of `_FILES`. Keyword-only.
- `clef` (*str*): "treble", "bass", "alto", "tenor", "soprano", "mezzo", "baritone_c" or "baritone_f". Keyword-only.
- `x` (*float*): The clef's left edge, in pixels. Keyword-only.
- `bottom` (*float*): The y position of the staff's bottom line, in pixels. Keyword-only.
- `gap` (*float*): The distance between staff lines in pixels. Keyword-only.
- `color` (*QColor*): The color. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> image.fill(QColor("white"))
>>> painter = QPainter(image)
>>> draw_clef(
...     painter,
...     font="bravura",
...     clef="treble",
...     x=10,
...     bottom=70,
...     gap=10,
...     color=QColor("black"),
... )
>>> painter.end()
True
>>> any(
...     image.pixelColor(x_, y).lightness()
...     < 128
...     for x_ in range(10, 40)
...     for y in range(20, 90)
... )
True
```

## accidental_width

<div class="api-signature" markdown="1">

```python
def accidental_width(
    *,
    font: str,
    sign: int,
    gap: float,
) -> float
```

{% endraw %}{% include api-source.html name="accidental_width" line=810 %}{% raw %}

</div>

Return how wide a sharp, flat or natural is drawn, so that it can be
placed beside other things.

**Parameters**

- `font` (*str*): A key of `_FILES`. Keyword-only.
- `sign` (*int*): -2 for a double flat, -1 flat, 0 natural, 1 sharp or 2 double sharp. Keyword-only.
- `gap` (*float*): The distance between staff lines in pixels, which sets the size. Keyword-only.

**Returns**

- *float*: The width of the glyph's ink, in pixels.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> accidental_width(
...     font="bravura", sign=1, gap=16
... ) > accidental_width(
...     font="bravura", sign=1, gap=8
... )
True
```

## draw_accidental

<div class="api-signature" markdown="1">

```python
def draw_accidental(
    p: QPainter,
    *,
    font: str,
    sign: int,
    x: float,
    y: float,
    gap: float,
    color: QColor,
    fit: float | None = None,
) -> float
```

{% endraw %}{% include api-source.html name="draw_accidental" line=849 %}{% raw %}

</div>

Draw a sharp, flat or natural with its left edge at a point.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `font` (*str*): A key of `_FILES`. Keyword-only.
- `sign` (*int*): -2 for a double flat, -1 flat, 0 natural, 1 sharp or 2 double sharp. Keyword-only.
- `x` (*float*): The glyph's left edge, in pixels. Keyword-only.
- `y` (*float*): The glyph's reference line, in pixels. Keyword-only.
- `gap` (*float*): The distance between staff lines in pixels. Keyword-only.
- `color` (*QColor*): The color. Keyword-only.
- `fit` (*float or None, default None*): If given, shrink the glyph to be no wider than this many pixels. Keyword-only.

**Returns**

- *float*: The width drawn, in pixels.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> painter = QPainter(image)
>>> normal = draw_accidental(
...     painter,
...     font="bravura",
...     sign=1,
...     x=10,
...     y=50,
...     gap=16,
...     color=QColor("black"),
... )
>>> squeezed = draw_accidental(
...     painter,
...     font="bravura",
...     sign=1,
...     x=10,
...     y=50,
...     gap=16,
...     color=QColor("black"),
...     fit=5.0,
... )
>>> painter.end()
True
>>> squeezed <= 5.0 < normal
True
```

## draw_brace

<div class="api-signature" markdown="1">

```python
def draw_brace(
    p: QPainter,
    *,
    font: str,
    x: float,
    y0: float,
    y1: float,
    color: QColor,
    width: float,
) -> bool
```

{% endraw %}{% include api-source.html name="draw_brace" line=938 %}{% raw %}

</div>

Draw the font's brace stretched between two heights, for a grand
staff.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `font` (*str*): A key of `_FILES`. Keyword-only.
- `x` (*float*): The brace's right edge, in pixels. Keyword-only.
- `y0` (*float*): The top, in pixels. Keyword-only.
- `y1` (*float*): The bottom, in pixels. Keyword-only.
- `color` (*QColor*): The color. Keyword-only.
- `width` (*float*): How wide to draw it, in pixels. Keyword-only.

**Returns**

- *bool*: True if it was drawn; False (and nothing is drawn) if the font has no usable brace.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     100, 100, QImage.Format.Format_ARGB32
... )
>>> painter = QPainter(image)
>>> draw_brace(
...     painter,
...     font="bravura",
...     x=30,
...     y0=10,
...     y1=90,
...     color=QColor("black"),
...     width=12,
... )
True
>>> painter.end()
True
```
{% endraw %}
