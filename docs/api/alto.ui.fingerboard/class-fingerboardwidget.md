---
title: FingerboardWidget
parent: alto.ui.fingerboard
api_module: alto.ui.fingerboard
package: alto.ui
permalink: /api/alto.ui.fingerboard/class-fingerboardwidget/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
FingerboardWidget()
```

{% endraw %}{% include api-source.html name="FingerboardWidget" line=285 %}{% raw %}

</div>

Bases: `QWidget`

Draw the instrument and keep the teaching overlays on the same
scale.

**Constructor**

Create an empty fingerboard display.

## FingerboardWidget.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="FingerboardWidget.sizeHint" line=331 %}{% raw %}

</div>

Reserve space for the whole instrument.

**Returns**

| Type | Description |
| --- | --- |
| `QSize` | Preferred dimensions of the diagram. |

## FingerboardWidget.show_position

<div class="api-signature" markdown="1">

```python
def show_position(position: FingerboardPosition | PicturePosition | None) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.show_position" line=360 %}{% raw %}

</div>

Resolve the saved pack identity and clear the previous playback
highlight.

## FingerboardWidget.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.resizeEvent" line=494 %}{% raw %}

</div>

Fit the drawn keyboards to the new height.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QResizeEvent` | The resize that happened. |

## FingerboardWidget.set_pickable

<div class="api-signature" markdown="1">

```python
def set_pickable(pickable: bool) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.set_pickable" line=519 %}{% raw %}

</div>

Let a click on the picture be an answer, and say so with the
pointer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `pickable` | `bool` | True to emit `picked` for each click on the picture. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> board = FingerboardWidget()
>>> board.set_pickable(True)
>>> board.cursor().shape() == Qt.CursorShape.PointingHandCursor
True
```

## FingerboardWidget.show_target

<div class="api-signature" markdown="1">

```python
def show_target(point: tuple[float, float] | None) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.show_target" line=543 %}{% raw %}

</div>

Mark the right place on a picture that has no marker, or clear
the mark.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `point` | `tuple of float, or None` | The place in the picture's own pixels, or None to clear it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> board = FingerboardWidget()
>>> board.show_target((10.0, 20.0))
>>> board.show_target(None)
```

## FingerboardWidget.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.mousePressEvent" line=562 %}{% raw %}

</div>

Turn a click into a point on the picture when the picture is
being used for an answer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The click. |

## FingerboardWidget.set_sounding

<div class="api-signature" markdown="1">

```python
def set_sounding(sounding: bool) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.set_sounding" line=583 %}{% raw %}

</div>

Mark the pitch during answer playback.

## FingerboardWidget.feedback_gap_ms

<div class="api-signature" markdown="1">

```python
def feedback_gap_ms() -> int
```

{% endraw %}{% include api-source.html name="FingerboardWidget.feedback_gap_ms" line=596 %}{% raw %}

</div>

Use the sounding note's full length for an animated single-note
question.

**Returns**

| Type | Description |
| --- | --- |
| `int` | Feedback duration in milliseconds. |

## FingerboardWidget.animate_silent_answer

<div class="api-signature" markdown="1">

```python
def animate_silent_answer(duration_ms: int) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.animate_silent_answer" line=613 %}{% raw %}

</div>

Show an image-anchored overlay during the usual silent picture
feedback interval.

## FingerboardWidget.hideEvent

<div class="api-signature" markdown="1">

```python
def hideEvent(event: QHideEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.hideEvent" line=637 %}{% raw %}

</div>

End any silent or sounding overlay when leaving the diagram.

## FingerboardWidget.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.paintEvent" line=644 %}{% raw %}

</div>

Draw the whole picture for a marked location, or only the neck
and ruler for a note on a string.
{% endraw %}
