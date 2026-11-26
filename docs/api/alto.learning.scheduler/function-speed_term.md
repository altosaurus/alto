---
title: speed_term
parent: alto.learning.scheduler
api_module: alto.learning.scheduler
package: alto.learning
permalink: /api/alto.learning.scheduler/function-speed_term/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def speed_term(
    seconds: float,
    *,
    par_seconds: float,
) -> float
```

{% endraw %}{% include api-source.html name="speed_term" line=110 %}{% raw %}

</div>

Return the strain change for how long the first answer took.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `seconds` | `float` | How long the first answer took. |
| `par_seconds` | `float` | How long a good first answer takes for this exercise. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | Negative when the answer was quick (down to `-FAST_BONUS`), zero at par, and positive when it was slow (up to `SLOW_PENALTY`). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> speed_term(
...     1.0, par_seconds=10.0
... )  # at or under half of par: the full bonus
-0.6
>>> round(speed_term(7.5, par_seconds=10.0), 2)
-0.3
>>> round(speed_term(25.0, par_seconds=10.0), 2)
0.5
>>> speed_term(
...     100.0, par_seconds=10.0
... )  # four times par or more: the full penalty
1.0
```
{% endraw %}
