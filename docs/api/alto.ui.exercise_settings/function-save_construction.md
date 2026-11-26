---
title: save_construction
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_construction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_construction(cfg: settings.ConstructionSettings) -> None
```

{% endraw %}{% include api-source.html name="save_construction" line=423 %}{% raw %}

</div>

Save the note construction settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ConstructionSettings` | The settings to save. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings.construction.degrees = {1, 3}
>>> save_construction(settings.construction)
>>> str(store().value("construction/degrees"))
'1,3'
>>> settings.construction.degrees = set(
...     range(1, 8)
... )
>>> save_construction(settings.construction)
```
{% endraw %}
