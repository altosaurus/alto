---
title: alto.exercises.rhythm_equations
parent: api
package: alto.exercises
api_components: [{"title": "counted_operands", "url": "/api/alto.exercises.rhythm_equations/function-counted_operands/"}, {"title": "equation_tokens", "url": "/api/alto.exercises.rhythm_equations/function-equation_tokens/"}, {"title": "number_question", "url": "/api/alto.exercises.rhythm_equations/function-number_question/"}]
permalink: /api/alto.exercises.rhythm_equations/
---
{% raw %}
Build balanced rhythm equations with exact operator counts.

## Functions

- [`equation_tokens`](function-equation_tokens/) — Choose a shared total, then build both sides backwards from it.
- [`counted_operands`](function-counted_operands/) — Supply counts for totals without a selected single symbol.
- [`number_question`](function-number_question/) — Hide a numeric factor, or count a duration in an explicit unit.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```text
An equation with one operation per side can compare a sum to a product.
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"equation_tokens": "function-equation_tokens/", "counted_operands": "function-counted_operands/", "number_question": "function-number_question/"}</script>
{% include api-fragments.html %}
