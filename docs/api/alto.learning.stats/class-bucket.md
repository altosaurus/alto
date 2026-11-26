---
title: Bucket
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/class-bucket/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Bucket(
    start: datetime,
    *,
    label: str,
    questions: int = 0,
    first_right: int = 0,
    times: list[float] = field(default_factory=list),
)
```

{% endraw %}{% include api-source.html name="Bucket" line=64 %}{% raw %}

</div>

The answers given in one period (an hour, day, week or month), for
the charts.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `start` | `datetime` | When the period begins. |
| `label` | `str` | What to call the period on a chart axis. Keyword-only. |
| `questions` | `int, default 0` | How many questions were answered in it. Keyword-only. |
| `first_right` | `int, default 0` | How many of those were right on the first answer. Keyword-only. |
| `times` | `list of float` | Seconds to the first answer, one per question. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bucket = Bucket(
...     datetime(2026, 1, 5),
...     label="Jan 5",
...     questions=2,
...     first_right=1,
...     times=[2.0, 4.0],
... )
>>> bucket.accuracy, bucket.median_seconds
(50.0, 3.0)
```

## Bucket.accuracy

<div class="api-signature" markdown="1">

```python
@property
def accuracy() -> float | None
```

{% endraw %}{% include api-source.html name="Bucket.accuracy" line=105 %}{% raw %}

</div>

Return the percentage of questions in the period that were right
on the first try.

**Returns**

| Type | Description |
| --- | --- |
| `float or None` | 0 to 100, or None if no questions were answered. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Bucket(
...     datetime(2026, 1, 5),
...     label="Jan 5",
...     questions=4,
...     first_right=3,
... ).accuracy
75.0
>>> Bucket(
...     datetime(2026, 1, 5), label="Jan 5"
... ).accuracy is None
True
```

## Bucket.median_seconds

<div class="api-signature" markdown="1">

```python
@property
def median_seconds() -> float | None
```

{% endraw %}{% include api-source.html name="Bucket.median_seconds" line=136 %}{% raw %}

</div>

Return the typical time to a first answer in the period.

**Returns**

| Type | Description |
| --- | --- |
| `float or None` | The median, in seconds, or None if no questions were answered. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Bucket(
...     datetime(2026, 1, 5),
...     label="Jan 5",
...     times=[1.0, 2.0, 9.0],
... ).median_seconds
2.0
```
{% endraw %}
