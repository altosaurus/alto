---
title: load_keyboard_intervals
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_keyboard_intervals/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_keyboard_intervals() -> None
```

{% endraw %}{% include api-source.html name="load_keyboard_intervals" line=248 %}{% raw %}

</div>

Load keyboard interval settings, ignoring invalid values and
intervals that cannot fit.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_keyboard_intervals()
>>> settings.keyboard_intervals.bounds()[
...     0
... ] < settings.keyboard_intervals.bounds()[1]
True
```
{% endraw %}
