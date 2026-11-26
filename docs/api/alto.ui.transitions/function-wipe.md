---
title: wipe
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-wipe/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def wipe(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="wipe" line=513 %}{% raw %}

</div>

Set the sprites for a wipe: the new cards are uncovered from one
side while the old ones fade.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `scene` | `Scene` | The time, the cards that are leaving and arriving, and the direction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> wipe(
...     Scene(
...         time=0,
...         old=[],
...         new=new,
...         direction=-1,
...     )
... )
>>> new[0].reveal, new[0].reveal_from
(0.0, -1)
```
{% endraw %}
