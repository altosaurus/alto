---
title: cascade
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-cascade/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def cascade(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="cascade" line=371 %}{% raw %}

</div>

Set the sprites for a cascade: the new cards arrive one after
another, each rising a little as it appears.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
...     for _ in range(2)
... ]
>>> cascade(
...     Scene(
...         time=100,
...         old=[],
...         new=new,
...         direction=1,
...     )
... )
>>> new[0].opacity > new[1].opacity > 0.0
True
```
{% endraw %}
