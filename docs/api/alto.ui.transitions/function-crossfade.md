---
title: crossfade
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-crossfade/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def crossfade(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="crossfade" line=257 %}{% raw %}

</div>

Set the sprites for a crossfade: the old cards fade out as the new
ones fade in.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> old, new = (
...     [
...         Sprite(
...             pixmap=QPixmap(), rect=QRectF()
...         )
...     ],
...     [
...         Sprite(
...             pixmap=QPixmap(), rect=QRectF()
...         )
...     ],
... )
>>> crossfade(
...     Scene(
...         time=300,
...         old=old,
...         new=new,
...         direction=1,
...     )
... )
>>> old[0].opacity, new[0].opacity
(0.0, 1.0)
```
{% endraw %}
