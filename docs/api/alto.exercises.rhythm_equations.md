---
title: alto.exercises.rhythm_equations
parent: api
package: alto.exercises
permalink: /api/alto.exercises.rhythm_equations/
---
{% raw %}
Build balanced rhythm equations with exact operator counts.

**Examples**

```text
An equation with one operation per side can compare a sum to a product.
```

## equation_tokens

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

- `rng` (*random.Random*): Chooses the grouping, total, signs and symbols.
- `ordinary` (*dict*): Single note and rest names by duration in sixteenth notes.
- `grouped` (*tuple of dict*): Separate tables of tied and beamed names by duration.
- `left` (*int*): Operator count before the equals sign.
- `right` (*int*): Operator count after the equals sign.
- `operators` (*tuple of str*): Signs allowed on the left and, by default, on the right.
- `right_operators` (*tuple of str or None*): Separate selection of signs for the right side.
- `parentheses` (*bool*): Whether an expression can group operations with parentheses.

**Returns**

- *list of str*: Equation tokens, or an empty list if no equation fits.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> equation_tokens(random.Random(0), ordinary={4: ["q"]},
...     grouped=(), left=1, right=1, operators=("+",))
['q', '+', 'q', '=', 'q', '+', 'q']
```

## counted_operands

<div class="api-signature" markdown="1">

```python
def counted_operands(ordinary: dict[float, list[str]]) -> dict[float, list[str]]
```

{% endraw %}{% include api-source.html name="counted_operands" line=372 %}{% raw %}

</div>

Supply counts for totals without a selected single symbol.

**Parameters**

- `ordinary` (*dict*): Selected symbols by duration.

**Returns**

- *dict*: Count and unit tokens indexed by their combined duration.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> counted_operands({4: ["quarter"]})[12]
['3:quarter']
```

## number_question

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

- `rng` (*random.Random*): Selects the blank and counting unit.
- `tokens` (*list of str*): Balanced equation. Each factor scales the preceding subtotal, with any additive prefix enclosed in parentheses.
- `ordinary` (*dict*): Selected note and rest symbols by duration.

**Returns**

- *Question*: A numeric answer with a unit caption when counting durations.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> number_question(random.Random(0),
...     tokens=["half", "÷", "2", "=", "quarter"],
...     ordinary={4: ["quarter"], 8: ["half"]}).answer
'2'
```
{% endraw %}
