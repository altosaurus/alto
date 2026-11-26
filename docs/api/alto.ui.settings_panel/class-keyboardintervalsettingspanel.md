---
title: KeyboardIntervalSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-keyboardintervalsettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardIntervalSettingsPanel(
    cfg: settings.KeyboardIntervalSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettingsPanel" line=1612 %}{% raw %}

</div>

Bases: `KeyboardRangePanel`

Range and interval selection pages for keyboard interval
identification.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `KeyboardIntervalSettings` | The settings being edited. |
| `stack` | `SlideStack` | The settings menu, range page, and interval page. |
| `span` | `KeyboardSpan` | The draggable range selector. |
| `interval_range` | `QWidget` | The interval range controls directly below Select all. |
| `interval_slider` | `IntervalRangeSlider` | The two-handle interval selector. |
| `interval_low_label, interval_high_label` | `FieldComboBox` | Clickable endpoint notation with scrollable interval lists. |
| `interval_page` | `ChoiceChecklist` | The interval checkboxes, keyed by distance in half steps. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = KeyboardIntervalSettingsPanel(
...     settings.KeyboardIntervalSettings()
... )
>>> panel.stack.count()
4
```

**Constructor**

Build the range selector and interval checklist.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `KeyboardIntervalSettings` | The settings to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = KeyboardIntervalSettingsPanel(
...     settings.KeyboardIntervalSettings()
... )
>>> (
...     panel.low_label.text(),
...     panel.high_label.text(),
... )
('C3', 'C5')
```
{% endraw %}
