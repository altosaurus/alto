---
title: FifthsCircle
parent: alto.ui.circle
api_module: alto.ui.circle
package: alto.ui
permalink: /api/alto.ui.circle/class-fifthscircle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
FifthsCircle(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="FifthsCircle" line=460 %}{% raw %}

</div>

Bases: `QWidget`

The circle of fifths, drawn for an exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `kind` | `str` | What is being asked: "major", "minor" or "numeral", or "" for nothing. |
| `target` | `tuple of (str, int) or None` | The cell asked about: its ring ("outer" or "inner") and its place clockwise from the top. |
| `shown` | `dict of str to set of int` | For each ring, the places whose key name is written. |
| `lit` | `set of int` | The places of the chords of the key, in a Roman numeral question; both rings are lit there. |
| `numerals` | `dict of tuple of (str, int) to str` | The Roman numeral written in each cell that has one. |
| `title` | `str` | The big text in the middle. |
| `subtitle` | `str` | The small text in the middle. |
| `signature` | `int or None` | The key signature drawn on the staff in the middle, or None for no staff. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.show_question(
...     "major", place=0, title="A minor"
... )
>>> circle.reveal(animate=False)
>>> circle.shown["outer"], circle.signature
({0}, 0)
```

**Constructor**

Build the circle, with nothing asked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> FifthsCircle().target is None
True
```

## FifthsCircle.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="FifthsCircle.sizeHint" line=539 %}{% raw %}

</div>

Return the size it would like: a square, big enough to read.

**Returns**

| Type | Description |
| --- | --- |
| `QSize` | The size. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> FifthsCircle().sizeHint().width()
460
```

## FifthsCircle.set_question

<div class="api-signature" markdown="1">

```python
def set_question(question: Question) -> None
```

{% endraw %}{% include api-source.html name="FifthsCircle.set_question" line=555 %}{% raw %}

</div>

Display a circle question using its caption and selected cell.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The exercise question to display. |

**Examples**

```text
A numeral question highlights the selected chord's key.
```

## FifthsCircle.show_question

<div class="api-signature" markdown="1">

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

{% endraw %}{% include api-source.html name="FifthsCircle.show_question" line=577 %}{% raw %}

</div>

Ask about a cell, showing what the question needs and leaving
the answer blank.

A "major" question shows the minor keys and asks for the major
of one of them; a "minor" question shows the majors and
asks for a minor; a "numeral" question shows every name, lights
the six chords of a key with its staff in the middle, and
asks for the Roman numeral of one of them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `kind` | `str` | "major", "minor" or "numeral". |
| `place` | `int` | The place of the cell asked about, clockwise from the top. Keyword-only. |
| `title` | `str` | The big text in the middle, such as "F♯ minor". Keyword-only. |
| `ring` | `str or None, default None` | The ring of the cell asked about; for "major" the outer one and for "minor" the inner one if None. Keyword-only. |
| `key` | `int or None, default None` | For a "numeral" question, the place of the key whose chords they are. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.show_question(
...     "minor", place=3, title="A major"
... )
>>> (
...     circle.target,
...     circle.shown["outer"] == set(range(12)),
...     circle.shown["inner"],
...     circle.signature,
... )
(('inner', 3), True, set(), None)
>>> circle.show_question(
...     "numeral",
...     place=11,
...     ring="outer",
...     key=0,
...     title="C major",
... )
>>> (
...     sorted(circle.lit),
...     circle.signature,
...     circle.numerals,
... )
([0, 1, 11], 0, {})
```

## FifthsCircle.reset

<div class="api-signature" markdown="1">

```python
def reset() -> None
```

{% endraw %}{% include api-source.html name="FifthsCircle.reset" line=753 %}{% raw %}

</div>

Clear everything: no question, no names shown, no animation
running.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.show_question(
...     "major", place=2, title="B minor"
... )
>>> circle.reset()
>>> (
...     circle.target is None
...     and circle.title == ""
...     and circle.lit == set()
... )
True
```

## FifthsCircle.reveal

<div class="api-signature" markdown="1">

```python
def reveal(
    *,
    animate: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="FifthsCircle.reveal" line=785 %}{% raw %}

</div>

Show the answer: the key's name in its cell, brightened, and its
staff and key signature in the middle.

For a Roman numeral question every chord of the key shows its
numeral, as the circle in the reference does.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `animate` | `bool, default True` | Brighten the cell gradually; if False it is bright at once. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.show_question(
...     "minor",
...     place=5,
...     title="B major / C♭ major",
... )
>>> circle.reveal(animate=False)
>>> (
...     circle.shown["inner"],
...     circle.title,
...     circle.subtitle,
...     circle.signature,
... )
({5}, 'G♯ minor', '5 sharps', 5)
```

## FifthsCircle.set_subtitle

<div class="api-signature" markdown="1">

```python
def set_subtitle(text: str) -> None
```

{% endraw %}{% include api-source.html name="FifthsCircle.set_subtitle" line=837 %}{% raw %}

</div>

Change the small text in the middle, for example to say that a
second answer is wanted.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The new text. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.set_subtitle("and its other name")
>>> circle.subtitle
'and its other name'
```

## FifthsCircle.flash_wrong

<div class="api-signature" markdown="1">

```python
def flash_wrong() -> None
```

{% endraw %}{% include api-source.html name="FifthsCircle.flash_wrong" line=857 %}{% raw %}

</div>

Flash the cell asked about in the red of a wrong answer, striped
as well so that it still shows on the red wedge.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.show_question(
...     "major", place=0, title="A minor"
... )
>>> circle.flash_wrong()
>>> circle._warning is not None
True
```

## FifthsCircle.lift_of

<div class="api-signature" markdown="1">

```python
def lift_of(
    ring: str,
    *,
    place: int,
) -> float
```

{% endraw %}{% include api-source.html name="FifthsCircle.lift_of" line=948 %}{% raw %}

</div>

Return how bright a cell is drawn, from 0 (quiet) to 1 (fully
lit).

The cell asked about is half lit, and brightens when it is
answered. The cell beside it on the other ring is a little
lit, to show the pair; in a Roman numeral question the six
chords of the key are lit instead.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ring` | `str` | "outer" or "inner". |
| `place` | `int` | The place clockwise from the top. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The brightness. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.show_question(
...     "major", place=0, title="A minor"
... )
>>> (
...     circle.lift_of("outer", place=0),
...     circle.lift_of("inner", place=0),
...     circle.lift_of("outer", place=5),
... )
(0.5, 0.3, 0.0)
>>> circle.reveal(animate=False)
>>> circle.lift_of("outer", place=0)
1.0
```

## FifthsCircle.geometry_of

<div class="api-signature" markdown="1">

```python
def geometry_of() -> tuple[QPointF, float]
```

{% endraw %}{% include api-source.html name="FifthsCircle.geometry_of" line=999 %}{% raw %}

</div>

Return where the circle is drawn: its middle and its radius.

The circle fits the widget as a square in the middle of it, but
no larger than `MAX_RADIUS`.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of QPointF and float` | The center and the radius, in pixels. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.resize(400, 300)
>>> middle, radius = circle.geometry_of()
>>> middle.toTuple(), radius < 150
((200.0, 150.0), True)
>>> circle.resize(2400, 2000)
>>> circle.geometry_of()[1] == MAX_RADIUS
True
```

## FifthsCircle.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="FifthsCircle.paintEvent" line=1028 %}{% raw %}

</div>

Draw the two rings, the names, the question and the disc in the
middle.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole circle is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.resize(400, 400)
>>> circle.show_question(
...     "major", place=0, title="A minor"
... )
>>> circle.grab().isNull()
False
```
{% endraw %}
