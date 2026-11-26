---
title: KeySignatureSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-keysignaturesettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeySignatureSettingsPanel(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str = 'keySignatures',
    keys_title: str = 'Key signatures',
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeySignatureSettingsPanel" line=2567 %}{% raw %}

</div>

Bases: `ClefsPanel`

The settings of a key signature exercise: a menu with a page for
each group of settings.

The same panel serves key signature identification, key signature
construction and both scale exercises, each saving
under its own name.

The menu has Clefs, Scales and Key signatures. Both scale exercises
have independent staff and scale key choices;
construction also has Octave and Steps switches. Edits are live:
each changes the settings, saves them and emits `changed`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `KeySignatureSettings` | The settings being edited. |
| `prefix` | `str` | What the settings are saved under, such as "keySignatures". |
| `stack` | `SlideStack` | The menu and its pages. |
| `boxes` | `dict of str to QCheckBox` | The clef checkboxes. |
| `modes` | `ChoiceChecklist` | The scales (major, minor and the modes). |
| `key_list` | `KeyChecklist` | The key signatures (of the scales, in scale construction). |
| `staff_key_list` | `KeyChecklist or None` | The key signatures that may be drawn on the staff; only scale construction has it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = KeySignatureSettingsPanel(
...     settings.KeySignatureSettings()
... )
>>> panel.modes_row.value.text()
'2 of 7'
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `KeySignatureSettings` | The settings to edit. |
| `prefix` | `str, default "keySignatures"` | What the settings are saved under. Keyword-only. |
| `keys_title` | `str, default "Key signatures"` | Title for the signature checklist when the exercise uses a single list. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatureSettingsPanel(
...     settings.KeySignatureSettings()
... ).stack.count()  # the menu and three pages
4
```
{% endraw %}
