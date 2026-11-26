---
title: LineChart
parent: alto.ui.charts
api_module: alto.ui.charts
package: alto.ui
permalink: /api/alto.ui.charts/class-linechart/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
LineChart(
    title: str,
    *,
    fmt: Callable[[float], str],
    fixed_top: float | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="LineChart" line=1255 %}{% raw %}

</div>

Bases: `_Chart`

A value per period joined by a line.

Periods with no answers leave a gap rather than a zero.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `fmt` | `callable` | Turns a value into its label, for the axis and the tooltip. |
| `fixed_top` | `float or None` | The value at the top of the plot; the largest value, rounded up, if None. |
| `values` | `list of float or None` | The value of each period, or None for a gap. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = LineChart(
...     "Right on the first try",
...     fmt=lambda v: f"{v:.0f}%",
...     fixed_top=100,
... )
>>> chart.set_data(
...     ["Mon", "Tue", "Wed"],
...     values=[40.0, None, 80.0],
... )
>>> chart.values
[40.0, None, 80.0]
```

**Constructor**

Create an empty chart.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `title` | `str` | Drawn at the top left. |
| `fmt` | `callable` | Turns a value into its label. Keyword-only. |
| `fixed_top` | `float or None, default None` | The value at the top of the plot (such as 100 for a percentage); the largest value, rounded up, if None. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the chart. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> LineChart(
...     "Speed", fmt=lambda v: f"{v:.1f} s"
... ).fixed_top is None
True
```

## LineChart.set_data

<div class="api-signature" markdown="1">

```python
def set_data(
    labels: Sequence[str],
    *,
    values: Sequence[float | None],
) -> None
```

{% endraw %}{% include api-source.html name="LineChart.set_data" line=1321 %}{% raw %}

</div>

Show a value for each period.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `labels` | `sequence of str` | The label of each period. |
| `values` | `sequence of float or None` | The value of each period; None leaves a gap. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = LineChart(
...     "Speed", fmt=lambda v: f"{v:.1f} s"
... )
>>> chart.set_data(
...     ["a", "b"], values=[2.5, None]
... )
>>> chart.labels
['a', 'b']
```

## LineChart.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="LineChart.paintEvent" line=1399 %}{% raw %}

</div>

Draw the axes, the line (one run at a time, so gaps show) and a
dot for each value.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = LineChart(
...     "Speed", fmt=lambda v: f"{v:.1f} s"
... )
>>> chart.resize(400, 300)
>>> chart.set_data(
...     ["a", "b", "c"], values=[2.0, None, 3.0]
... )
>>> chart.grab().isNull()
False
```

## LineChart.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="LineChart.mouseMoveEvent" line=1526 %}{% raw %}

</div>

Say what the value under the pointer is in a tooltip.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> from PySide6.QtGui import QMouseEvent
>>> chart = LineChart(
...     "Speed", fmt=lambda v: f"{v:.1f} s"
... )
>>> chart.resize(400, 300)
>>> chart.set_data(
...     ["a", "b"], values=[2.0, 3.0]
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
