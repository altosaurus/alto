---
title: BeatPlacementStaff
parent: alto.ui.meter_staff
api_module: alto.ui.meter_staff
package: alto.ui
permalink: /api/alto.ui.meter_staff/class-beatplacementstaff/
---
{% raw %}
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

## BeatPlacementStaff.reset

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

| Parameter | Type | Description |
| --- | --- | --- |
| `values` | `tuple of str` | The rhythm to engrave. |
| `meter` | `tuple of int` | The time signature. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = BeatPlacementStaff()
>>> staff.reset(("quarter",) * 4, meter=(2, 4))
>>> staff.slots_per_bar
4
```

## BeatPlacementStaff.slots_per_bar

<div class="api-signature" markdown="1">

```python
@property
def slots_per_bar() -> int
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.slots_per_bar" line=864 %}{% raw %}

</div>

Count eighth-note positions per measure.

**Returns**

| Type | Description |
| --- | --- |
| `int` | The number of subdivisions selectable in each measure. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().slots_per_bar
8
```

## BeatPlacementStaff.beat_numbers

<div class="api-signature" markdown="1">

```python
def beat_numbers() -> dict[int, int]
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.beat_numbers" line=897 %}{% raw %}

</div>

Return beat numbers in reading order within each measure.

**Returns**

| Type | Description |
| --- | --- |
| `dict of int to int` | The beat number shown at each selected eighth-note position. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = BeatPlacementStaff()
>>> staff.marks = [10, 4, 8, 0]
>>> staff.beat_numbers()
{0: 1, 4: 2, 8: 1, 10: 2}
```

## BeatPlacementStaff.position

<div class="api-signature" markdown="1">

```python
def position(slot: int) -> QPointF
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.position" line=922 %}{% raw %}

</div>

Locate a selectable position below its corresponding rhythm.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `slot` | `int` | Zero-based eighth-note position across the score. |

**Returns**

| Type | Description |
| --- | --- |
| `QPointF` | The center of the marker. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().position(0).y() > 0
True
```

## BeatPlacementStaff.undo

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

## BeatPlacementStaff.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.mousePressEvent" line=1008 %}{% raw %}

</div>

Toggle the nearest subdivision in the clicked measure.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The click in local coordinates. |

**Examples**

```text
Tested with clicks on notes and beneath sustained notes.
```

## BeatPlacementStaff.keyPressEvent

<div class="api-signature" markdown="1">

```python
def keyPressEvent(event: QKeyEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.keyPressEvent" line=1040 %}{% raw %}

</div>

Move the active position with arrows and toggle it with Space.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QKeyEvent` | The key pressed while the rhythm has focus. |

**Examples**

```text
Keyboard input reaches the same subdivisions as a click.
```

## BeatPlacementStaff.focusInEvent

<div class="api-signature" markdown="1">

```python
def focusInEvent(event: QFocusEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.focusInEvent" line=1076 %}{% raw %}

</div>

Repaint the keyboard cursor when the rhythm receives focus.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QFocusEvent` | The focus change. |

**Examples**

```text
The focused score outlines the current selectable position.
```

## BeatPlacementStaff.focusOutEvent

<div class="api-signature" markdown="1">

```python
def focusOutEvent(event: QFocusEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.focusOutEvent" line=1092 %}{% raw %}

</div>

Hide the keyboard cursor when focus leaves the rhythm.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QFocusEvent` | The focus change. |

**Examples**

```text
Placed beats remain visible when focus moves to Answer.
```

## BeatPlacementStaff.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="BeatPlacementStaff.paintEvent" line=1108 %}{% raw %}

</div>

Draw the subdivision blanks, beat numbers, and keyboard focus.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatPlacementStaff().grab().isNull()
False
```
{% endraw %}
