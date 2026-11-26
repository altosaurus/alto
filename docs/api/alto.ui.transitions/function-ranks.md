---
title: ranks
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-ranks/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ranks(
    sprites: Sequence[Sprite],
    *,
    order: str,
) -> list[int]
```

{% endraw %}{% include api-source.html name="ranks" line=761 %}{% raw %}

</div>

Say where each sprite comes in an order: 0 for the first to start.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `sprites` | `sequence of Sprite` | The cards of one side. |
| `order` | `str` | One of `ORDERS`: "index" is as laid out, "reverse" backwards, "outward" from the middle of the cards to the edges, "inward" the other way, "diagonal" from the top left to the bottom right, and "random" in a fixed scrambled order. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | The rank of each sprite, in the sprites' own order. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = [
...     Sprite(
...         pixmap=QPixmap(),
...         rect=QRectF(x, 0, 10, 10),
...     )
...     for x in (0, 20, 40)
... ]
>>> (
...     ranks(row, order="index"),
...     ranks(row, order="reverse"),
...     ranks(row, order="outward"),
... )
([0, 1, 2], [2, 1, 0], [1, 0, 2])
```
{% endraw %}
