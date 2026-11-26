---
title: NoteConstructionSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-noteconstructionsettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NoteConstructionSettingsPanel(
    cfg: settings.ConstructionSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="NoteConstructionSettingsPanel" line=820 %}{% raw %}

</div>

Bases: `ClefsPanel`

The settings of the note construction exercise: a menu with a page
for the staff and one for the keys.

The menu has Clefs, Staff Key, Question Type, and Octave. Edits are
live: each changes the settings, saves them and
emits `changed`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `ConstructionSettings` | The settings being edited. |
| `stack` | `SlideStack` | The menu and its pages. |
| `boxes` | `dict of str to QCheckBox` | The clef checkboxes, including the grand staff. |
| `key_tabs` | `QTabWidget` | The key signature sub-page. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = NoteConstructionSettingsPanel(
...     settings.ConstructionSettings()
... )
>>> sorted(panel.boxes)[:3]
['alto', 'baritone', 'bass']
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ConstructionSettings` | The settings to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstructionSettingsPanel(
...     settings.ConstructionSettings()
... ).stack.count()
4
```
{% endraw %}
