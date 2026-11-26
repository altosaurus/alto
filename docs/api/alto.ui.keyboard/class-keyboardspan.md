---
title: KeyboardSpan
parent: alto.ui.keyboard
api_module: alto.ui.keyboard
package: alto.ui
permalink: /api/alto.ui.keyboard/class-keyboardspan/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardSpan(
    parent: QWidget | None = None,
    *,
    compact: bool = False,
    size: tuple[int, int] = (124, 26),
)
```

{% endraw %}{% include api-source.html name="KeyboardSpan" line=768 %}{% raw %}

</div>

Bases: `QWidget`

The whole 88-key piano in miniature, with the keys that will be
asked shaded.

The full-size one can be dragged across to choose the span:
`dragged` is emitted with the lowest and highest key as it
changes.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `dragged` | `Signal` | Emitted with the lowest and highest key (MIDI numbers) as the span is dragged. |
| `lo` | `int` | The lowest key shaded. |
| `hi` | `int` | The highest key shaded. |
| `full` | `tuple of int` | The lowest and highest key the miniature draws. All 88 keys, unless a plugin's keyboard has fewer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> span = KeyboardSpan()
>>> span.set_span(60, hi=72)
>>> (span.lo, span.hi)
(60, 72)
```

**Constructor**

Create the miniature, shading the default range.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |
| `compact` | `bool, default False` | Make a fixed-size version that ignores the mouse, for a summary in a menu row. Keyword-only. |
| `size` | `tuple of (int, int), default (124, 26)` | The width and height of the compact version, in pixels. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardSpan(
...     compact=True, size=(100, 20)
... ).size().width()
100
```

## KeyboardSpan.key_at

<div class="api-signature" markdown="1">

```python
def key_at(pos: QPointF) -> int
```

{% endraw %}{% include api-source.html name="KeyboardSpan.key_at" line=850 %}{% raw %}

</div>

Return the key under a point.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `pos` | `QPointF` | The position in the widget. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The MIDI number: a black key where one is drawn there, else the white key (clamped to the ends of the piano). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> span = KeyboardSpan()
>>> span.resize(500, 64)
>>> (
...     span.key_at(QPointF(0, 50)),
...     span.key_at(QPointF(499, 50)),
... )  # the lowest and highest keys
(21, 108)
>>> span.key_at(QPointF(250, 50))
64
```

## KeyboardSpan.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyboardSpan.mousePressEvent" line=987 %}{% raw %}

</div>

Start choosing a span: grab an edge, pick the span up, or start
a new one.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The press. Only the left button does anything. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> span = KeyboardSpan()
>>> span.resize(500, 64)
>>> got = []
>>> _ = span.dragged.connect(
...     lambda lo, hi: got.append((lo, hi))
... )
>>> point = QPointF(5, 50)
>>> span.mousePressEvent(
...     QMouseEvent(
...         QEvent.Type.MouseButtonPress,
...         point,
...         point,
...         Qt.MouseButton.LeftButton,
...         Qt.MouseButton.LeftButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> got  # a press outside the span starts a new one on that key
[(21, 21)]
```

## KeyboardSpan.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyboardSpan.mouseMoveEvent" line=1028 %}{% raw %}

</div>

Drag the span, or (with no button held) show the cursor for what
a press here would do.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> span = KeyboardSpan()
>>> span.resize(500, 64)
>>> middle = QPointF(sum(span._edges()) / 2, 50)
>>> span.mouseMoveEvent(
...     QMouseEvent(
...         QEvent.Type.MouseMove,
...         middle,
...         middle,
...         Qt.MouseButton.NoButton,
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> # inside the span: it can be picked up
>>> span.cursor().shape() == Qt.CursorShape.OpenHandCursor
True
```

## KeyboardSpan.mouseReleaseEvent

<div class="api-signature" markdown="1">

```python
def mouseReleaseEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyboardSpan.mouseReleaseEvent" line=1082 %}{% raw %}

</div>

Finish a drag and refresh the cursor for where the pointer now
is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The release. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QEvent
>>> span = KeyboardSpan()
>>> span.resize(500, 64)
>>> point = QPointF(5, 50)
>>> span.mouseReleaseEvent(
...     QMouseEvent(
...         QEvent.Type.MouseButtonRelease,
...         point,
...         point,
...         Qt.MouseButton.LeftButton,
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> span._mode is None
True
```

## KeyboardSpan.set_span

<div class="api-signature" markdown="1">

```python
def set_span(
    lo: int,
    *,
    hi: int,
) -> None
```

{% endraw %}{% include api-source.html name="KeyboardSpan.set_span" line=1116 %}{% raw %}

</div>

Choose which keys are shaded and redraw.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `lo` | `int` | The lowest key asked, as a MIDI number. |
| `hi` | `int` | The highest key asked. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> span = KeyboardSpan()
>>> span.set_span(48, hi=72)
>>> (span.lo, span.hi)
(48, 72)
```

## KeyboardSpan.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyboardSpan.paintEvent" line=1142 %}{% raw %}

</div>

Draw the whole piano in miniature with the asked keys shaded and
the span's edges marked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> span = KeyboardSpan()
>>> span.grab().isNull()
False
```
{% endraw %}
