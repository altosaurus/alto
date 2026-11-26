---
title: HeatmapChart
parent: alto.ui.charts
api_module: alto.ui.charts
package: alto.ui
permalink: /api/alto.ui.charts/class-heatmapchart/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
HeatmapChart(
    title: str,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="HeatmapChart" line=1815 %}{% raw %}

</div>

Bases: `_Chart`

A calendar of reviews: a column per week (Monday to Sunday), a
square per day, darker the more questions.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `LEVELS` | `int` | The number of shades above "none". |
| `counts` | `dict of date to int` | Questions answered on each day that had any. |
| `today` | `date` | The last day shown. |
| `weeks` | `int` | How many weeks are shown, counting this one. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HeatmapChart("Reviews")
>>> chart.set_data(
...     {date(2026, 11, 13): 12},
...     today=date(2026, 11, 13),
... )
>>> chart.counts
{datetime.date(2026, 11, 13): 12}
```

**Constructor**

Create an empty calendar for the last 53 weeks.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `title` | `str` | Drawn at the top left. |
| `parent` | `QWidget or None, default None` | The widget that owns the chart. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HeatmapChart("Reviews").weeks
53
```

## HeatmapChart.set_data

<div class="api-signature" markdown="1">

```python
def set_data(
    counts: dict[date, int],
    *,
    today: date,
    weeks: int = 53,
) -> None
```

{% endraw %}{% include api-source.html name="HeatmapChart.set_data" line=1924 %}{% raw %}

</div>

Show how many questions were answered on each day.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `counts` | `dict of date to int` | Questions answered on each day that had any. |
| `today` | `date` | The last day to show. Keyword-only. |
| `weeks` | `int, default 53` | How many weeks to show, counting this one. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HeatmapChart("Reviews")
>>> chart.set_data(
...     {}, today=date(2026, 11, 13), weeks=26
... )
>>> chart.weeks
26
```

## HeatmapChart.first_day

<div class="api-signature" markdown="1">

```python
def first_day() -> date
```

{% endraw %}{% include api-source.html name="HeatmapChart.first_day" line=1968 %}{% raw %}

</div>

Return the first day shown: the Monday that starts the first
week.

**Returns**

| Type | Description |
| --- | --- |
| `date` | A Monday. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HeatmapChart("Reviews")
>>> chart.set_data({}, today=date(2026, 11, 13))
>>> (
...     chart.first_day(),
...     chart.first_day().weekday(),
... )
(datetime.date(2025, 11, 10), 0)
```

## HeatmapChart.level

<div class="api-signature" markdown="1">

```python
def level(count: int) -> int
```

{% endraw %}{% include api-source.html name="HeatmapChart.level" line=1992 %}{% raw %}

</div>

Return how dark a day's square is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `count` | `int` | Questions answered that day. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | 0 for no questions, otherwise 1 to `LEVELS` by how the day compares with the busiest. The scale is in quarters of the 90th-percentile day, so one huge day does not flatten everything else. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HeatmapChart("Reviews")
>>> chart.set_data(
...     {
...         date(2026, 11, 13): 40,
...         date(2026, 11, 12): 20,
...         date(2026, 11, 11): 1,
...     },
...     today=date(2026, 11, 13),
... )
>>> (
...     chart.level(0),
...     chart.level(1),
...     chart.level(40),
... )
(0, 1, 4)
```

## HeatmapChart.day_at

<div class="api-signature" markdown="1">

```python
def day_at(pos: QPointF) -> date | None
```

{% endraw %}{% include api-source.html name="HeatmapChart.day_at" line=2155 %}{% raw %}

</div>

Return the day whose square is under a point.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `pos` | `QPointF` | The position in the widget. |

**Returns**

| Type | Description |
| --- | --- |
| `date or None` | The day, or None if the point is outside the calendar or on a day that has not happened yet. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HeatmapChart("Reviews")
>>> chart.resize(760, 190)
>>> chart.set_data({}, today=date(2026, 11, 13))
>>> cell_, (x0_, y0_) = (
...     chart._cell(),
...     chart._origin(),
... )
>>> chart.day_at(
...     QPointF(
...         x0_ + 52.5 * cell_,
...         y0_ + 4.5 * cell_,
...     )
... )  # the last column, Friday
datetime.date(2026, 11, 13)
>>> chart.day_at(
...     QPointF(
...         x0_ + 52.5 * cell_,
...         y0_ + 6.5 * cell_,
...     )
... ) is None  # Sunday: not yet
True
```

## HeatmapChart.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="HeatmapChart.paintEvent" line=2204 %}{% raw %}

</div>

Draw the month and weekday labels, a square for each day, and
the Less-More legend.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HeatmapChart("Reviews")
>>> chart.resize(760, 190)
>>> chart.set_data(
...     {date(2026, 11, 13): 5},
...     today=date(2026, 11, 13),
... )
>>> chart.grab().isNull()
False
```

## HeatmapChart.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="HeatmapChart.mouseMoveEvent" line=2384 %}{% raw %}

</div>

Say how many questions were answered on the day under the
pointer, in a tooltip.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> from PySide6.QtGui import QMouseEvent
>>> chart = HeatmapChart("Reviews")
>>> chart.resize(760, 190)
>>> chart.set_data(
...     {date(2026, 11, 13): 3},
...     today=date(2026, 11, 13),
... )
>>> cell, (x0, y0) = (
...     chart._cell(),
...     chart._origin(),
... )
>>> point = QPointF(
...     x0 + 52.5 * cell, y0 + 4.5 * cell
... )
>>> chart.mouseMoveEvent(
...     QMouseEvent(
...         QEvent.Type.MouseMove,
...         point,
...         point,
...         Qt.MouseButton.NoButton,
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
```
{% endraw %}
