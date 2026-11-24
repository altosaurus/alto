---
title: alto.ui.fingerboard
parent: api
package: alto.ui
permalink: /api/alto.ui.fingerboard/
---
{% raw %}
Render a pack's instrument portrait using its calibrated string
endpoints.

## ruler_reach

<div class="api-signature" markdown="1">

```python
def ruler_reach(model: PackInstrument) -> int
```

{% endraw %}{% include api-source.html name="ruler_reach" line=55 %}{% raw %}

</div>

Find how many half steps the ruler covers: an octave, or further if
the pack names a position beyond it.

**Parameters**

- `model` (*PackInstrument*): The instrument whose positions, if any, the ruler labels.

**Returns**

- *int*: The highest half step with a tick.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> bare = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (10, 10),
...     (),
...     None,
... )
>>> ruler_reach(bare)
12
>>> ruler_reach(
...     PackInstrument(
...         "pack.x.y",
...         Path("a.png"),
...         (10, 10),
...         (),
...         None,
...         positions=((14, "9th"),),
...     )
... )
14
```

## ruler_base

<div class="api-signature" markdown="1">

```python
def ruler_base(
    model: PackInstrument,
    *,
    step: int,
) -> tuple[QPointF, QPointF, float]
```

{% endraw %}{% include api-source.html name="ruler_base" line=97 %}{% raw %}

</div>

Locate where a ruler tick for one half step starts, beside the
fingerboard rather than on it.

**Parameters**

- `model` (*PackInstrument*): The instrument whose string endpoints give the geometry.
- `step` (*int*): Half steps above the open string.

**Returns**

- *tuple of QPointF, QPointF and float*: The tick's starting point in image pixels, the unit vector pointing away from the strings, and the local distance between neighboring strings at that step.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> from alto.instrument_packs import PackString
>>> strings = (
...     PackString("C3", (0, 10), (100, 10)),
...     PackString("G3", (0, 0), (100, 0)),
... )
>>> viola = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (100, 10),
...     strings,
...     None,
... )
>>> start, away, apart = ruler_base(
...     viola, step=0
... )
>>> (start.x(), start.y(), away.y(), apart)
(0.0, -18.0, -1.0, 10.0)
```

## neck_view

<div class="api-signature" markdown="1">

```python
def neck_view(
    model: PackInstrument,
    *,
    gap: float,
) -> QRectF
```

{% endraw %}{% include api-source.html name="neck_view" line=152 %}{% raw %}

</div>

Choose the part of the picture a note question needs: the nut, the
neck with its ruler, and the bridge.

The scroll, the pegs and everything past the bridge are left out,
since the question never refers to them.

**Parameters**

- `model` (*PackInstrument*): The instrument whose string endpoints give the geometry.
- `gap` (*float*): The smallest distance between strings at the nut, in image pixels. Keyword-only.

**Returns**

- *QRectF*: The region to show, in image pixels. It can extend past the picture, so intersect it with the picture's rectangle.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> from alto.instrument_packs import PackString
>>> strings = (
...     PackString("C3", (100, 60), (900, 60)),
...     PackString("G3", (100, 40), (900, 40)),
... )
>>> board = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (1000, 100),
...     strings,
...     None,
... )
>>> view = neck_view(board, gap=20.0)
>>> (
...     view.left() < 100
...     and view.right() > 900
...     and view.top() < 40
...     and view.bottom() > 60
... )
True
```

## manual_style

<div class="api-signature" markdown="1">

```python
def manual_style(model: PackInstrument) -> tuple[KeyboardStyle | None, float]
```

{% endraw %}{% include api-source.html name="manual_style" line=219 %}{% raw %}

</div>

Build the look of an instrument's drawn keyboards from its plugin's
``keyboard_style``.

**Parameters**

- `model` (*PackInstrument*): The instrument whose keyboards are drawn.

**Returns**

- *tuple of KeyboardStyle or None and float*: The style, or None to use the learner's own keyboard style, and how long a natural key is, in key widths.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> bare = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (10, 10),
...     (),
...     None,
... )
>>> manual_style(bare)
(None, 4.5)
>>> from alto.instrument_packs import (
...     PackKeyboardStyle,
... )
>>> look = PackKeyboardStyle(
...     (("cap", "#eee3c8"),),
...     (("length", 5.0),),
... )
>>> styled = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (10, 10),
...     (),
...     None,
...     keyboard_style=look,
... )
>>> look_style, look_length = manual_style(
...     styled
... )
>>> # noinspection PyUnresolvedReferences
>>> look_style.cap, look_length
('#eee3c8', 5.0)
```

## FingerboardWidget

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

### FingerboardWidget.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="FingerboardWidget.sizeHint" line=331 %}{% raw %}

</div>

Reserve space for the whole instrument.

**Returns**

- *QSize*: Preferred dimensions of the diagram.

### FingerboardWidget.show_position

<div class="api-signature" markdown="1">

```python
def show_position(position: FingerboardPosition | PicturePosition | None) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.show_position" line=360 %}{% raw %}

</div>

Resolve the saved pack identity and clear the previous playback
highlight.

### FingerboardWidget.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.resizeEvent" line=494 %}{% raw %}

</div>

Fit the drawn keyboards to the new height.

**Parameters**

- `event` (*QResizeEvent*): The resize that happened.

### FingerboardWidget.set_pickable

<div class="api-signature" markdown="1">

```python
def set_pickable(pickable: bool) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.set_pickable" line=519 %}{% raw %}

</div>

Let a click on the picture be an answer, and say so with the
pointer.

**Parameters**

- `pickable` (*bool*): True to emit `picked` for each click on the picture.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> board = FingerboardWidget()
>>> board.set_pickable(True)
>>> board.cursor().shape() == Qt.CursorShape.PointingHandCursor
True
```

### FingerboardWidget.show_target

<div class="api-signature" markdown="1">

```python
def show_target(point: tuple[float, float] | None) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.show_target" line=543 %}{% raw %}

</div>

Mark the right place on a picture that has no marker, or clear
the mark.

**Parameters**

- `point` (*tuple of float, or None*): The place in the picture's own pixels, or None to clear it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> board = FingerboardWidget()
>>> board.show_target((10.0, 20.0))
>>> board.show_target(None)
```

### FingerboardWidget.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.mousePressEvent" line=562 %}{% raw %}

</div>

Turn a click into a point on the picture when the picture is
being used for an answer.

**Parameters**

- `event` (*QMouseEvent*): The click.

### FingerboardWidget.set_sounding

<div class="api-signature" markdown="1">

```python
def set_sounding(sounding: bool) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.set_sounding" line=583 %}{% raw %}

</div>

Mark the pitch during answer playback.

### FingerboardWidget.feedback_gap_ms

<div class="api-signature" markdown="1">

```python
def feedback_gap_ms() -> int
```

{% endraw %}{% include api-source.html name="FingerboardWidget.feedback_gap_ms" line=596 %}{% raw %}

</div>

Use the sounding note's full length for an animated single-note
question.

**Returns**

- *int*: Feedback duration in milliseconds.

### FingerboardWidget.animate_silent_answer

<div class="api-signature" markdown="1">

```python
def animate_silent_answer(duration_ms: int) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.animate_silent_answer" line=613 %}{% raw %}

</div>

Show an image-anchored overlay during the usual silent picture
feedback interval.

### FingerboardWidget.hideEvent

<div class="api-signature" markdown="1">

```python
def hideEvent(event: QHideEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.hideEvent" line=637 %}{% raw %}

</div>

End any silent or sounding overlay when leaving the diagram.

### FingerboardWidget.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="FingerboardWidget.paintEvent" line=644 %}{% raw %}

</div>

Draw the whole picture for a marked location, or only the neck
and ruler for a note on a string.
{% endraw %}
