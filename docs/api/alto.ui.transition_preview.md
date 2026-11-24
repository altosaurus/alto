---
title: alto.ui.transition_preview
parent: api
package: alto.ui
permalink: /api/alto.ui.transition_preview/
---
{% raw %}
A preview of a transition for the settings.

It is a mock of the home page, with the app's own cards, that switches
from the exercises to the lessons once.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.show_transition("cascade")
>>> preview.transition.key
'cascade'
```

## make_sides

<div class="api-signature" markdown="1">

```python
def make_sides() -> tuple[list[TileCard], list[TileCard]]
```

{% endraw %}{% include api-source.html name="make_sides" line=79 %}{% raw %}

</div>

Make the cards for the two sides of the preview: the app's own
exercise cards, and its lesson cards.

The lessons side has the real lesson, and a few examples that are
marked as such, so that a transition has more than one
card to move.

**Returns**

- *tuple of (list of TileCard, list of TileCard)*: The cards of the exercises side, and of the lessons side.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> first, second = make_sides()
>>> len(first), len(second) > len(LESSONS)
(6, True)
```

## Stage

<div class="api-signature" markdown="1">

```python
Stage(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="Stage" line=113 %}{% raw %}

</div>

Bases: `QWidget`

The page of the mock window: it draws the cards that are resting,
and the transition plays on a canvas over it.

**Attributes**

- `canvas` (*TransitionCanvas*): Where a transition is drawn.
- `resting` (*list of Sprite*): The cards that are showing when no transition is playing.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Stage().resting
[]
```

**Constructor**

Build the stage with nothing on it.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Stage().canvas.running
False
```

### Stage.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="Stage.resizeEvent" line=149 %}{% raw %}

</div>

Keep the canvas the size of the stage.

**Parameters**

- `event` (*QResizeEvent*): The resize.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> stage = Stage()
>>> # a hidden widget is only told about its size once it is
>>> # shown
>>> stage.show()
>>> stage.resize(300, 200)
>>> stage.canvas.geometry() == stage.rect()
True
```

### Stage.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="Stage.paintEvent" line=171 %}{% raw %}

</div>

Draw the cards at rest, unless a transition is drawing them.

**Parameters**

- `_` (*QPaintEvent*): The paint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> stage = Stage()
>>> stage.resize(100, 100)
>>> stage.grab().isNull()
False
```

## TransitionPreview

<div class="api-signature" markdown="1">

```python
TransitionPreview(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="TransitionPreview" line=194 %}{% raw %}

</div>

Bases: `QFrame`

A mock home page that plays a transition between two sets of the
app's cards, once.

It has a bar with the same Exercises and Lessons switch as the real
window. It follows the side that is showing, and pressing
it plays the transition to the other side, so the learner can try it
as often as they like.

**Attributes**

- `transition` (*Transition*): The transition being shown.
- `side` (*int*): Which set of cards is showing: 0 for the exercises, 1 for the lessons.
- `stage` (*Stage*): The page the cards are on.
- `switch` (*SegmentedControl*): The mock switch in the title bar.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.side
0
```

**Constructor**

Build the preview, showing the default transition.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> TransitionPreview().transition.key
'cascade'
```

### TransitionPreview.show_transition

<div class="api-signature" markdown="1">

```python
def show_transition(key: str) -> None
```

{% endraw %}{% include api-source.html name="TransitionPreview.show_transition" line=334 %}{% raw %}

</div>

Show a transition: the exercises appear, and after a moment they
change to the lessons, once.

**Parameters**

- `key` (*str*): The transition's key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.show_transition("flip")
>>> preview.transition.key
'flip'
```

### TransitionPreview.replay

<div class="api-signature" markdown="1">

```python
def replay() -> None
```

{% endraw %}{% include api-source.html name="TransitionPreview.replay" line=360 %}{% raw %}

</div>

Play the transition that is showing again, from the exercises.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.replay()
>>> preview.transition.key
'cascade'
```

### TransitionPreview.go_to

<div class="api-signature" markdown="1">

```python
def go_to(side: int) -> None
```

{% endraw %}{% include api-source.html name="TransitionPreview.go_to" line=387 %}{% raw %}

</div>

Switch to one side with the transition, as the switch does in
the real window.

A transition that is still playing ends first. Nothing happens
if that side is already showing.

**Parameters**

- `side` (*int*): 0 for the exercises, 1 for the lessons.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.go_to(1)
>>> preview.side, preview.switch.current()
(1, 1)
>>> preview.go_to(0)
>>> preview.side
0
```

### TransitionPreview.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="TransitionPreview.resizeEvent" line=444 %}{% raw %}

</div>

Lay the cards out again for the new size, unless a transition is
playing.

**Parameters**

- `event` (*QResizeEvent*): The resize.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.resize(700, 500)
>>> preview.stage.resting[
...     0
... ].rect.width() <= CARD_W
True
```
{% endraw %}
