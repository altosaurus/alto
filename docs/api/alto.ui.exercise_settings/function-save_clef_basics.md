---
title: save_clef_basics
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_clef_basics/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_clef_basics(cfg: settings.ClefBasicsSettings) -> None
```

{% endraw %}{% include api-source.html name="save_clef_basics" line=1099 %}{% raw %}

</div>

Save clef basics settings, the form `load_clef_basics` reads.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ClefBasicsSettings` | The settings to save. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_clef_basics(
...     settings.ClefBasicsSettings(
...         clefs={"french", "treble"},
...         question_type="identification",
...     )
... )
>>> (
...     str(store().value("clefBasics/clefs")),
...     str(store().value("clefBasics/type")),
... )
('treble,french', 'identification')
>>> store().remove("clefBasics")
```
{% endraw %}
