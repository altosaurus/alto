---
title: Stats
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/class-stats/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Stats(
    questions: int = 0,
    *,
    first_right: int = 0,
    attempts: int = 0,
    median_seconds: float | None = None,
    practice_seconds: float = 0.0,
    days_practiced: int = 0,
    granularity: str = 'day',
    buckets: list[Bucket] = field(default_factory=list),
    volume_buckets: list[Bucket] = field(default_factory=list),
    by_exercise: list[ExerciseStats] = field(default_factory=list),
    hardest: list[HardQuestion] = field(default_factory=list),
)
```

{% endraw %}{% include api-source.html name="Stats" line=239 %}{% raw %}

</div>

Everything the statistics screen shows.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `questions` | `int, default 0` | How many questions were answered, each counted once. |
| `first_right` | `int, default 0` | How many were right on the first answer. Keyword-only. |
| `attempts` | `int, default 0` | How many answers were given in all, including repeats. Keyword-only. |
| `median_seconds` | `float or None` | The typical time to a first answer. Keyword-only. |
| `practice_seconds` | `float, default 0.0` | Time spent practicing, with a cap on each answer so leaving the app open does not inflate it. Keyword-only. |
| `days_practiced` | `int, default 0` | On how many different days there were answers. Keyword-only. |
| `granularity` | `str, default "day"` | The size of the chart periods: "hour", "day", "week" or "month". Keyword-only. |
| `buckets` | `list of Bucket` | One per period, oldest first. Keyword-only. |
| `volume_buckets` | `list of Bucket` | Period counts for the questions answered chart. These share the trend buckets when their periods match. Keyword-only. |
| `by_exercise` | `list of ExerciseStats` | One per exercise practiced, sorted by name. Keyword-only. |
| `hardest` | `list of HardQuestion` | The questions that need most practice. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Stats().accuracy is None  # nothing answered yet
True
>>> Stats(
...     4, first_right=3, attempts=6
... ).attempts_per_question
1.5
```

## Stats.accuracy

<div class="api-signature" markdown="1">

```python
@property
def accuracy() -> float | None
```

{% endraw %}{% include api-source.html name="Stats.accuracy" line=296 %}{% raw %}

</div>

Return the percentage of questions that were right on the first
try.

**Returns**

| Type | Description |
| --- | --- |
| `float or None` | 0 to 100, or None if no questions were answered. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Stats(4, first_right=3).accuracy
75.0
```

## Stats.attempts_per_question

<div class="api-signature" markdown="1">

```python
@property
def attempts_per_question() -> float | None
```

{% endraw %}{% include api-source.html name="Stats.attempts_per_question" line=318 %}{% raw %}

</div>

Return the average number of answers it took per question.

**Returns**

| Type | Description |
| --- | --- |
| `float or None` | 1.0 if every question was answered right on the first try; None if no questions were answered. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Stats(4, attempts=5).attempts_per_question
1.25
```
{% endraw %}
