---
title: clef_targets
parent: alto.ui.staff
api_module: alto.ui.staff
package: alto.ui
permalink: /api/alto.ui.staff/function-clef_targets/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def clef_targets(clef: str) -> set[tuple[str, int]]
```

{% endraw %}{% include api-source.html name="clef_targets" line=132 %}{% raw %}

</div>

Return the ways a clef can be written: the symbol and where on the
staff it goes.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | A clef name such as "treble", "mezzo" or "baritone". |

**Returns**

| Type | Description |
| --- | --- |
| `set of tuple of (str, int)` | Each is a symbol, "G", "C" or "F", and the place of its reference line (the G, F or middle C) counted in lines and spaces up from the bottom line at 0: the bottom line is 0, the space above it 1, the second line 2, up to the top line at 8. Most clefs have one. The baritone clef has two: the F clef on the middle line and the C clef on the top line. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> clef_targets("treble") == {
...     ("G", 2)
... } and clef_targets("mezzo") == {("C", 2)}
True
>>> sorted(clef_targets("baritone"))
[('C', 8), ('F', 4)]
>>> sorted(
...     clef_targets("french")
...     | clef_targets("subbass")
... )
[('F', 8), ('G', 0)]
```
{% endraw %}
