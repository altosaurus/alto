---
title: settings_inversion_names
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/function-settings_inversion_names/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def settings_inversion_names() -> tuple[str, ...]
```

{% endraw %}{% include api-source.html name="settings_inversion_names" line=3484 %}{% raw %}

</div>

Return the inversions as they are written in the settings.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of str` | 'Root position', '1st inversion', '2nd inversion' and '3rd inversion'. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_inversion_names()
('Root position', '1st inversion', '2nd inversion', '3rd inversion')
```
{% endraw %}
