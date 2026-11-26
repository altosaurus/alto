---
title: accidental_width
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-accidental_width/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def accidental_width(
    *,
    font: str,
    sign: int,
    gap: float,
) -> float
```

{% endraw %}{% include api-source.html name="accidental_width" line=810 %}{% raw %}

</div>

Return how wide a sharp, flat or natural is drawn, so that it can be
placed beside other things.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `font` | `str` | A key of `_FILES`. Keyword-only. |
| `sign` | `int` | -2 for a double flat, -1 flat, 0 natural, 1 sharp or 2 double sharp. Keyword-only. |
| `gap` | `float` | The distance between staff lines in pixels, which sets the size. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The width of the glyph's ink, in pixels. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> accidental_width(
...     font="bravura", sign=1, gap=16
... ) > accidental_width(
...     font="bravura", sign=1, gap=8
... )
True
```
{% endraw %}
