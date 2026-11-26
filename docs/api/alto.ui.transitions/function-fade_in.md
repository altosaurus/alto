---
title: fade_in
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-fade_in/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def fade_in(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="fade_in" line=228 %}{% raw %}

</div>

Set the sprites for a fade in: the new cards fade up from clear, and
nothing of the old remains.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> fade_in(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].opacity
0.0
```
{% endraw %}
