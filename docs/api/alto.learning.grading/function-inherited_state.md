---
title: inherited_state
parent: alto.learning.grading
api_module: alto.learning.grading
package: alto.learning
permalink: /api/alto.learning.grading/function-inherited_state/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def inherited_state(
    key: str,
    *,
    source: str,
    state: str,
    due: float,
    rating: Rating,
) -> str
```

{% endraw %}{% include api-source.html name="inherited_state" line=114 %}{% raw %}

</div>

Translate one saved calendar schedule into the other scheduler's
initial state.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | Card identity. |
| `source` | `str` | Scheduler that produced the grade. |
| `state` | `str` | Serialized source state. |
| `due` | `float` | Original due timestamp. |
| `rating` | `Rating` | Last calendar grade. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Destination state with the same due date and learning phase. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> result = inherited_state(
...     "abc",
...     source="SM-2",
...     state="[8, 180, 2.5]",
...     due=200 * DAY,
...     rating=Rating.Good,
... )
>>> Card.from_json(result).stability
180.0
```
{% endraw %}
