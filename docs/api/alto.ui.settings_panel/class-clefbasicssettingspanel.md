---
title: ClefBasicsSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-clefbasicssettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ClefBasicsSettingsPanel(
    cfg: settings.ClefBasicsSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ClefBasicsSettingsPanel" line=3304 %}{% raw %}

</div>

Bases: `ClefsPanel`

The settings of the clef basics exercise: a menu with two pages,
Question Type and Clefs.

Question Type chooses between Clef Construction (put a named clef on
a blank staff) and Clef Identification (name the clef on
a staff). Clefs lists the clefs in the same groups as the other
exercises, with the French violin and subbass clefs, which
only this exercise has, at the bottom. Edits are live: each changes
the settings, saves them and emits `changed`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `ClefBasicsSettings` | The settings being edited. |
| `stack` | `SlideStack` | The menu and its two pages. |
| `types` | `dict of str to QRadioButton` | The choice of question, by key of `CLEF_QUESTION_TYPES`. |
| `boxes` | `dict of str to QCheckBox` | The checkbox of each clef. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ClefBasicsSettingsPanel(
...     settings.ClefBasicsSettings()
... )
>>> panel.stack.count()  # the menu and two pages
3
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ClefBasicsSettings` | The settings to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ClefBasicsSettingsPanel(
...     settings.ClefBasicsSettings(
...         clefs={"subbass"}
...     )
... )
>>> (
...     panel.boxes["subbass"].isChecked(),
...     list(panel.boxes)[-2:],
... )
(True, ['french', 'subbass'])
```
{% endraw %}
