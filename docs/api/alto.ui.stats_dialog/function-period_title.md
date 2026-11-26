---
title: period_title
parent: alto.ui.stats_dialog
api_module: alto.ui.stats_dialog
package: alto.ui
permalink: /api/alto.ui.stats_dialog/function-period_title/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def period_title(
    start: datetime,
    *,
    granularity: str,
) -> str
```

{% endraw %}{% include api-source.html name="period_title" line=168 %}{% raw %}

</div>

Name a chart period in words, for the heading of its list of
answers.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `start` | `datetime` | The start of the period. |
| `granularity` | `str` | "hour", "day", "week" or "month", as `Stats.granularity` says. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | For example "Mon 5 Jan 2026", "Week of Mon 5 Jan 2026" or "January 2026". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> period_title(
...     datetime(2026, 1, 5, 14),
...     granularity="hour",
... )
'Mon 5 Jan 2026, 14:00'
>>> period_title(
...     datetime(2026, 1, 5), granularity="day"
... )
'Mon 5 Jan 2026'
>>> period_title(
...     datetime(2026, 1, 5), granularity="week"
... )
'Week of Mon 5 Jan 2026'
>>> period_title(
...     datetime(2026, 1, 1),
...     granularity="month",
... )
'January 2026'
```
{% endraw %}
