---
title: cells_of_key
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-cells_of_key/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def cells_of_key(place: int) -> dict[tuple[str, int], str]
```

{% endraw %}{% include api-source.html name="cells_of_key" line=178 %}{% raw %}

</div>

Return the six wedges that hold the chords of a major key, and the
Roman numeral of each.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `place` | `int` | The key's own place on the circle, clockwise from C at 0. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of tuple of (str, int) to str` | For each of the six cells, its ring ("outer" or "inner") and place, the numeral of its chord. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cells = cells_of_key(0)
>>> (
...     cells[("outer", 11)],
...     cells[("inner", 0)],
...     cells[("inner", 1)],
... )  # F is IV; Am is vi; Em is iii
('IV', 'vi', 'iii')
>>> cells[("outer", 1)]  # G is V
'V'
>>> (
...     len(cells_of_key(11)),
...     cells_of_key(11)[("outer", 10)],
... )  # in F major, B♭ is IV
(6, 'IV')
```
{% endraw %}
