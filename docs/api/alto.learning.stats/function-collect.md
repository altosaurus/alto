---
title: collect
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/function-collect/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def collect(
    db: Database,
    *,
    profile_ids: list[int] | None,
    exercise: str | None = None,
    since: float | None = None,
    now: float | None = None,
    hardest: int = 8,
    volume_granularity: str | None = None,
) -> Stats
```

{% endraw %}{% include api-source.html name="collect" line=755 %}{% raw %}

</div>

Work out everything the statistics screen shows.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `db` | `Database` | Where the answers are. |
| `profile_ids` | `list of int or None` | The profiles to include; every profile if None. Keyword-only. |
| `exercise` | `str or None, default None` | Only this exercise (its class name); every exercise if None. Keyword-only. |
| `since` | `float or None, default None` | Only answers from this timestamp on; the whole history if None. Keyword-only. |
| `now` | `float or None, default None` | The current time as a timestamp; the clock is used if None. Keyword-only. |
| `hardest` | `int, default 8` | How many questions to list as needing practice. Keyword-only. |
| `volume_granularity` | `str or None, default None` | Group question counts by hour, day, week or month. None follows the timeframe. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Stats` | The totals, the per-period buckets, the per-exercise figures and the hardest questions. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> database = Database()
>>> ada = database.add_profile("Ada")
>>> database.add_attempt(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
...     attempt_no=1,
...     answer="C",
...     correct=True,
...     duration_ms=4000,
...     answered_at=1000.0,
... )
>>> stats = collect(
...     database,
...     profile_ids=[ada.id],
...     now=1060.0,
... )
>>> (
...     stats.questions,
...     stats.median_seconds,
...     stats.practice_seconds,
... )
(1, 4.0, 4.0)
>>> collect(
...     database, profile_ids=[999], now=1060.0
... ).questions  # nobody has answered anything
0
```
{% endraw %}
