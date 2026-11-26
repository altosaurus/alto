---
title: IntervalSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-intervalsettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
IntervalSettingsPanel(
    cfg: settings.IntervalSettings,
    *,
    prefix: str = 'intervals',
)
```

{% endraw %}{% include api-source.html name="IntervalSettingsPanel" line=1129 %}{% raw %}

</div>

Bases: `StaffRangePanel`

Choose the notation and answer format for written intervals.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalSettingsPanel(
...     settings.IntervalSettings()
... ).stack.count()
10
```

**Constructor**

Build the interval settings menu with direction choices under
Melodic.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `IntervalSettings` | The interval exercise settings. |
| `prefix` | `str` | Settings-store group for identification or construction. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalSettingsPanel(
...     settings.IntervalSettings()
... ).quality_row.value.text()
'Interval and Quality'
```
{% endraw %}
