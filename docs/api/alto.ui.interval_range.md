---
title: alto.ui.interval_range
parent: api
package: alto.ui
order: 38
permalink: /api/alto.ui.interval_range/
---
{% raw %}
A two-handle slider for selecting interval distances without changing the keyboard range.

**Examples**

```pycon
>>> slider = IntervalRangeSlider()
>>> slider.set_range(3, high=12, maximum=24)
>>> slider.low, slider.high
(3, 12)
```

## IntervalRangeSlider

```python
IntervalRangeSlider(parent: QWidget | None = None)
```

Bases: `QWidget`

A draggable interval range with keyboard controls for either endpoint.

**Attributes**

- `edited` (*Signal*): Emits the selected lower and upper distances in half steps.
- `low, high` (*int*): The selected distances, inclusive.
- `maximum` (*int*): The largest available interval distance.
- `active` (*bool*): Whether the current selection contains any intervals.

**Examples**

```pycon
>>> slider = IntervalRangeSlider()
>>> slider.low, slider.high, slider.maximum
(1, 12, 24)
```

**Constructor**

Create the slider with a one-octave selection.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the slider.

**Constructor examples**

```pycon
>>> IntervalRangeSlider().height()
36
```

### IntervalRangeSlider.set_range

```python
def set_range(
    low: int,
    *,
    high: int,
    maximum: int,
    active: bool = True,
) -> None
```

Synchronize the slider without emitting an edit.

**Parameters**

- `low` (*int*): The lowest selected interval distance.
- `high` (*int*): The highest selected interval distance. Keyword-only.
- `maximum` (*int*): The largest available distance. Keyword-only.
- `active` (*bool, default True*): Whether any intervals are selected. Keyword-only.

**Examples**

```pycon
>>> slider = IntervalRangeSlider()
>>> slider.set_range(3, high=7, maximum=12)
>>> slider.low, slider.high
(3, 7)
```

### IntervalRangeSlider.move_endpoint

```python
def move_endpoint(
    which: str,
    *,
    delta: int,
) -> None
```

Move an endpoint by a number of half-step distances.

**Parameters**

- `which` (*str*): The endpoint, "low" or "high".
- `delta` (*int*): The number of interval distances to move. Keyword-only.

**Examples**

```pycon
>>> slider = IntervalRangeSlider()
>>> slider.move_endpoint("low", delta=2)
>>> slider.low
3
```

### IntervalRangeSlider.paintEvent

```python
def paintEvent(event: QPaintEvent) -> None
```

Draw the track, selected span, and both handles.

**Parameters**

- `event` (*QPaintEvent*): The repaint request.

**Examples**

```pycon
>>> IntervalRangeSlider().grab().isNull()
False
```

### IntervalRangeSlider.mousePressEvent

```python
def mousePressEvent(event: QMouseEvent) -> None
```

Choose the nearest handle and start dragging it.

**Parameters**

- `event` (*QMouseEvent*): The mouse press.

**Examples**

```pycon
>>> IntervalRangeSlider()._dragging
False
```

### IntervalRangeSlider.mouseMoveEvent

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

Move the active handle while dragging.

**Parameters**

- `event` (*QMouseEvent*): The pointer movement.

**Examples**

```pycon
>>> IntervalRangeSlider().maximum
24
```

### IntervalRangeSlider.mouseReleaseEvent

```python
def mouseReleaseEvent(event: QMouseEvent) -> None
```

Finish dragging a handle.

**Parameters**

- `event` (*QMouseEvent*): The mouse release.

**Examples**

```pycon
>>> IntervalRangeSlider()._dragging
False
```

### IntervalRangeSlider.keyPressEvent

```python
def keyPressEvent(event: QKeyEvent) -> None
```

Adjust the active endpoint with arrow keys, Home, or End.

**Parameters**

- `event` (*QKeyEvent*): The keyboard input. Up selects the upper handle and Down the lower handle.

**Examples**

```pycon
>>> IntervalRangeSlider().focusPolicy() == Qt.FocusPolicy.StrongFocus
True
```
{% endraw %}
