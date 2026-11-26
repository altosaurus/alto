---
title: HBarChart
parent: alto.ui.charts
api_module: alto.ui.charts
package: alto.ui
permalink: /api/alto.ui.charts/class-hbarchart/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
HBarChart(
    title: str,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="HBarChart" line=1572 %}{% raw %}

</div>

Bases: `_Chart`

One bar per name, on a fixed 0-100 scale, each with its value at the
end.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `ROW` | `int` | The height of each bar's row, in pixels. |
| `rows` | `list of tuple of (str, float, str)` | For each bar, its name, its value from 0 to 100 and the text shown at its end. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HBarChart(
...     "Right on the first try, by exercise"
... )
>>> chart.set_data(
...     [
...         ("Intervals", 77.0, "77%  ·  52 q"),
...         ("Chords", 88.0, "88%  ·  48 q"),
...     ]
... )
>>> len(chart.rows)
2
```

**Constructor**

Create an empty chart.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `title` | `str` | Drawn at the top left. |
| `parent` | `QWidget or None, default None` | The widget that owns the chart. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HBarChart("By exercise").rows
[]
```

## HBarChart.set_data

<div class="api-signature" markdown="1">

```python
def set_data(rows: Sequence[tuple[str, float, str]]) -> None
```

{% endraw %}{% include api-source.html name="HBarChart.set_data" line=1626 %}{% raw %}

</div>

Show a bar for each name, and make the chart tall enough for
them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rows` | `sequence of tuple of (str, float, str)` | Each bar's name, its value from 0 to 100, and the text shown at the end of the bar. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HBarChart("By exercise")
>>> chart.set_data(
...     [
...         (f"Exercise {i}", 50.0, "50%")
...         for i in range(10)
...     ]
... )
>>> chart.minimumHeight()
306
```

## HBarChart.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="HBarChart.paintEvent" line=1655 %}{% raw %}

</div>

Draw a bar with its name and value for each row, or a message
when there are none.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> chart = HBarChart("By exercise")
>>> chart.resize(400, 300)
>>> chart.set_data([("Intervals", 77.0, "77%")])
>>> chart.grab().isNull()
False
```

## HBarChart.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="HBarChart.mouseMoveEvent" line=1782 %}{% raw %}

</div>

Highlight the row under the pointer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> chart = HBarChart("By exercise")
>>> chart.set_data([("A", 50.0, "50%")])
>>> point = QPointF(
...     10, chart.TOP + chart.ROW / 2
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
>>> chart.hovered
0
```
{% endraw %}
