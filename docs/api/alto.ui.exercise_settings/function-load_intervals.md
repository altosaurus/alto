---
title: load_intervals
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_intervals/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_intervals(
    cfg: settings.IntervalSettings | None = None,
    *,
    prefix: str = 'intervals',
) -> None
```

{% endraw %}{% include api-source.html name="load_intervals" line=558 %}{% raw %}

</div>

Restore the saved staff interval options, keeping valid choices and
per-clef ranges.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `IntervalSettings or None` | Settings to populate. Defaults to Interval Identification. |
| `prefix` | `str` | Independent settings-store group for the exercise. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_intervals()
>>> bool(settings.intervals.active_clefs())
True
```
{% endraw %}
