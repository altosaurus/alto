---
title: neck_view
parent: alto.ui.fingerboard
api_module: alto.ui.fingerboard
package: alto.ui
permalink: /api/alto.ui.fingerboard/function-neck_view/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def neck_view(
    model: PackInstrument,
    *,
    gap: float,
) -> QRectF
```

{% endraw %}{% include api-source.html name="neck_view" line=152 %}{% raw %}

</div>

Choose the part of the picture a note question needs: the nut, the
neck with its ruler, and the bridge.

The scroll, the pegs and everything past the bridge are left out,
since the question never refers to them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `model` | `PackInstrument` | The instrument whose string endpoints give the geometry. |
| `gap` | `float` | The smallest distance between strings at the nut, in image pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QRectF` | The region to show, in image pixels. It can extend past the picture, so intersect it with the picture's rectangle. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> from alto.instrument_packs import PackString
>>> strings = (
...     PackString("C3", (100, 60), (900, 60)),
...     PackString("G3", (100, 40), (900, 40)),
... )
>>> board = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (1000, 100),
...     strings,
...     None,
... )
>>> view = neck_view(board, gap=20.0)
>>> (
...     view.left() < 100
...     and view.right() > 900
...     and view.top() < 40
...     and view.bottom() > 60
... )
True
```
{% endraw %}
