---
title: alto.ui.meter_staff
parent: api
package: alto.ui
permalink: /api/alto.ui.meter_staff/
---
{% raw %}
Staffless rhythm notation for lesson and glossary examples.

## MeterButton

<div class="api-signature" markdown="1">

```python
MeterButton(
    text: str,
    *,
    meter: tuple[int, int],
)
```

{% endraw %}{% include api-source.html name="MeterButton" line=110 %}{% raw %}

</div>

Bases: `QPushButton`

Draw a stacked time signature in a standard answer button.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MeterButton("12/8", meter=(12, 8)).accessibleName()
'12/8'
```

**Constructor**

Keep the plain signature as the text and accessible name.

**Parameters**

- `text` (*str*): The time signature written with a slash.
- `meter` (*tuple of int*): The numerator and denominator to engrave.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MeterButton("3/4", meter=(3, 4)).text()
'3/4'
```

### MeterButton.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterButton.paintEvent" line=140 %}{% raw %}

</div>

Draw the styled button chrome and engrave its label.

**Parameters**

- `event` (*QPaintEvent*): The paint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MeterButton("6/8", meter=(6, 8)).grab().isNull()
False
```

## MeterStaff

<div class="api-signature" markdown="1">

```python
MeterStaff()
```

{% endraw %}{% include api-source.html name="MeterStaff" line=217 %}{% raw %}

</div>

Bases: `QWidget`

Lay out rhythm on one baseline and wrap at bar lines.

**Constructor**

Create an empty rhythm example.

### MeterStaff.show_score

<div class="api-signature" markdown="1">

```python
def show_score(
    values: tuple[str, ...],
    *,
    meter: tuple[int, int] = (4, 4),
    counts: tuple[str, ...] = (),
    bar_line: str = '',
    show_signature: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.show_score" line=240 %}{% raw %}

</div>

Show the rhythm. Tilde-joined notes share a playback step.

**Parameters**

- `values` (*tuple of str*): Note values and rests in playback order.
- `meter` (*tuple of int*): Numerator and denominator of the time signature.
- `counts` (*tuple of str*): Optional spoken labels for each onset.
- `bar_line` (*str*): Single or double bar line to emphasize in the glossary.
- `show_signature` (*bool*): Draw and announce the time signature.

### MeterStaff.set_counts_visible

<div class="api-signature" markdown="1">

```python
def set_counts_visible(visible: bool) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.set_counts_visible" line=418 %}{% raw %}

</div>

Show or hide the counts below the notes.

### MeterStaff.highlight_column

<div class="api-signature" markdown="1">

```python
def highlight_column(column: int | None) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.highlight_column" line=424 %}{% raw %}

</div>

Highlight the symbols that share a sounding onset.

### MeterStaff.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="MeterStaff.sizeHint" line=429 %}{% raw %}

</div>

Prefer one line at the natural rhythmic spacing.

**Returns**

- *QSize*: Preferred size for one line.

### MeterStaff.minimumSizeHint

<div class="api-signature" markdown="1">

```python
def minimumSizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="MeterStaff.minimumSizeHint" line=461 %}{% raw %}

</div>

Keep dense subdivisions legible when measures wrap.

**Returns**

- *QSize*: Width for one bar at a readable scale and one row of music.

### MeterStaff.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.resizeEvent" line=518 %}{% raw %}

</div>

Reflow whole measures at the available width.

### MeterStaff.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.paintEvent" line=607 %}{% raw %}

</div>

Draw the time signature and a line at each bar boundary.

## BeatPlacementStaff

<div class="api-signature" markdown="1">

```python
BeatPlacementStaff()
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff" line=802 %}{% raw %}

</div>

Bases: `MeterStaff`

Let a learner toggle beat markers at eighth-note positions.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().marks
[]
```

**Constructor**

Start with no selected or graded positions.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().active_slot
0
```

### BeatPlacementStaff.reset

<div class="api-signature" markdown="1">

```python
def reset(
    values: tuple[str, ...],
    *,
    meter: tuple[int, int],
) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.reset" line=834 %}{% raw %}

</div>

Replace the score and clear the learner's marks.

**Parameters**

- `values` (*tuple of str*): The rhythm to engrave.
- `meter` (*tuple of int*): The time signature.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = BeatPlacementStaff()
>>> staff.reset(("quarter",) * 4, meter=(2, 4))
>>> staff.slots_per_bar
4
```

### BeatPlacementStaff.slots_per_bar

<div class="api-signature" markdown="1">

```python
@property
def slots_per_bar() -> int
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.slots_per_bar" line=864 %}{% raw %}

</div>

Count eighth-note positions per measure.

**Returns**

- *int*: The number of subdivisions selectable in each measure.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().slots_per_bar
8
```

### BeatPlacementStaff.beat_numbers

<div class="api-signature" markdown="1">

```python
def beat_numbers() -> dict[int, int]
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.beat_numbers" line=897 %}{% raw %}

</div>

Return beat numbers in reading order within each measure.

**Returns**

- *dict of int to int*: The beat number shown at each selected eighth-note position.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = BeatPlacementStaff()
>>> staff.marks = [10, 4, 8, 0]
>>> staff.beat_numbers()
{0: 1, 4: 2, 8: 1, 10: 2}
```

### BeatPlacementStaff.position

<div class="api-signature" markdown="1">

```python
def position(slot: int) -> QPointF
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.position" line=922 %}{% raw %}

</div>

Locate a selectable position below its corresponding rhythm.

**Parameters**

- `slot` (*int*): Zero-based eighth-note position across the score.

**Returns**

- *QPointF*: The center of the marker.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().position(0).y() > 0
True
```

### BeatPlacementStaff.undo

<div class="api-signature" markdown="1">

```python
def undo() -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.undo" line=992 %}{% raw %}

</div>

Remove the most recently added beat marker.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = BeatPlacementStaff()
>>> staff._toggle()
>>> staff.undo()
>>> staff.marks
[]
```

### BeatPlacementStaff.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.mousePressEvent" line=1008 %}{% raw %}

</div>

Toggle the nearest subdivision in the clicked measure.

**Parameters**

- `event` (*QMouseEvent*): The click in local coordinates.

**Examples**

```text
Tested with clicks on notes and beneath sustained notes.
```

### BeatPlacementStaff.keyPressEvent

<div class="api-signature" markdown="1">

```python
def keyPressEvent(event: QKeyEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.keyPressEvent" line=1040 %}{% raw %}

</div>

Move the active position with arrows and toggle it with Space.

**Parameters**

- `event` (*QKeyEvent*): The key pressed while the rhythm has focus.

**Examples**

```text
Keyboard input reaches the same subdivisions as a click.
```

### BeatPlacementStaff.focusInEvent

<div class="api-signature" markdown="1">

```python
def focusInEvent(event: QFocusEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.focusInEvent" line=1076 %}{% raw %}

</div>

Repaint the keyboard cursor when the rhythm receives focus.

**Parameters**

- `event` (*QFocusEvent*): The focus change.

**Examples**

```text
The focused score outlines the current selectable position.
```

### BeatPlacementStaff.focusOutEvent

<div class="api-signature" markdown="1">

```python
def focusOutEvent(event: QFocusEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.focusOutEvent" line=1092 %}{% raw %}

</div>

Hide the keyboard cursor when focus leaves the rhythm.

**Parameters**

- `event` (*QFocusEvent*): The focus change.

**Examples**

```text
Placed beats remain visible when focus moves to Answer.
```

### BeatPlacementStaff.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.paintEvent" line=1108 %}{% raw %}

</div>

Draw the subdivision blanks, beat numbers, and keyboard focus.

**Parameters**

- `event` (*QPaintEvent*): The paint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().grab().isNull()
False
```
{% endraw %}
