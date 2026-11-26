---
title: move
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-move/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def move(
    scene: Scene,
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> None
```

{% endraw %}{% include api-source.html name="move" line=869 %}{% raw %}

</div>

Set the sprites for a transition built from a motion for the cards
that leave and one for the cards that arrive.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards and the direction. |
| `leaving` | `Motion or None` | What the old cards do; None for them to be gone at once. |
| `arriving` | `Motion` | What the new cards do. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> move(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     ),
...     leaving=None,
...     arriving=Motion(dy=20),
... )
>>> new[0].opacity, new[0].dy
(0.0, 20.0)
```
{% endraw %}
