---
title: MeterStaff
parent: alto.ui.meter_staff
api_module: alto.ui.meter_staff
package: alto.ui
permalink: /api/alto.ui.meter_staff/class-meterstaff/
---
{% raw %}
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

## MeterStaff.show_score

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

| Parameter | Type | Description |
| --- | --- | --- |
| `values` | `tuple of str` | Note values and rests in playback order. |
| `meter` | `tuple of int` | Numerator and denominator of the time signature. |
| `counts` | `tuple of str` | Optional spoken labels for each onset. |
| `bar_line` | `str` | Single or double bar line to emphasize in the glossary. |
| `show_signature` | `bool` | Draw and announce the time signature. |

## MeterStaff.set_counts_visible

<div class="api-signature" markdown="1">

```python
def set_counts_visible(visible: bool) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.set_counts_visible" line=418 %}{% raw %}

</div>

Show or hide the counts below the notes.

## MeterStaff.highlight_column

<div class="api-signature" markdown="1">

```python
def highlight_column(column: int | None) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.highlight_column" line=424 %}{% raw %}

</div>

Highlight the symbols that share a sounding onset.

## MeterStaff.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="MeterStaff.sizeHint" line=429 %}{% raw %}

</div>

Prefer one line at the natural rhythmic spacing.

**Returns**

| Type | Description |
| --- | --- |
| `QSize` | Preferred size for one line. |

## MeterStaff.minimumSizeHint

<div class="api-signature" markdown="1">

```python
def minimumSizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="MeterStaff.minimumSizeHint" line=461 %}{% raw %}

</div>

Keep dense subdivisions legible when measures wrap.

**Returns**

| Type | Description |
| --- | --- |
| `QSize` | Width for one bar at a readable scale and one row of music. |

## MeterStaff.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.resizeEvent" line=518 %}{% raw %}

</div>

Reflow whole measures at the available width.

## MeterStaff.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.paintEvent" line=607 %}{% raw %}

</div>

Draw the time signature and a line at each bar boundary.
{% endraw %}
