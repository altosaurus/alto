---
title: StaffWidget
parent: alto.ui.staff
api_module: alto.ui.staff
package: alto.ui
permalink: /api/alto.ui.staff/class-staffwidget/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
StaffWidget(
    parent: QWidget | None = None,
    *,
    gap: float = 16.0,
    side: float = 20.0,
    note_offset: float = 100.0,
    margin: float = 8.0,
    compact: bool = False,
    max_step: float | None = None,
    lesson_layout: bool = False,
)
```

{% endraw %}{% include api-source.html name="StaffWidget" line=530 %}{% raw %}

</div>

Bases: `QWidget`

A staff with notes, a clef, a key signature and, optionally, a
caption.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `GAP` | `float` | The distance between staff lines, in pixels. |
| `side` | `float` | The space at the left and right edges. |
| `note_offset` | `float` | Where the notes start, from the left edge. |
| `margin` | `float` | The space kept above and below the staff for ledger lines, in gaps. |
| `compact` | `bool` | Size the widget to fit instead of the 220 px default. |
| `max_step` | `float or None` | The most width each column of notes may take. |
| `clef` | `str` | The clef being drawn ("treble", "bass", "alto", "tenor", "soprano", "mezzo", "baritone" or "grand"). |
| `columns` | `list of list of Note` | The notes drawn; each inner list is one chord or note. |
| `interval_voices` | `bool` | Draw harmonic interval endpoints with their written duration and opposing stems. |
| `note_color` | `QColor or None` | Feedback color for the highlighted notation component, or for the notes in other exercises. |
| `column_colors` | `dict of int to QColor` | The color of particular columns of notes, by position from 0; they are drawn in these instead of `note_color`. |
| `wedges` | `list of str` | The step between each column and the next, such as "W" or "H", drawn as two lines rising from the notes to a point above them, with the letter over the point; "" for none there. |
| `wedge_colors` | `dict of int to QColor` | The color of particular wedges, by position from 0. The others take the color of the note on their right, or `note_color`. |
| `notation_style` | `NotationStyle or None` | A style to use instead of the one chosen in the settings. |
| `clef_hidden` | `bool` | Draw the staff without its clef, for a clef the learner places. |
| `key` | `int` | The key signature drawn: sharps if positive, flats if negative. |
| `key_room` | `int` | How many sharps or flats' worth of room to keep for the signature at least, so that a capped staff does not change width as the signature does. 0 keeps room only for the one drawn. |
| `value` | `str` | The note value drawn. |
| `caption` | `str` | Text written under the staff, inside the paper. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget()
>>> staff.show_notes(
...     [
...         [Note.parse("E4")],
...         [Note.parse("G4")],
...     ],
...     clef="treble",
... )
>>> len(staff.columns)
2
```

**Constructor**

Create an empty treble staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the staff. |
| `gap` | `float, default 16.0` | The distance between staff lines, in pixels. Keyword-only. |
| `side` | `float, default 20.0` | The space at the left and right edges. Keyword-only. |
| `note_offset` | `float, default 100.0` | Where the notes start, from the left edge. Keyword-only. |
| `margin` | `float, default 8.0` | The space kept above and below the staff for ledger lines, in gaps. Keyword-only. |
| `compact` | `bool, default False` | Size the widget to fit instead of the 220 px default. Keyword-only. |
| `max_step` | `float or None, default None` | The most width each column of notes may take: the staff then stops growing once its notes would be spread wider than that, so a few notes stay easy to read in a wide window. Keyword-only. |
| `lesson_layout` | `bool, default False` | Space the excerpt by its printed symbols and wrap at note or chord boundaries. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StaffWidget(gap=8.0, compact=True).GAP
8.0
```

## StaffWidget.show_notes

<div class="api-signature" markdown="1">

```python
def show_notes(
    columns: list[list[Note]],
    *,
    clef: str = 'treble',
    key: int = 0,
    value: str = 'whole',
    caption: str = '',
    notation_target: tuple[str, int] | None = None,
    locate_notation: bool = False,
    notation_excerpt: str | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="StaffWidget.show_notes" line=720 %}{% raw %}

</div>

Show some notes, with a clef and a key signature.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `columns` | `list of list of Note` | The notes: each inner list is one note or chord, drawn left to right. |
| `clef` | `str, default "treble"` | The clef, or "grand" for a grand staff. Keyword-only. |
| `key` | `int, default 0` | The key signature: that many sharps if positive, flats if negative. Keyword-only. |
| `value` | `str, default "whole"` | The written duration for single notes and interval voices. Keyword-only. |
| `caption` | `str, default ""` | Text to write under the staff. Keyword-only. |
| `notation_target` | `tuple of (str, int) or None` | Part and position to highlight in a notation question. Keyword-only. |
| `notation_excerpt` | `str or None` | Versioned score to show for a repertoire question. Keyword-only. |
| `locate_notation` | `bool, default False` | Render the target in ordinary ink for the learner to find. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget()
>>> staff.show_notes(
...     [[Note.parse("C4")]],
...     clef="bass",
...     key=-1,
...     value="quarter",
...     caption="_ Major",
... )
>>> (
...     staff.clef,
...     staff.key,
...     staff.value,
...     staff.caption,
... )
('bass', -1, 'quarter', '_ Major')
```

## StaffWidget.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="StaffWidget.sizeHint" line=870 %}{% raw %}

</div>

Return the size the staff would like.

A capped staff asks for its full capped width, so a layout that
centers it gives it that much.

**Returns**

| Type | Description |
| --- | --- |
| `QSize` | The capped width and minimum height for a lesson or a staff with a `max_step`. Other staves use Qt's default. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget(max_step=120.0)
>>> staff.show_notes([[Note.parse("C4")]])
>>> staff.sizeHint().width()
500
```

## StaffWidget.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="StaffWidget.resizeEvent" line=1133 %}{% raw %}

</div>

Reflow a lesson excerpt when its available width changes.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QResizeEvent` | Previous and current widget size. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget(lesson_layout=True)
>>> staff.resize(300, staff.height())
```

## StaffWidget.highlight_column

<div class="api-signature" markdown="1">

```python
def highlight_column(index: int | None) -> None
```

{% endraw %}{% include api-source.html name="StaffWidget.highlight_column" line=1194 %}{% raw %}

</div>

Highlight a sounding note or chord, preserving the staff's other
markings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `index` | `int or None` | The sounding column, or None to restore its usual ink. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget()
>>> staff.highlight_column(0)
>>> staff.playback_column
0
```

## StaffWidget.set_note_color

<div class="api-signature" markdown="1">

```python
def set_note_color(color: QColor | None) -> None
```

{% endraw %}{% include api-source.html name="StaffWidget.set_note_color" line=1214 %}{% raw %}

</div>

Apply feedback to the highlighted notation component or to the
notes when there is no component target.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `color` | `QColor or None` | The feedback color. None restores the usual ink and highlight colors. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget()
>>> staff.set_note_color(QColor("#2e7d32"))
>>> # noinspection PyUnresolvedReferences
>>> staff.note_color.name()
'#2e7d32'
>>> staff.set_note_color(None)
>>> staff.note_color is None
True
```

## StaffWidget.staff_bottoms

<div class="api-signature" markdown="1">

```python
def staff_bottoms() -> dict[str, float]
```

{% endraw %}{% include api-source.html name="StaffWidget.staff_bottoms" line=1239 %}{% raw %}

</div>

Return where each staff is drawn.

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to float` | Clef name to the y position of that staff's bottom line, in pixels. A grand staff has a "treble" and a "bass". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget()
>>> staff.resize(400, 400)
>>> staff.staff_bottoms()
{'treble': 232.0}
```

## StaffWidget.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="StaffWidget.paintEvent" line=1267 %}{% raw %}

</div>

Draw the paper, the staff lines, the clef, the key signature,
the notes and the caption.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffWidget()
>>> staff.resize(400, 400)
>>> staff.show_notes(
...     [[Note.parse("C4")]], clef="treble"
... )
>>> staff.grab().toImage().pixelColor(
...     200, 5
... ).name()  # the white paper
'#ffffff'
```

## StaffWidget.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="StaffWidget.mouseMoveEvent" line=1325 %}{% raw %}

</div>

Preview the component under the pointer in Click on Staff
questions.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The pointer position relative to the score. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StaffWidget().hasMouseTracking()
False
```

## StaffWidget.leaveEvent

<div class="api-signature" markdown="1">

```python
def leaveEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="StaffWidget.leaveEvent" line=1345 %}{% raw %}

</div>

Clear the component preview when the pointer leaves the music.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QEvent` | The pointer leaving the staff. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StaffWidget().leaveEvent(
...     QEvent(QEvent.Type.Leave)
... )
```

## StaffWidget.hits_notation

<div class="api-signature" markdown="1">

```python
def hits_notation(point: QPoint) -> bool
```

{% endraw %}{% include api-source.html name="StaffWidget.hits_notation" line=1365 %}{% raw %}

</div>

Check for target ink within four logical pixels of a click on
the score.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `point` | `QPoint` | Click position relative to the staff widget. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | Whether the clicked neighborhood contains the selected marking. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StaffWidget().hits_notation(QPoint(0, 0))
False
```
{% endraw %}
