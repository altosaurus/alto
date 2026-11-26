---
title: save_keyboard_intervals
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_keyboard_intervals/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_keyboard_intervals(cfg: settings.KeyboardIntervalSettings) -> None
```

{% endraw %}{% include api-source.html name="save_keyboard_intervals" line=315 %}{% raw %}

</div>

Save the keyboard interval range and selected distances.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `KeyboardIntervalSettings` | The settings to save. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_keyboard_intervals(
...     settings.KeyboardIntervalSettings()
... )
>>> int(store().value("keyboardIntervals/low"))
48
```
{% endraw %}
