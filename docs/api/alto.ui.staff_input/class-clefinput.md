---
title: ClefInput
parent: alto.ui.staff_input
api_module: alto.ui.staff_input
package: alto.ui
permalink: /api/alto.ui.staff_input/class-clefinput/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ClefInput(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ClefInput" line=1367 %}{% raw %}

</div>

Bases: `StaffWidget`

A blank staff on which you put a clef symbol: choose the G, C or F
clef, then click where it goes.

The symbol can go on any line or space of the staff and on the three
ledger lines and spaces above and below it, and
follows the pointer from place to place, in a lighter color, until
you click. Without the mouse, `move_caret` moves it,
`step_symbol` switches the symbol and `place_caret` places it.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `placed` | `Signal` | Emitted with the symbol ("G", "C" or "F") and its place when you click: 0 is the bottom line, 1 the space above it, up to 8 for the top line, with -6 to 14 allowed. |
| `changed` | `Signal` | Emitted when the symbol chosen or the place the keyboard would use changes. |
| `options` | `list of str` | The symbols that can be chosen, in the order the wheel goes through them. |
| `selected` | `str` | The symbol chosen now. |
| `locked` | `bool` | Ignore the mouse and the wheel (while feedback is showing). |
| `caret` | `int or None` | The place the keyboard would put the symbol; None until the keyboard has moved it. |
| `placed_symbol` | `str or None` | The symbol that has been placed and is drawn solid, with `placed_step` its place; None until one is. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G", "F"])
>>> staff.step_symbol(1)
>>> staff.selected
'F'
```

**Constructor**

Create the staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the staff. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefInput().hasMouseTracking()
True
```

## ClefInput.reset

<div class="api-signature" markdown="1">

```python
def reset(
    options: list[str],
    *,
    caption: str = '',
) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.reset" line=1451 %}{% raw %}

</div>

Clear the staff for a new question and offer some symbols to
choose from.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `options` | `list of str` | The symbols the wheel goes through, any of "G", "C" and "F"; the first is chosen to begin with. |
| `caption` | `str, default ""` | The question, written under the staff. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(
...     ["C", "F"],
...     caption="Place the alto clef.",
... )
>>> (
...     staff.selected,
...     staff.placed_symbol,
...     staff.caption,
... )
('C', None, 'Place the alto clef.')
```

## ClefInput.select

<div class="api-signature" markdown="1">

```python
def select(symbol: str) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.select" line=1496 %}{% raw %}

</div>

Choose a symbol.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `symbol` | `str` | "G", "C" or "F"; one that is not among the options is ignored. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G", "C", "F"])
>>> staff.select("F")
>>> staff.selected
'F'
```

## ClefInput.step_symbol

<div class="api-signature" markdown="1">

```python
def step_symbol(direction: int) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.step_symbol" line=1527 %}{% raw %}

</div>

Choose the next symbol of the options, or the one before, going
around.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `direction` | `int` | 1 for the next, -1 for the one before. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G", "C", "F"])
>>> staff.step_symbol(-1)
>>> staff.selected
'F'
```

## ClefInput.step_at

<div class="api-signature" markdown="1">

```python
def step_at(y: float) -> int
```

{% endraw %}{% include api-source.html name="ClefInput.step_at" line=1552 %}{% raw %}

</div>

Return the line or space nearest to a height in the widget.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `y` | `float` | The height, in pixels. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The place, 0 for the bottom line and 1 for the space above it, up to 8 for the top line; from the first ledger line below the staff (-6) to the third above it (14). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.resize(400, 300)
>>> floor = staff.staff_bottoms()["treble"]
>>> (
...     staff.step_at(floor),
...     staff.step_at(floor - 1.4 * staff.GAP),
...     staff.step_at(0),
...     staff.step_at(10_000),
... )
(0, 3, 14, -6)
```

## ClefInput.move_caret

<div class="api-signature" markdown="1">

```python
def move_caret(steps: int) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.move_caret" line=1588 %}{% raw %}

</div>

Move the place the keyboard would put the symbol.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `steps` | `int` | How many lines and spaces up (positive) or down, stopping at the last ledger lines; the first move starts from the middle line. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.move_caret(1)
>>> staff.caret
5
>>> staff.move_caret(20)
>>> staff.caret
14
```

## ClefInput.place

<div class="api-signature" markdown="1">

```python
def place(step: int) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.place" line=1622 %}{% raw %}

</div>

Put the chosen symbol in a place, drawn solid, and say so.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `step` | `int` | The place, 0 for the bottom line, 1 for the space above it and so on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["F"])
>>> got = []
>>> _ = staff.placed.connect(
...     lambda symbol, where: got.append(
...         (symbol, where)
...     )
... )
>>> staff.place(6)
>>> got, staff.placed_symbol, staff.placed_step
([('F', 6)], 'F', 6)
```

## ClefInput.place_caret

<div class="api-signature" markdown="1">

```python
def place_caret() -> None
```

{% endraw %}{% include api-source.html name="ClefInput.place_caret" line=1657 %}{% raw %}

</div>

Place the symbol where the keyboard put it, or on the middle
line if it has not moved.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.move_caret(-2)
>>> staff.place_caret()
>>> staff.placed_step
2
```

## ClefInput.clear_placed

<div class="api-signature" markdown="1">

```python
def clear_placed() -> None
```

{% endraw %}{% include api-source.html name="ClefInput.clear_placed" line=1673 %}{% raw %}

</div>

Take the placed symbol off the staff, so another can be tried.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.place(1)
>>> staff.clear_placed()
>>> staff.placed_symbol is None
True
```

## ClefInput.set_clef_color

<div class="api-signature" markdown="1">

```python
def set_clef_color(color: QColor | None) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.set_clef_color" line=1688 %}{% raw %}

</div>

Draw the placed symbol in a color, for feedback, or back in
black.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `color` | `QColor or None` | The color; None for black. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.set_clef_color(QColor("#2e7d32"))
>>> staff.clef_color == QColor("#2e7d32")
True
```

## ClefInput.mouseMoveEvent

<div class="api-signature" markdown="1">

```python
def mouseMoveEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.mouseMoveEvent" line=1708 %}{% raw %}

</div>

Show the symbol in the place under the pointer, in a lighter
color.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse move. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.resize(400, 300)
>>> from PySide6.QtCore import QPointF
>>> point = QPointF(
...     50,
...     staff.staff_bottoms()["treble"]
...     - 2 * staff.GAP,
... )
>>> staff.mouseMoveEvent(
...     QMouseEvent(
...         QEvent.Type.MouseMove,
...         point,
...         point,
...         Qt.MouseButton.NoButton,
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> staff._hover
4
```

## ClefInput.leaveEvent

<div class="api-signature" markdown="1">

```python
def leaveEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.leaveEvent" line=1746 %}{% raw %}

</div>

Stop following the pointer when it leaves the staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QEvent` | The leave event. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff._hover = 2
>>> staff.leaveEvent(QEvent(QEvent.Type.Leave))
>>> staff._hover is None
True
```

## ClefInput.mousePressEvent

<div class="api-signature" markdown="1">

```python
def mousePressEvent(event: QMouseEvent) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.mousePressEvent" line=1767 %}{% raw %}

</div>

Place the symbol on a left click, or choose the next symbol on a
right click.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QMouseEvent` | The mouse press. Nothing happens while the staff is locked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G", "F"])
>>> staff.resize(400, 300)
>>> from PySide6.QtCore import QPointF
>>> point = QPointF(
...     50, staff.staff_bottoms()["treble"]
... )
>>> staff.mousePressEvent(
...     QMouseEvent(
...         QEvent.Type.MouseButtonPress,
...         point,
...         point,
...         Qt.MouseButton.RightButton,
...         Qt.MouseButton.RightButton,
...         Qt.KeyboardModifier.NoModifier,
...     )
... )
>>> staff.selected
'F'
```

## ClefInput.wheelEvent

<div class="api-signature" markdown="1">

```python
def wheelEvent(event: QWheelEvent) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.wheelEvent" line=1806 %}{% raw %}

</div>

Choose the next symbol for each notch of the wheel turned up,
and the one before for each turned down.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QWheelEvent` | The wheel turn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPoint, QPointF
>>> staff = ClefInput()
>>> staff.reset(["G", "F"])
>>> here = QPointF(50, 50)
>>> staff.wheelEvent(
...     QWheelEvent(
...         here,
...         here,
...         QPoint(0, 0),
...         QPoint(0, 120),
...         Qt.MouseButton.NoButton,
...         Qt.KeyboardModifier.NoModifier,
...         Qt.ScrollPhase.NoScrollPhase,
...         False,
...     )
... )
>>> staff.selected
'F'
```

## ClefInput.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="ClefInput.paintEvent" line=1847 %}{% raw %}

</div>

Draw the staff, then the symbol that was placed or, until one
is, the one that would be placed.

A symbol on a ledger line has the ledger lines it needs drawn
behind it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = ClefInput()
>>> staff.reset(["G"])
>>> staff.place(1)
>>> staff.grab().isNull()
False
```
{% endraw %}
