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

```python
def ruler_reach(model: PackInstrument) -> int
```

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

```python
def ruler_base(
    model: PackInstrument,
    *,
    step: int,
) -> tuple[QPointF, QPointF, float]
```

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

```python
def neck_view(
    model: PackInstrument,
    *,
    gap: float,
) -> QRectF
```

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

```python
def manual_style(model: PackInstrument) -> tuple[KeyboardStyle | None, float]
```

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

```python
FingerboardWidget()
```

Bases: `QWidget`

Draw the instrument and keep the teaching overlays on the same
scale.

**Constructor**

Create an empty fingerboard display.

### FingerboardWidget.sizeHint

```python
def sizeHint() -> QSize
```

Reserve space for the whole instrument.

**Returns**

- *QSize*: Preferred dimensions of the diagram.

### FingerboardWidget.show_position

```python
def show_position(position: FingerboardPosition | PicturePosition | None) -> None
```

Resolve the saved pack identity and clear the previous playback
highlight.

### FingerboardWidget.resizeEvent

```python
def resizeEvent(event: QResizeEvent) -> None
```

Fit the drawn keyboards to the new height.

**Parameters**

- `event` (*QResizeEvent*): The resize that happened.

### FingerboardWidget.set_pickable

```python
def set_pickable(pickable: bool) -> None
```

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

```python
def show_target(point: tuple[float, float] | None) -> None
```

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

```python
def mousePressEvent(event: QMouseEvent) -> None
```

Turn a click into a point on the picture when the picture is
being used for an answer.

**Parameters**

- `event` (*QMouseEvent*): The click.

### FingerboardWidget.set_sounding

```python
def set_sounding(sounding: bool) -> None
```

Mark the pitch during answer playback.

### FingerboardWidget.feedback_gap_ms

```python
def feedback_gap_ms() -> int
```

Use the sounding note's full length for an animated single-note
question.

**Returns**

- *int*: Feedback duration in milliseconds.

### FingerboardWidget.animate_silent_answer

```python
def animate_silent_answer(duration_ms: int) -> None
```

Show an image-anchored overlay during the usual silent picture
feedback interval.

### FingerboardWidget.hideEvent

```python
def hideEvent(event: QHideEvent) -> None
```

End any silent or sounding overlay when leaving the diagram.

### FingerboardWidget.paintEvent

```python
def paintEvent(event: QPaintEvent) -> None
```

Draw the whole picture for a marked location, or only the neck
and ruler for a note on a string.
{% endraw %}
