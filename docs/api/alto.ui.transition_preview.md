---
title: alto.ui.transition_preview
parent: api
package: alto.ui
order: 52
permalink: /api/alto.ui.transition_preview/
---
{% raw %}
A preview of a transition for the settings.

It is a mock of the home page, with the app's own cards, that switches from the exercises to the lessons once.

**Examples**

```pycon
>>> preview = TransitionPreview()
>>> preview.show_transition("cascade")
>>> preview.transition.key
'cascade'
```

## make_sides

```python
def make_sides() -> tuple[list[TileCard], list[TileCard]]
```

Make the cards for the two sides of the preview: the app's own exercise cards, and its lesson cards.

The lessons side has the real lesson, and a few examples that are marked as such, so that a transition has more than one
card to move.

**Returns**

- *tuple of (list of TileCard, list of TileCard)*: The cards of the exercises side, and of the lessons side.

**Examples**

```pycon
>>> first, second = make_sides()
>>> len(first), len(second) > len(LESSONS)
(6, True)
```

## Stage

```python
Stage(parent: QWidget | None = None)
```

Bases: `QWidget`

The page of the mock window: it draws the cards that are resting, and the transition plays on a canvas over it.

**Attributes**

- `canvas` (*TransitionCanvas*): Where a transition is drawn.
- `resting` (*list of Sprite*): The cards that are showing when no transition is playing.

**Examples**

```pycon
>>> Stage().resting
[]
```

**Constructor**

Build the stage with nothing on it.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> Stage().canvas.running
False
```

### Stage.resizeEvent

```python
def resizeEvent(event: QResizeEvent) -> None
```

Keep the canvas the size of the stage.

**Parameters**

- `event` (*QResizeEvent*): The resize.

**Examples**

```pycon
>>> stage = Stage()
>>> stage.show()  # a hidden widget is only told about its size once it is shown
>>> stage.resize(300, 200)
>>> stage.canvas.geometry() == stage.rect()
True
```

### Stage.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw the cards at rest, unless a transition is drawing them.

**Parameters**

- `_` (*QPaintEvent*): The paint request.

**Examples**

```pycon
>>> stage = Stage()
>>> stage.resize(100, 100)
>>> stage.grab().isNull()
False
```

## TransitionPreview

```python
TransitionPreview(parent: QWidget | None = None)
```

Bases: `QFrame`

A mock home page that plays a transition between two sets of the app's cards, once.

It has a bar with the same Exercises and Lessons switch as the real window. It follows the side that is showing, and pressing
it plays the transition to the other side, so the learner can try it as often as they like.

**Attributes**

- `transition` (*Transition*): The transition being shown.
- `side` (*int*): Which set of cards is showing: 0 for the exercises, 1 for the lessons.
- `stage` (*Stage*): The page the cards are on.
- `switch` (*SegmentedControl*): The mock switch in the title bar.

**Examples**

```pycon
>>> preview = TransitionPreview()
>>> preview.side
0
```

**Constructor**

Build the preview, showing the default transition.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> TransitionPreview().transition.key
'cascade'
```

### TransitionPreview.show_transition

```python
def show_transition(key: str) -> None
```

Show a transition: the exercises appear, and after a moment they change to the lessons, once.

**Parameters**

- `key` (*str*): The transition's key.

**Examples**

```pycon
>>> preview = TransitionPreview()
>>> preview.show_transition("flip")
>>> preview.transition.key
'flip'
```

### TransitionPreview.replay

```python
def replay() -> None
```

Play the transition that is showing again, from the exercises.

**Examples**

```pycon
>>> preview = TransitionPreview()
>>> preview.replay()
>>> preview.transition.key
'cascade'
```

### TransitionPreview.go_to

```python
def go_to(side: int) -> None
```

Switch to one side with the transition, as the switch does in the real window.

A transition that is still playing ends first. Nothing happens if that side is already showing.

**Parameters**

- `side` (*int*): 0 for the exercises, 1 for the lessons.

**Examples**

```pycon
>>> preview = TransitionPreview()
>>> preview.go_to(1)
>>> preview.side, preview.switch.current()
(1, 1)
>>> preview.go_to(0)
>>> preview.side
0
```

### TransitionPreview.resizeEvent

```python
def resizeEvent(event: QResizeEvent) -> None
```

Lay the cards out again for the new size, unless a transition is playing.

**Parameters**

- `event` (*QResizeEvent*): The resize.

**Examples**

```pycon
>>> preview = TransitionPreview()
>>> preview.resize(700, 500)
>>> preview.stage.resting[0].rect.width() <= CARD_W
True
```
{% endraw %}
