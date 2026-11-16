---
title: alto.ui.circle
parent: api
package: alto.ui
order: 24
permalink: /api/alto.ui.circle/
---
{% raw %}
The circle of fifths: twelve wedges, the major keys on the outside and their relative minors on the inside.

C is at the top and each step clockwise is a fifth up, so the keys gather sharps on the right and flats on the left. The
disc in the middle shows the staff and key signature of the key being talked about. In an exercise one wedge is the question
and its name (or its Roman numeral) is blank until the answer is right.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.show_question("major", place=3, title="F♯ minor")
>>> circle.target
('outer', 3)
```

## wedge_path

```python
def wedge_path(
    *,
    centre: QPointF,
    inner: float,
    outer: float,
    index: int,
) -> QPainterPath
```

Return the outline of one wedge of a ring.

**Parameters**

- `centre` (*QPointF*): The middle of the circle.
- `inner` (*float*): The radius of the wedge's inner edge, in pixels. Keyword-only.
- `outer` (*float*): The radius of its outer edge. Keyword-only.
- `index` (*int*): Which wedge: 0 is the one at the top and they go clockwise. Keyword-only.

**Returns**

- *QPainterPath*: A closed shape, a piece of a ring 30 degrees wide.

**Examples**

```pycon
>>> shape = wedge_path(centre=QPointF(100, 100), inner=40, outer=90, index=0)
>>> shape.contains(QPointF(100, 30)), shape.contains(QPointF(100, 170))  # the top of the circle, and the bottom
(True, False)
```

## wedge_middle

```python
def wedge_middle(
    *,
    centre: QPointF,
    radius: float,
    index: int,
) -> QPointF
```

Return the point in the middle of a wedge, at a given distance from the centre.

**Parameters**

- `centre` (*QPointF*): The middle of the circle.
- `radius` (*float*): How far out, in pixels. Keyword-only.
- `index` (*int*): Which wedge, clockwise from the top. Keyword-only.

**Returns**

- *QPointF*: The point.

**Examples**

```pycon
>>> wedge_middle(centre=QPointF(100, 100), radius=50, index=0).toTuple()  # straight up
(100.0, 50.0)
>>> round(wedge_middle(centre=QPointF(100, 100), radius=50, index=3).x())  # a quarter of the way round: to the right
150
```

## wedge_color

```python
def wedge_color(
    index: int,
    *,
    inner: bool,
    lift: float = 0.0,
    scheme: Scheme | None = None,
) -> QColor
```

Return the colour of a wedge in a colour scheme: quiet when it is not being talked about and bright when it is.

**Parameters**

- `index` (*int*): Which wedge, clockwise from the top.
- `inner` (*bool*): Whether it is in the inner ring. Keyword-only.
- `lift` (*float, default 0.0*): How bright it is, from 0 (quiet) to 1 (lit). Keyword-only.
- `scheme` (*Scheme or None, default None*): The colour scheme; the one chosen in the circle of fifths settings if None. Keyword-only.

**Returns**

- *QColor*: The colour.

**Examples**

```pycon
>>> from alto.circle_schemes import preset
>>> spectrum = preset("spectrum")
>>> wedge_color(0, inner=False, lift=1.0, scheme=spectrum).hue(), wedge_color(6, inner=False, scheme=spectrum).hue()
(0, 180)
>>> lit, quiet = (wedge_color(0, inner=False, lift=amount, scheme=spectrum) for amount in (1.0, 0.0))
>>> lit.lightness() > quiet.lightness()
True
>>> # no wedge looks too bright for white names
>>> every = [wedge_color(i, inner=False, lift=1.0, scheme=spectrum) for i in range(12)]
>>> all(0.299 * c.redF() + 0.587 * c.greenF() + 0.114 * c.blueF() <= 0.44 for c in every)
True
```

## write_text

```python
def write_text(
    p: QPainter,
    *,
    centre: QPointF,
    text: str,
    pixels: float,
    weight: QFont.Weight,
    colour: QColor,
    max_width: float | None = None,
) -> None
```

Write a line of text centred on a point, with its sharps and flats drawn as the notation font draws them.

The letters are in the app's own font. Its ♭ is the shape of a small "b", though, and does not look like a flat sign, so
the sharps, flats and naturals are the glyphs of the notation style that the staff is drawn in, sized to the letters.

**Parameters**

- `p` (*QPainter*): The painter to draw with.
- `centre` (*QPointF*): The middle of the line. Keyword-only.
- `text` (*str*): What to write, such as "B♭m" or "F♯ major". Keyword-only.
- `pixels` (*float*): The size of the letters. Keyword-only.
- `weight` (*QFont.Weight*): How heavy they are. Keyword-only.
- `colour` (*QColor*): The colour. Keyword-only.
- `max_width` (*float or None, default None*): The widest the line may be. A longer line is written smaller to fit. Keyword-only.

**Examples**

```pycon
>>> from PySide6.QtGui import QImage
>>> image = QImage(120, 60, QImage.Format.Format_ARGB32)
>>> image.fill(QColor("black"))
>>> painter = QPainter(image)
>>> write_text(painter, centre=QPointF(60, 30), text="B♭m", pixels=24, weight=QFont.Weight.Bold, colour=QColor("white"))
>>> painter.end()
True
>>> any(image.pixelColor(x, 30).lightness() > 128 for x in range(20, 100))
True
```

## FifthsCircle

```python
FifthsCircle(parent: QWidget | None = None)
```

Bases: `QWidget`

The circle of fifths, drawn for an exercise.

**Attributes**

- `kind` (*str*): What is being asked: "major", "minor" or "numeral", or "" for nothing.
- `target` (*tuple of (str, int) or None*): The cell asked about: its ring ("outer" or "inner") and its place clockwise from the top.
- `shown` (*dict of str to set of int*): For each ring, the places whose key name is written.
- `lit` (*set of int*): The places of the chords of the key, in a Roman numeral question; both rings are lit there.
- `numerals` (*dict of tuple of (str, int) to str*): The Roman numeral written in each cell that has one.
- `title` (*str*): The big text in the middle.
- `subtitle` (*str*): The small text in the middle.
- `signature` (*int or None*): The key signature drawn on the staff in the middle, or None for no staff.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.show_question("major", place=0, title="A minor")
>>> circle.reveal(animate=False)
>>> circle.shown["outer"], circle.signature
({0}, 0)
```

**Constructor**

Build the circle, with nothing asked.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> FifthsCircle().target is None
True
```

### FifthsCircle.sizeHint

```python
def sizeHint() -> QSize
```

Return the size it would like: a square, big enough to read.

**Returns**

- *QSize*: The size.

**Examples**

```pycon
>>> FifthsCircle().sizeHint().width()
460
```

### FifthsCircle.show_question

```python
def show_question(
    kind: str,
    *,
    place: int,
    title: str,
    ring: str | None = None,
    key: int | None = None,
) -> None
```

Ask about a cell, showing what the question needs and leaving the answer blank.

A "major" question shows the minor keys and asks for the major of one of them; a "minor" question shows the majors and
asks for a minor; a "numeral" question shows every name, lights the six chords of a key with its staff in the middle, and
asks for the Roman numeral of one of them.

**Parameters**

- `kind` (*str*): "major", "minor" or "numeral".
- `place` (*int*): The place of the cell asked about, clockwise from the top. Keyword-only.
- `title` (*str*): The big text in the middle, such as "F♯ minor". Keyword-only.
- `ring` (*str or None, default None*): The ring of the cell asked about; for "major" the outer one and for "minor" the inner one if None. Keyword-only.
- `key` (*int or None, default None*): For a "numeral" question, the place of the key whose chords they are. Keyword-only.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.show_question("minor", place=3, title="A major")
>>> circle.target, circle.shown["outer"] == set(range(12)), circle.shown["inner"], circle.signature
(('inner', 3), True, set(), None)
>>> circle.show_question("numeral", place=11, ring="outer", key=0, title="C major")
>>> sorted(circle.lit), circle.signature, circle.numerals
([0, 1, 11], 0, {})
```

### FifthsCircle.reset

```python
def reset() -> None
```

Clear everything: no question, no names shown, no animation running.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.show_question("major", place=2, title="B minor")
>>> circle.reset()
>>> circle.target is None and circle.title == "" and circle.lit == set()
True
```

### FifthsCircle.reveal

```python
def reveal(
    *,
    animate: bool = True,
) -> None
```

Show the answer: the key's name in its cell, brightened, and its staff and key signature in the middle.

For a Roman numeral question every chord of the key shows its numeral, as the circle in the reference does.

**Parameters**

- `animate` (*bool, default True*): Brighten the cell gradually; if False it is bright at once. Keyword-only.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.show_question("minor", place=5, title="B major / C♭ major")
>>> circle.reveal(animate=False)
>>> circle.shown["inner"], circle.title, circle.subtitle, circle.signature
({5}, 'G♯ minor', '5 sharps', 5)
```

### FifthsCircle.set_subtitle

```python
def set_subtitle(text: str) -> None
```

Change the small text in the middle, for example to say that a second answer is wanted.

**Parameters**

- `text` (*str*): The new text.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.set_subtitle("and its other name")
>>> circle.subtitle
'and its other name'
```

### FifthsCircle.flash_wrong

```python
def flash_wrong() -> None
```

Flash the cell asked about in the red of a wrong answer, striped as well so that it still shows on the red wedge.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.show_question("major", place=0, title="A minor")
>>> circle.flash_wrong()
>>> circle._warning is not None
True
```

### FifthsCircle.lift_of

```python
def lift_of(
    ring: str,
    *,
    place: int,
) -> float
```

Return how bright a cell is drawn, from 0 (quiet) to 1 (fully lit).

The cell asked about is half lit, and brightens when it is answered. The cell beside it on the other ring is a little
lit, to show the pair; in a Roman numeral question the six chords of the key are lit instead.

**Parameters**

- `ring` (*str*): "outer" or "inner".
- `place` (*int*): The place clockwise from the top. Keyword-only.

**Returns**

- *float*: The brightness.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.show_question("major", place=0, title="A minor")
>>> circle.lift_of("outer", place=0), circle.lift_of("inner", place=0), circle.lift_of("outer", place=5)
(0.5, 0.3, 0.0)
>>> circle.reveal(animate=False)
>>> circle.lift_of("outer", place=0)
1.0
```

### FifthsCircle.geometry_of

```python
def geometry_of() -> tuple[QPointF, float]
```

Return where the circle is drawn: its middle and its radius.

The circle fits the widget as a square in the middle of it, but no larger than `MAX_RADIUS`.

**Returns**

- *tuple of QPointF and float*: The centre and the radius, in pixels.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.resize(400, 300)
>>> middle, radius = circle.geometry_of()
>>> middle.toTuple(), radius < 150
((200.0, 150.0), True)
>>> circle.resize(2400, 2000)
>>> circle.geometry_of()[1] == MAX_RADIUS
True
```

### FifthsCircle.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw the two rings, the names, the question and the disc in the middle.

**Parameters**

- `_` (*QPaintEvent*): The paint request; the whole circle is always redrawn.

**Examples**

```pycon
>>> circle = FifthsCircle()
>>> circle.resize(400, 400)
>>> circle.show_question("major", place=0, title="A minor")
>>> circle.grab().isNull()
False
```
{% endraw %}
