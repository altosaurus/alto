---
title: alto.ui.meter_staff
parent: api
package: alto.ui
permalink: /api/alto.ui.meter_staff/
---
{% raw %}
Staffless rhythm notation for lesson and glossary examples.

## MeterStaff

<div class="api-signature" markdown="1">

```python
MeterStaff()
```

{% endraw %}{% include api-source.html name="MeterStaff" line=36 %}{% raw %}

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
) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.show_score" line=52 %}{% raw %}

</div>

Show the rhythm. Tilde-joined notes share a playback step.

**Parameters**

- `values` (*tuple of str*): Note values and rests in playback order.
- `meter` (*tuple of int*): Numerator and denominator of the time signature.
- `counts` (*tuple of str*): Optional spoken labels for each onset.
- `bar_line` (*str*): Single or double bar line to emphasize in the glossary.

### MeterStaff.set_counts_visible

<div class="api-signature" markdown="1">

```python
def set_counts_visible(visible: bool) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.set_counts_visible" line=133 %}{% raw %}

</div>

Show or hide the counts below the notes.

### MeterStaff.highlight_column

<div class="api-signature" markdown="1">

```python
def highlight_column(column: int | None) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.highlight_column" line=139 %}{% raw %}

</div>

Highlight the symbols that share a sounding onset.

### MeterStaff.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="MeterStaff.sizeHint" line=144 %}{% raw %}

</div>

Prefer one line at the natural rhythmic spacing.

**Returns**

- *QSize*: Preferred size for one line.

### MeterStaff.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.resizeEvent" line=178 %}{% raw %}

</div>

Reflow whole measures at the available width.

### MeterStaff.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterStaff.paintEvent" line=197 %}{% raw %}

</div>

Draw the time signature and a line at each bar boundary.
{% endraw %}
