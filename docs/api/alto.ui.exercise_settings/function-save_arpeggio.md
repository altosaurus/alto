---
title: save_arpeggio
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_arpeggio/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_arpeggio(cfg: settings.ArpeggioSettings) -> None
```

{% endraw %}{% include api-source.html name="save_arpeggio" line=524 %}{% raw %}

</div>

Save the arpeggio settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ArpeggioSettings` | The settings to save. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_arpeggio(settings.arpeggio)
>>> str(
...     store().value("arpeggio/clefs")
... ) == ",".join(
...     settings.arpeggio.active_clefs()
... )
True
```
{% endraw %}
