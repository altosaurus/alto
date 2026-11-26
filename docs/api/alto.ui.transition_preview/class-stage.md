---
title: Stage
parent: alto.ui.transition_preview
api_module: alto.ui.transition_preview
package: alto.ui
permalink: /api/alto.ui.transition_preview/class-stage/
---
{% raw %}
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

| Attribute | Type | Description |
| --- | --- | --- |
| `canvas` | `TransitionCanvas` | Where a transition is drawn. |
| `resting` | `list of Sprite` | The cards that are showing when no transition is playing. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Stage().resting
[]
```

**Constructor**

Build the stage with nothing on it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Stage().canvas.running
False
```

## Stage.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="Stage.resizeEvent" line=149 %}{% raw %}

</div>

Keep the canvas the size of the stage.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QResizeEvent` | The resize. |

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

## Stage.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="Stage.paintEvent" line=171 %}{% raw %}

</div>

Draw the cards at rest, unless a transition is drawing them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> stage = Stage()
>>> stage.resize(100, 100)
>>> stage.grab().isNull()
False
```
{% endraw %}
