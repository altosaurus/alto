---
title: period_end
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/function-period_end/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def period_end(
    start: datetime,
    *,
    granularity: str,
) -> datetime
```

{% endraw %}{% include api-source.html name="period_end" line=495 %}{% raw %}

</div>

Return the moment a chart period ends, which is when the next one
begins.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `start` | `datetime` | The start of the period, as `Bucket.start` gives it. |
| `granularity` | `str` | "hour", "day", "week" or "month", as `Stats.granularity` says. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `datetime` | The start of the following period. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> period_end(
...     datetime(2026, 1, 5), granularity="week"
... )
datetime.datetime(2026, 1, 12, 0, 0)
>>> period_end(
...     datetime(2026, 12, 1),
...     granularity="month",
... )
datetime.datetime(2027, 1, 1, 0, 0)
```
{% endraw %}
