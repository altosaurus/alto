---
title: drop
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-drop/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def drop(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="drop" line=547 %}{% raw %}

</div>

Set the sprites for drop and pop: the old cards drop away one by
one, then the new ones pop in with a small bounce.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> drop(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].opacity
0.0
```
{% endraw %}
