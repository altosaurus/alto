---
title: pick_distractors
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/function-pick_distractors/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def pick_distractors(
    correct: str,
    *,
    pool: list[str],
    n: int,
    rng: random.Random,
) -> list[str]
```

{% endraw %}{% include api-source.html name="pick_distractors" line=1738 %}{% raw %}

</div>

Choose wrong answers to offer alongside the right one, and shuffle
them all.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `correct` | `str` | The right answer. It is always in the result. |
| `pool` | `list of str` | Where the wrong answers come from; repeats and the right answer are ignored. Keyword-only. |
| `n` | `int` | How many wrong answers to include (fewer if the pool has fewer). Keyword-only. |
| `rng` | `random.Random` | The random number generator used to choose and shuffle. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The right answer and up to `n` others, in a random order. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> choices_ = pick_distractors(
...     "C",
...     pool=["C", "D", "E", "F"],
...     n=2,
...     rng=random.Random(0),
... )
>>> len(choices_), "C" in choices_
(3, True)
```
{% endraw %}
