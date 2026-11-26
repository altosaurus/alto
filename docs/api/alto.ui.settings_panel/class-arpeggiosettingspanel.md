---
title: ArpeggioSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-arpeggiosettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ArpeggioSettingsPanel(
    cfg: settings.ArpeggioSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ArpeggioSettingsPanel" line=2294 %}{% raw %}

</div>

Bases: `ClefsPanel`

The settings of the arpeggio exercise: a menu with a page for each
group of settings.

The menu has Clefs, Arpeggio types, Inversions and Key signatures.
Edits are live: each changes the settings, saves them
and emits `changed`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `ArpeggioSettings` | The settings being edited. |
| `stack` | `SlideStack` | The menu and its pages. |
| `boxes` | `dict of str to QCheckBox` | The clef checkboxes. |
| `types` | `ChoiceChecklist` | The chord types. |
| `inversions` | `ChoiceChecklist` | The inversions. |
| `key_page` | `KeySignaturePage` | The key signature sub-page. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ArpeggioSettingsPanel(
...     settings.ArpeggioSettings()
... )
>>> panel.types_row.value.text()
'4 of 9'
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ArpeggioSettings` | The settings to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettingsPanel(
...     settings.ArpeggioSettings()
... ).stack.count()  # the menu and four pages
5
```
{% endraw %}
