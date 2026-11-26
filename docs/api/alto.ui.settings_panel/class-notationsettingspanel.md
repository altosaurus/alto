---
title: NotationSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-notationsettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NotationSettingsPanel()
```

{% endraw %}{% include api-source.html name="NotationSettingsPanel" line=3121 %}{% raw %}

</div>

Bases: `ExerciseSettingsPanel`

Choose the question type and the notation terms to practice.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Trill" in NotationSettingsPanel().terms.boxes
True
```

**Constructor**

Build the settings menu and its Question Type and Terms pages.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(
...     NotationSettingsPanel().terms.boxes
... ) == len(settings.NOTATION_TERMS)
True
```
{% endraw %}
