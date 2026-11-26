---
title: daily_counts
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/function-daily_counts/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def daily_counts(
    db: Database,
    *,
    profile_ids: list[int] | None,
    exercise: str | None = None,
    weeks: int = 53,
    now: float | None = None,
) -> dict[date, int]
```

{% endraw %}{% include api-source.html name="daily_counts" line=635 %}{% raw %}

</div>

Return how many questions were answered on each day, for the review
heatmap.

Looks back over the last `weeks` calendar weeks up to today, in
local time. Days with no answers are left out. It
counts questions (first attempts), not attempts, like everything
else here.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `db` | `Database` | Where the answers are. |
| `profile_ids` | `list of int or None` | The profiles to include; every profile if None. Keyword-only. |
| `exercise` | `str or None, default None` | Only this exercise (its class name); every exercise if None. Keyword-only. |
| `weeks` | `int, default 53` | How many calendar weeks to look back, counting this one. Keyword-only. |
| `now` | `float or None, default None` | The current time as a timestamp; the clock is used if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of date to int` | The number of questions answered on each day that had any. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> database = Database()
>>> ada = database.add_profile("Ada")
>>> noon = datetime(
...     2026, 11, 13, 12
... ).timestamp()
>>> for i in range(3):
...     database.add_attempt(
...         ada.id,
...         exercise="NoteNames",
...         item_key=str(i),
...         attempt_no=1,
...         answer="C",
...         correct=True,
...         duration_ms=1000,
...         answered_at=noon + i,
...     )
>>> daily_counts(
...     database,
...     profile_ids=[ada.id],
...     now=noon + 60,
... )
{datetime.date(2026, 11, 13): 3}
```
{% endraw %}
