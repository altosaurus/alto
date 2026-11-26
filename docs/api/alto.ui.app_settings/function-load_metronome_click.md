---
title: load_metronome_click
parent: alto.ui.app_settings
api_module: alto.ui.app_settings
package: alto.ui
permalink: /api/alto.ui.app_settings/function-load_metronome_click/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_metronome_click() -> None
```

{% endraw %}{% include api-source.html name="load_metronome_click" line=111 %}{% raw %}

</div>

Apply the saved click or use High pip as the default.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_metronome_click()
>>> sounds.metronome_click in METRONOME_CLICKS
True
```
{% endraw %}
