---
title: load_scale_identification
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_scale_identification/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_scale_identification() -> None
```

{% endraw %}{% include api-source.html name="load_scale_identification" line=955 %}{% raw %}

</div>

Load the saved scale identification options independently of scale
construction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_scale_identification()
>>> settings.scale_identification.active_staff_keys()
[0]
```
{% endraw %}
