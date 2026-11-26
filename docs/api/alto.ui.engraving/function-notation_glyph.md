---
title: notation_glyph
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-notation_glyph/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
@cache
def notation_glyph(
    font: str,
    *,
    codepoint: int,
) -> QPainterPath
```

{% endraw %}{% include api-source.html name="notation_glyph" line=362 %}{% raw %}

</div>

Read a score marking from a bundled font at four staff spaces per
em.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `font` | `str` | Preferred SMuFL font key. |
| `codepoint` | `int` | Standard Music Font Layout code point. |

**Returns**

| Type | Description |
| --- | --- |
| `QPainterPath` | Outline at 100 pixels per em. Bravura supplies markings missing in the selected font. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> notation_glyph(
...     "bravura", codepoint=0xE260
... ).isEmpty()
False
```
{% endraw %}
