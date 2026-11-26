---
title: save_circle
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_circle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_circle(cfg: settings.CircleSettings) -> None
```

{% endraw %}{% include api-source.html name="save_circle" line=1183 %}{% raw %}

</div>

Save the circle of fifths settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `CircleSettings` | The settings to save. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_circle(
...     settings.CircleSettings(scheme="ink")
... )
>>> store().value("circle/scheme")
'ink'
>>> store().remove("circle")
```
{% endraw %}
