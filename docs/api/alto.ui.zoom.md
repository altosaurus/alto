---
title: alto.ui.zoom
parent: api
package: alto.ui
permalink: /api/alto.ui.zoom/
---
{% raw %}
Zoom: make everything in Alto larger or smaller together.

The zoom is a percentage, 100 by default, that moves through a list of steps. It scales the application font, every pixel
and point length in the stylesheet, and the sizes the interface fixes in pixels, which are written with `px` here so that
they follow it. The notation that is drawn by hand takes its size from the same percentage. Pressing Ctrl and Plus or Ctrl and
Minus, or turning the mouse wheel with Ctrl held, moves one step, and Ctrl and 0 goes back to 100%. The choice is saved.

**Examples**

```pycon
>>> set_percent(100)
False
>>> px(20), px(0)
(20, 0)
>>> css("QLabel { font-size: 14pt; border: 1px solid; }")
'QLabel { font-size: 14pt; border: 1px solid; }'
```

## percent

```python
def percent() -> int
```

Give the zoom now in force.

**Returns**

- *int*: The percentage, one of `STEPS`.

**Examples**

```pycon
>>> percent()
100
```

## factor

```python
def factor() -> float
```

Give the zoom as a multiplier.

**Returns**

- *float*: 1.0 at 100%.

**Examples**

```pycon
>>> factor()
1.0
```

## px

```python
def px(value: float) -> int
```

Scale a length in pixels by the zoom.

**Parameters**

- `value` (*float*): The length at 100%.

**Returns**

- *int*: The length now, rounded, and never less than one pixel unless it was zero.

**Examples**

```pycon
>>> px(20), px(0), px(-4)
(20, 0, -4)
```

## css

```python
def css(text: str) -> str
```

Scale every pixel and point length in a stylesheet by the zoom.

**Parameters**

- `text` (*str*): The stylesheet.

**Returns**

- *str*: The same stylesheet with each length such as ``12px`` or ``14pt`` multiplied. A length of zero stays zero.

**Examples**

```pycon
>>> css("QLabel { padding: 8px 12px; font-size: 14pt; margin: 0px; }")
'QLabel { padding: 8px 12px; font-size: 14pt; margin: 0px; }'
```

## apply_font

```python
def apply_font() -> None
```

Make the application font as large as the zoom says, from the size it had at 100%.

**Examples**

```pycon
>>> apply_font()
```

## set_percent

```python
def set_percent(value: int) -> bool
```

Zoom to the step nearest a percentage, save it and say so.

**Parameters**

- `value` (*int*): The percentage wanted.

**Returns**

- *bool*: True if the zoom changed, False if it was already there.

**Examples**

```pycon
>>> set_percent(125)
True
>>> percent(), factor()
(125, 1.25)
>>> set_percent(125)
False
>>> set_percent(100)
True
```

## step

```python
def step(direction: int) -> bool
```

Zoom in or out by one step.

**Parameters**

- `direction` (*int*): Positive to zoom in, negative to zoom out.

**Returns**

- *bool*: True if the zoom changed, False at the largest or smallest step.

**Examples**

```pycon
>>> step(1), percent()
(True, 110)
>>> step(-1), percent()
(True, 100)
>>> while step(-1):
...     pass
>>> percent(), step(-1)
(50, False)
>>> reset(), percent()
(True, 100)
```

## reset

```python
def reset() -> bool
```

Go back to 100%.

**Returns**

- *bool*: True if the zoom changed.

**Examples**

```pycon
>>> reset()
False
```

## load

```python
def load() -> None
```

Take the saved zoom into force, without announcing it, ignoring anything that is not a step.

**Examples**

```pycon
>>> store().setValue(SETTING, 150)
>>> load()
>>> percent()
150
>>> store().setValue(SETTING, "wide")
>>> load()
>>> percent()
100
```

## WheelZoom

```python
WheelZoom(parent: QObject | None = None)
```

Bases: `QObject`

Zoom when the mouse wheel turns with Ctrl held, wherever the pointer is.

A touchpad that sends small steps is added up, so that a whole notch is needed to move one step.

**Examples**

```pycon
>>> WheelZoom().eventFilter(QObject(), QEvent(QEvent.Type.None_))
False
```

**Constructor**

Start with no wheel turned.

**Parameters**

- `parent` (*QObject or None, default None*): The object that owns the filter.

**Constructor examples**

```pycon
>>> WheelZoom()._turned
0
```

### WheelZoom.eventFilter

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

Take a wheel event with Ctrl held as a zoom, and let every other event through.

**Parameters**

- `watched` (*QObject*): The object the event is for.
- `event` (*QEvent*): The event.

**Returns**

- *bool*: True when the event was a zoom, so that nothing under the pointer scrolls.

**Examples**

```pycon
>>> WheelZoom().eventFilter(QObject(), QEvent(QEvent.Type.None_))
False
```
{% endraw %}
