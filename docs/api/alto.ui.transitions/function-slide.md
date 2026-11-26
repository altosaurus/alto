---
title: slide
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-slide/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def slide(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="slide" line=300 %}{% raw %}

</div>

Set the sprites for a slide: both sets move sideways, toward the
side of the switch that was pressed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> slide(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].dx
60.0
```
{% endraw %}
