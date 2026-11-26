---
title: since_for
parent: alto.ui.stats_dialog
api_module: alto.ui.stats_dialog
package: alto.ui
permalink: /api/alto.ui.stats_dialog/function-since_for/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def since_for(
    span: str | int | None,
    *,
    now: float,
) -> float | None
```

{% endraw %}{% include api-source.html name="since_for" line=86 %}{% raw %}

</div>

Return the timestamp a timeframe starts from.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `span` | `str or int or None` | "today", a number of days back, or None for all time. |
| `now` | `float` | The current time as a timestamp. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float or None` | Midnight for "today", `now` less that many days for a number, and None for all time. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> since_for(7, now=864000.0)
259200.0
>>> since_for(None, now=864000.0) is None
True
>>> 0 <= 864000.0 - since_for(
...     "today", now=864000.0
... ) < 90000  # within a day of now
True
```
{% endraw %}
