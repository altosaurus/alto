---
title: save_key_settings
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_key_settings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_key_settings(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str,
) -> None
```

{% endraw %}{% include api-source.html name="save_key_settings" line=801 %}{% raw %}

</div>

Save the settings of a key exercise: its clefs, scales and key
signatures, and the options of the kind of exercise it is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `KeySignatureSettings` | The settings to save; the scale and Order of Keys exercises save their own options too. |
| `prefix` | `str` | What the exercise's saved settings are filed under, such as "keySignatures". Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> saved_ = settings.ScaleConstructionSettings(
...     modes={"Major (Ionian)", "Dorian"},
...     steps=True,
... )
>>> save_key_settings(
...     saved_, prefix="doctestScales"
... )
>>> loaded_ = (
...     settings.ScaleConstructionSettings()
... )
>>> _load_key_settings(
...     loaded_, prefix="doctestScales"
... )
>>> sorted(loaded_.modes), loaded_.steps
(['Dorian', 'Major (Ionian)'], True)
>>> store().remove("doctestScales")
```
{% endraw %}
