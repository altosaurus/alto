---
title: zoom
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-zoom/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def zoom(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="zoom" line=405 %}{% raw %}

</div>

Set the sprites for a zoom: the old cards grow a little as they
fade, and the new ones grow into place.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> zoom(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].sx
0.92
```
{% endraw %}
