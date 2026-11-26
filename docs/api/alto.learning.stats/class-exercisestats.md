---
title: ExerciseStats
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/class-exercisestats/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ExerciseStats(
    exercise: str,
    *,
    questions: int,
    accuracy: float,
    median_seconds: float,
)
```

{% endraw %}{% include api-source.html name="ExerciseStats" line=159 %}{% raw %}

</div>

How practice is going on one exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `exercise` | `str` | The exercise's class name. |
| `questions` | `int` | How many questions were answered. Keyword-only. |
| `accuracy` | `float` | The percentage right on the first try. Keyword-only. |
| `median_seconds` | `float` | The typical time to a first answer, in seconds. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ExerciseStats(
...     "NoteNames",
...     questions=40,
...     accuracy=87.5,
...     median_seconds=3.2,
... ).accuracy
87.5
```
{% endraw %}
