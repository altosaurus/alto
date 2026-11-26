---
title: rise
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-rise/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def rise(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="rise" line=337 %}{% raw %}

</div>

Set the sprites for a rise: the old cards sink and fade, and the new
ones rise into place.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> rise(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].dy, new[0].opacity
(22.0, 0.0)
```
{% endraw %}
