---
title: note_shape
parent: alto.ui.notes
api_module: alto.ui.notes
package: alto.ui
permalink: /api/alto.ui.notes/function-note_shape/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def note_shape(
    value: str,
    *,
    stem_down: bool = False,
) -> QPainterPath
```

{% endraw %}{% include api-source.html name="note_shape" line=317 %}{% raw %}

</div>

Return the outline of a note of a value, with the stem up or down.

Half notes and shorter values have stems, so a double whole note or
whole note looks the same either way.
Shapes are cached after their first use.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `str` | "breve", "whole", "half", "quarter", "eighth", "sixteenth" or "thirty_second". |
| `stem_down` | `bool, default False` | Turn the stem down. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QPainterPath` | The outline, in glyph units. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> up, down = (
...     note_shape("quarter"),
...     note_shape("quarter", stem_down=True),
... )
>>> up == down
False
```
{% endraw %}
