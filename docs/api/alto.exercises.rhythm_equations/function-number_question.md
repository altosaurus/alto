---
title: number_question
parent: alto.exercises.rhythm_equations
api_module: alto.exercises.rhythm_equations
package: alto.exercises
permalink: /api/alto.exercises.rhythm_equations/function-number_question/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def number_question(
    rng: random.Random,
    *,
    tokens: list[str],
    ordinary: dict[float, list[str]],
) -> Question
```

{% endraw %}{% include api-source.html name="number_question" line=445 %}{% raw %}

</div>

Hide a numeric factor, or count a duration in an explicit unit.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Selects the blank and counting unit. |
| `tokens` | `list of str` | Balanced equation. Each factor scales the preceding subtotal, with any additive prefix enclosed in parentheses. |
| `ordinary` | `dict` | Selected note and rest symbols by duration. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A numeric answer with a unit caption when counting durations. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> number_question(random.Random(0),
...     tokens=["half", "÷", "2", "=", "quarter"],
...     ordinary={4: ["quarter"], 8: ["half"]}).answer
'2'
```
{% endraw %}
