---
title: choose
parent: alto.learning.scheduler
api_module: alto.learning.scheduler
package: alto.learning
permalink: /api/alto.learning.scheduler/function-choose/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def choose(
    options: Sequence[T],
    *,
    weights: Sequence[float],
    rng: random.Random,
) -> T
```

{% endraw %}{% include api-source.html name="choose" line=284 %}{% raw %}

</div>

Pick one option at random, in proportion to its weight.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `options` | `sequence of T` | The things to choose from. |
| `weights` | `sequence of float` | One weight per option; a larger weight makes it more likely. Keyword-only. |
| `rng` | `random.Random` | The random number generator to draw with. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `T` | The chosen option. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> choose(
...     ["a", "b"],
...     weights=[1.0, 0.0],
...     rng=random.Random(0),
... )
'a'
```
{% endraw %}
