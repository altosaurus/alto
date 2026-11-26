---
title: TransitionPreview
parent: alto.ui.transition_preview
api_module: alto.ui.transition_preview
package: alto.ui
permalink: /api/alto.ui.transition_preview/class-transitionpreview/
---
{% raw %}
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

| Attribute | Type | Description |
| --- | --- | --- |
| `transition` | `Transition` | The transition being shown. |
| `side` | `int` | Which set of cards is showing: 0 for the exercises, 1 for the lessons. |
| `stage` | `Stage` | The page the cards are on. |
| `switch` | `SegmentedControl` | The mock switch in the title bar. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.side
0
```

**Constructor**

Build the preview, showing the default transition.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> TransitionPreview().transition.key
'cascade'
```

## TransitionPreview.show_transition

<div class="api-signature" markdown="1">

```python
def show_transition(key: str) -> None
```

{% endraw %}{% include api-source.html name="TransitionPreview.show_transition" line=334 %}{% raw %}

</div>

Show a transition: the exercises appear, and after a moment they
change to the lessons, once.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The transition's key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.show_transition("flip")
>>> preview.transition.key
'flip'
```

## TransitionPreview.replay

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

## TransitionPreview.go_to

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

| Parameter | Type | Description |
| --- | --- | --- |
| `side` | `int` | 0 for the exercises, 1 for the lessons. |

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

## TransitionPreview.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="TransitionPreview.resizeEvent" line=444 %}{% raw %}

</div>

Lay the cards out again for the new size, unless a transition is
playing.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QResizeEvent` | The resize. |

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
