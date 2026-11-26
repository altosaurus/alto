---
title: clef_target_of
parent: alto.ui.staff
api_module: alto.ui.staff
package: alto.ui
permalink: /api/alto.ui.staff/function-clef_target_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def clef_target_of(shape: str) -> tuple[str, int]
```

{% endraw %}{% include api-source.html name="clef_target_of" line=172 %}{% raw %}

</div>

Return the symbol and the place of one way of writing a clef.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `shape` | `str` | A key of `engraving.CLEF_SIGNS`, such as "alto" or "baritone_c". |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (str, int)` | The symbol and its place, as for `clef_targets`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     clef_target_of("bass"),
...     clef_target_of("soprano"),
... )
(('F', 6), ('C', 0))
```
{% endraw %}
