---
title: TransitionCanvas
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/class-transitioncanvas/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
TransitionCanvas(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="TransitionCanvas" line=1639 %}{% raw %}

</div>

Bases: `QWidget`

A see-through sheet laid over the cards, on which a transition is
drawn.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `old` | `list of Sprite` | The cards that are leaving. |
| `new` | `list of Sprite` | The cards that are arriving. |
| `finished` | `Signal` | Emitted when a transition has played to its end. |
| `running` | `bool` | True while a transition is playing. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.running
False
```

**Constructor**

Build the canvas, hidden.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget it is laid over. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> TransitionCanvas().isHidden()
True
```

## TransitionCanvas.cover

<div class="api-signature" markdown="1">

```python
def cover(old: list[Sprite]) -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.cover" line=1692 %}{% raw %}

</div>

Show the old cards on the canvas as they are, so that they can
be swapped for the new ones unseen.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `old` | `list of Sprite` | The photographs of the cards that are leaving. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.running
True
```

## TransitionCanvas.play

<div class="api-signature" markdown="1">

```python
def play(
    transition: Transition,
    *,
    new: list[Sprite],
    direction: int,
) -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.play" line=1718 %}{% raw %}

</div>

Play a transition from the old cards that cover the canvas to
the new ones.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `transition` | `Transition` | Which one. |
| `new` | `list of Sprite` | The photographs of the cards that are arriving. Keyword-only. |
| `direction` | `int` | 1 when going toward the lessons, -1 when coming back. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.play(
...     TRANSITIONS[1], new=[], direction=1
... )
>>> canvas.running
True
>>> canvas.stop()
```

## TransitionCanvas.stop

<div class="api-signature" markdown="1">

```python
def stop() -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.stop" line=1763 %}{% raw %}

</div>

End the transition at once and take the canvas away.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.stop()
>>> canvas.running, canvas.isHidden()
(False, True)
```

## TransitionCanvas.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.paintEvent" line=1808 %}{% raw %}

</div>

Draw every sprite as it now looks.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.resize(100, 100)
>>> canvas.grab().isNull()
False
```
{% endraw %}
