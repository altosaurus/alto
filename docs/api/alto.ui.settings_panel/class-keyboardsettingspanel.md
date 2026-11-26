---
title: KeyboardSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-keyboardsettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardSettingsPanel(
    cfg: settings.KeyboardSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyboardSettingsPanel" line=482 %}{% raw %}

</div>

Bases: `KeyboardRangePanel`

The settings of the keyboard exercise: a menu with a page for the
range of keys.

The menu includes Range, Black keys, Octave number, Key signatures
and Note names.
Edits are live: each changes the settings, saves them
and emits `changed`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `KeyboardSettings` | The settings being edited. |
| `stack` | `SlideStack` | The menu and its pages. |
| `span` | `KeyboardSpan` | The miniature piano on the Range page, which can be dragged to choose the keys. |
| `low_label, high_label` | `QLabel` | The names of the lowest and highest key asked. |
| `key_page` | `KeySignaturePage` | The key signature sub-page. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = KeyboardSettingsPanel(
...     settings.KeyboardSettings()
... )
>>> (
...     panel.low_label.text(),
...     panel.high_label.text(),
... )
('C3', 'C5')
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `KeyboardSettings` | The settings to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardSettingsPanel(
...     settings.KeyboardSettings()
... ).stack.count()  # the menu, range, keys and note names
4
```
{% endraw %}
