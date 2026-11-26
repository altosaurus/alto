---
title: weight
parent: alto.learning.scheduler
api_module: alto.learning.scheduler
package: alto.learning
permalink: /api/alto.learning.scheduler/function-weight/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def weight(
    strain: float | None,
    *,
    last_seen: float | None,
    now: float,
) -> float
```

{% endraw %}{% include api-source.html name="weight" line=230 %}{% raw %}

</div>

Return how likely a question is to be picked, relative to the
others.

A question just seen is held back for a while, long for an easy one
and short for a hard one, so what you have
learned is not repeated right away but what you struggle with
returns within the minute.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `strain` | `float or None` | The question's strain, or None for one never answered. |
| `last_seen` | `float or None` | When it was last answered (a timestamp), or None if never. Keyword-only. |
| `now` | `float` | The current time (a timestamp). Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | A positive number; a larger one means the question is more likely to come up. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> round(
...     weight(None, last_seen=None, now=0.0), 2
... )  # a new question
2.46
>>> round(
...     weight(3.0, last_seen=0.0, now=1e9), 2
... )  # a hard question, long unseen
6.05
>>> round(
...     weight(3.0, last_seen=100.0, now=100.0),
...     3,
... )  # the same, just seen: held back
0.121
```
{% endraw %}
