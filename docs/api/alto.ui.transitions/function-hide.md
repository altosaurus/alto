---
title: hide
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-hide/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def hide(sprites: Sequence[Sprite]) -> None
```

{% endraw %}{% include api-source.html name="hide" line=206 %}{% raw %}

</div>

Make sprites invisible.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `sprites` | `sequence of Sprite` | The sprites. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = Sprite(
...     pixmap=QPixmap(), rect=QRectF()
... )
>>> hide([card])
>>> card.opacity
0.0
```
{% endraw %}
