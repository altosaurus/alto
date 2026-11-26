---
title: clef_shape
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/function-clef_shape/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def clef_shape(clef: str) -> str
```

{% endraw %}{% include api-source.html name="clef_shape" line=171 %}{% raw %}

</div>

Return the clef as it is drawn.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | A clef name such as "treble" or "baritone". |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The same name, except that "baritone" becomes "baritone_f" or "baritone_c" by the chosen way of writing it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> clef_shape("alto")
'alto'
>>> set_baritone_clef("c")
>>> clef_shape("baritone")
'baritone_c'
>>> set_baritone_clef(
...     "f"
... )  # back to the default
>>> clef_shape("baritone")
'baritone_f'
```
{% endraw %}
