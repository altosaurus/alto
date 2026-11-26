---
title: ledger_width
parent: alto.ui.engraving
api_module: alto.ui.engraving
package: alto.ui
permalink: /api/alto.ui.engraving/function-ledger_width/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ledger_width(
    font: str,
    *,
    gap: float,
) -> float
```

{% endraw %}{% include api-source.html name="ledger_width" line=422 %}{% raw %}

</div>

Return the thickness of a ledger line, as the font specifies.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `font` | `str` | A key of `_FILES`. |
| `gap` | `float` | The distance between staff lines in pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The thickness in pixels, at least 1.2. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ledger_width("bravura", gap=16) >= 1.2
True
```
{% endraw %}
