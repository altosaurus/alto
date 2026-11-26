---
title: ScaleKeyPicker
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-scalekeypicker/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ScaleKeyPicker(
    *,
    major_keys: set[int],
    minor_keys: set[int],
)
```

{% endraw %}{% include api-source.html name="ScaleKeyPicker" line=2661 %}{% raw %}

</div>

Bases: `QTabWidget`

Select major and minor keys independently.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleKeyPicker(
...     major_keys={0}, minor_keys={-2}
... ).count()
2
```

**Constructor**

Build one checklist per mode.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `major_keys` | `set of int` | Selected major signatures. Keyword-only. |
| `minor_keys` | `set of int` | Selected minor signatures. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleKeyPicker(
...     major_keys=set(), minor_keys={0}
... ).currentIndex()
1
```
{% endraw %}
