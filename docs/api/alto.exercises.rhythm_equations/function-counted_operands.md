---
title: counted_operands
parent: alto.exercises.rhythm_equations
api_module: alto.exercises.rhythm_equations
package: alto.exercises
permalink: /api/alto.exercises.rhythm_equations/function-counted_operands/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def counted_operands(ordinary: dict[float, list[str]]) -> dict[float, list[str]]
```

{% endraw %}{% include api-source.html name="counted_operands" line=372 %}{% raw %}

</div>

Supply counts for totals without a selected single symbol.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ordinary` | `dict` | Selected symbols by duration. |

**Returns**

| Type | Description |
| --- | --- |
| `dict` | Count and unit tokens indexed by their combined duration. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> counted_operands({4: ["quarter"]})[12]
['3:quarter']
```
{% endraw %}
