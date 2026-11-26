---
title: StackedBarChart
parent: alto.ui.charts
api_module: alto.ui.charts
package: alto.ui
permalink: /api/alto.ui.charts/class-stackedbarchart/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
StackedBarChart(
    title: str,
    *,
    header_control: QWidget | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="StackedBarChart" line=944 %}{% raw %}

</div>

Bases: `_Chart`

Questions per period, the first-try right ones in green with the
missed ones stacked above in red.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `right` | `list of int` | Questions right on the first try, per period. |
| `wrong` | `list of int` | Questions missed, per period. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = StackedBarChart(
...     "Questions answered per day"
... )
>>> chart.set_data(
...     ["Mon", "Tue", "Wed"],
...     right=[3, 0, 5],
...     wrong=[1, 2, 0],
... )
>>> chart.labels
['Mon', 'Tue', 'Wed']
```

**Constructor**

Create an empty chart.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `title` | `str` | Drawn at the top left. |
| `header_control` | `QWidget or None, default None` | Optional control at the right edge of the chart title row. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the chart. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StackedBarChart("Questions").right
[]
```

## StackedBarChart.set_data

<div class="api-signature" markdown="1">

```python
def set_data(
    labels: Sequence[str],
    *,
    right: Sequence[int],
    wrong: Sequence[int],
) -> None
```

{% endraw %}{% include api-source.html name="StackedBarChart.set_data" line=1004 %}{% raw %}

</div>

Show a count of right and missed questions for each period.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `labels` | `sequence of str` | The label of each period. |
| `right` | `sequence of int` | Questions right on the first try in each period. Keyword-only. |
| `wrong` | `sequence of int` | Questions missed in each period. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = StackedBarChart("Questions")
>>> chart.set_data(
...     ["a", "b"], right=[2, 0], wrong=[0, 4]
... )
>>> chart.right, chart.wrong
([2, 0], [0, 4])
```

## StackedBarChart.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="StackedBarChart.paintEvent" line=1088 %}{% raw %}

</div>

Draw the axes and a bar for each period, or a message when no
questions were answered.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = StackedBarChart("Questions")
>>> chart.resize(400, 300)
>>> chart.set_data(
...     ["a", "b"], right=[3, 1], wrong=[1, 0]
... )
>>> chart.grab().isNull()
False
```

## StackedBarChart.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="StackedBarChart.mouseMoveEvent" line=1200 %}{% raw %}

</div>

Explain the bar under the pointer in a tooltip.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> from PySide6.QtGui import QMouseEvent
>>> chart = StackedBarChart("Questions")
>>> chart.resize(400, 300)
>>> chart.set_data(
...     ["Mon", "Tue"],
...     right=[3, 1],
...     wrong=[1, 0],
... )
>>> point = QPointF(
...     chart._centers()[0],
...     chart._plot().center().y(),
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
