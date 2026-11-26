---
title: equation_tokens
parent: alto.exercises.rhythm_equations
api_module: alto.exercises.rhythm_equations
package: alto.exercises
permalink: /api/alto.exercises.rhythm_equations/function-equation_tokens/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def equation_tokens(
    rng: random.Random,
    *,
    ordinary: dict[float, list[str]],
    grouped: tuple[dict[float, list[str]], ...],
    left: int,
    right: int,
    operators: tuple[str, ...],
    right_operators: tuple[str, ...] | None = None,
    parentheses: bool = True,
) -> list[str]
```

{% endraw %}{% include api-source.html name="equation_tokens" line=267 %}{% raw %}

</div>

Choose a shared total, then build both sides backwards from it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Chooses the grouping, total, signs and symbols. |
| `ordinary` | `dict` | Single note and rest names by duration in sixteenth notes. |
| `grouped` | `tuple of dict` | Separate tables of tied and beamed names by duration. |
| `left` | `int` | Operator count before the equals sign. |
| `right` | `int` | Operator count after the equals sign. |
| `operators` | `tuple of str` | Signs allowed on the left and, by default, on the right. |
| `right_operators` | `tuple of str or None` | Separate selection of signs for the right side. |
| `parentheses` | `bool` | Whether an expression can group operations with parentheses. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | Equation tokens, or an empty list if no equation fits. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> equation_tokens(random.Random(0), ordinary={4: ["q"]},
...     grouped=(), left=1, right=1, operators=("+",))
['q', '+', 'q', '=', 'q', '+', 'q']
```
{% endraw %}
