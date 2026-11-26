---
title: staff_line_width
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-staff_line_width/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def staff_line_width(
    font: str,
    *,
    gap: float,
) -> float
```

{% endraw %}{% include api-source.html name="staff_line_width" line=394 %}{% raw %}

</div>

Return the thickness of a staff line, as the font specifies.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `font` | `str` | A key of `_FILES`. |
| `gap` | `float` | The distance between staff lines in pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The thickness in pixels, at least 1. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff_line_width("bravura", gap=16) >= 1.0
True
```
{% endraw %}
