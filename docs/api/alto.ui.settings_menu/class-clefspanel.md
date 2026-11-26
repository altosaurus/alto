---
title: ClefsPanel
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-clefspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ClefsPanel(ExerciseSettingsPanel)
```

{% endraw %}{% include api-source.html name="ClefsPanel" line=1851 %}{% raw %}

</div>

A settings pane with a Clefs page, whose checkboxes choose the clefs
that are asked about.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `ClefChoice` | The settings being edited. |
| `boxes` | `dict of str to QCheckBox` | The checkbox of each clef. |
| `clef_pictures` | `ClefPictures` | The clefs shown in the menu's Clefs row. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.ui.settings_panel import (
...     ClefBasicsSettingsPanel,
... )
>>> isinstance(
...     ClefBasicsSettingsPanel(
...         settings.ClefBasicsSettings()
...     ),
...     ClefsPanel,
... )
True
```
{% endraw %}
