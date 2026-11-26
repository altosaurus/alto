---
title: ResponseTimeDialog
parent: alto.ui.response_times
api_module: alto.ui.response_times
package: alto.ui
permalink: /api/alto.ui.response_times/class-responsetimedialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ResponseTimeDialog(
    learner: Learner,
    *,
    parent: QWidget,
    exercise: str | None = None,
)
```

{% endraw %}{% include api-source.html name="ResponseTimeDialog" line=30 %}{% raw %}

</div>

Bases: `QDialog`

Inspect recent correct first answers and adjust the profile's
automatic grading bands.

**Constructor**

Open with the active profile’s saved settings and the selected
exercise’s recent timings.
{% endraw %}
