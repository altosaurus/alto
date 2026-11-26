---
title: blur
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-blur/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def blur(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="blur" line=479 %}{% raw %}

</div>

Set the sprites for a blur: the old cards dissolve into a blur and
the new ones come into focus.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> blur(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].blur, new[0].opacity
(1.0, 0.0)
```
{% endraw %}
