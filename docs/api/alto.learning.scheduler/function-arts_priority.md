---
title: arts_priority
parent: alto.learning.scheduler
api_module: alto.learning.scheduler
package: alto.learning
permalink: /api/alto.learning.scheduler/function-arts_priority/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def arts_priority(
    intervening: int,
    *,
    correct: bool,
    duration_ms: int,
) -> float
```

{% endraw %}{% include api-source.html name="arts_priority" line=66 %}{% raw %}

</div>

Score a previously answered item for Adaptive Response-Time-based
Sequencing.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `intervening` | `int` | Other first submissions since the last first submission to this item. |
| `correct` | `bool` | Whether the last first submission was correct. |
| `duration_ms` | `int` | Response time of that submission, in milliseconds. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | Priority for the next trial. A new item starts at 1.0. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> arts_priority(
...     1, correct=False, duration_ms=200
... )
2.0
>>> arts_priority(
...     0, correct=True, duration_ms=3000
... )
0.0
```
{% endraw %}
