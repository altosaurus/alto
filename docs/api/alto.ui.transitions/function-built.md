---
title: built
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-built/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def built(
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> tuple[Callable[[Scene], None], Callable[[Scene], float]]
```

{% endraw %}{% include api-source.html name="built" line=1014 %}{% raw %}

</div>

Make the frame and length functions of a transition built from
motions.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `leaving` | `Motion or None` | What the old cards do. Keyword-only. |
| `arriving` | `Motion` | What the new cards do. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (callable, callable)` | The frame function, and the length function. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> draw, lasts = built(
...     leaving=None,
...     arriving=Motion(
...         length=300, per_card=50
...     ),
... )
>>> lasts(
...     Scene(
...         time=0,
...         old=[],
...         new=[
...             Sprite(
...                 pixmap=QPixmap(),
...                 rect=QRectF(),
...             )
...         ]
...         * 3,
...         direction=1,
...     )
... )
400.0
```
{% endraw %}
