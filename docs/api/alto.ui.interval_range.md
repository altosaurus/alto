---
title: alto.ui.interval_range
parent: api
package: alto.ui
permalink: /api/alto.ui.interval_range/
---
{% raw %}
A two-handle slider for selecting interval distances without changing
the keyboard range.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> slider = IntervalRangeSlider()
>>> slider.set_range(3, high=12, maximum=24)
>>> slider.low, slider.high
(3, 12)
```

## IntervalRangeSlider

<div class="api-signature" markdown="1">

```python
IntervalRangeSlider(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider" line=36 %}{% raw %}

</div>

Bases: `QWidget`

A draggable interval range with keyboard controls for either
endpoint.

**Attributes**

- `edited` (*Signal*): Emits the selected lower and upper distances in half steps.
- `low, high` (*int*): The selected distances, inclusive.
- `minimum, maximum` (*int*): The smallest and largest available interval distances.
- `active` (*bool*): Whether the current selection contains any intervals.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> slider = IntervalRangeSlider()
>>> slider.low, slider.high, slider.maximum
(1, 12, 24)
```

**Constructor**

Create the slider with a one-octave selection.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the slider.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalRangeSlider().height()
36
```

### IntervalRangeSlider.set_range

<div class="api-signature" markdown="1">

```python
def set_range(
    low: int,
    *,
    high: int,
    maximum: int,
    minimum: int = 1,
    active: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider.set_range" line=97 %}{% raw %}

</div>

Synchronize the slider without emitting an edit.

**Parameters**

- `low` (*int*): The lowest selected interval distance.
- `high` (*int*): The highest selected interval distance. Keyword-only.
- `maximum` (*int*): The largest available distance. Keyword-only.
- `minimum` (*int, default 1*): The smallest available distance. Keyword-only.
- `active` (*bool, default True*): Whether any intervals are selected. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> slider = IntervalRangeSlider()
>>> slider.set_range(3, high=7, maximum=12)
>>> slider.low, slider.high
(3, 7)
```

### IntervalRangeSlider.move_endpoint

<div class="api-signature" markdown="1">

```python
def move_endpoint(
    which: str,
    *,
    delta: int,
) -> None
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider.move_endpoint" line=141 %}{% raw %}

</div>

Move an endpoint by a number of half-step distances.

**Parameters**

- `which` (*str*): The endpoint, "low" or "high".
- `delta` (*int*): The number of interval distances to move. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> slider = IntervalRangeSlider()
>>> slider.move_endpoint("low", delta=2)
>>> slider.low
3
```

### IntervalRangeSlider.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider.paintEvent" line=219 %}{% raw %}

</div>

Draw the track, selected span, and both handles.

**Parameters**

- `event` (*QPaintEvent*): The repaint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalRangeSlider().grab().isNull()
False
```

### IntervalRangeSlider.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider.mousePressEvent" line=276 %}{% raw %}

</div>

Choose the nearest handle and start dragging it.

**Parameters**

- `event` (*QMouseEvent*): The mouse press.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalRangeSlider()._dragging
False
```

### IntervalRangeSlider.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider.mouseMoveEvent" line=304 %}{% raw %}

</div>

Move the active handle while dragging.

**Parameters**

- `event` (*QMouseEvent*): The pointer movement.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalRangeSlider().maximum
24
```

### IntervalRangeSlider.mouseReleaseEvent

<div class="api-signature" markdown="1">

```python
def mouseReleaseEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider.mouseReleaseEvent" line=332 %}{% raw %}

</div>

Finish dragging a handle.

**Parameters**

- `event` (*QMouseEvent*): The mouse release.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalRangeSlider()._dragging
False
```

### IntervalRangeSlider.keyPressEvent

<div class="api-signature" markdown="1">

```python
def keyPressEvent(event: QKeyEvent) -> None
```

{% endraw %}{% include api-source.html name="IntervalRangeSlider.keyPressEvent" line=352 %}{% raw %}

</div>

Adjust the active endpoint with arrow keys, Home, or End.

**Parameters**

- `event` (*QKeyEvent*): The keyboard input. Up selects the upper handle and Down the lower handle.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     IntervalRangeSlider().focusPolicy()
...     == Qt.FocusPolicy.StrongFocus
... )
True
```
{% endraw %}
