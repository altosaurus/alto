---
title: flip
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-flip/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def flip(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="flip" line=441 %}{% raw %}

</div>

Set the sprites for a flip: each old card turns edge on and goes,
then each new one turns face on.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> flip(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].opacity
0.0
```
{% endraw %}
