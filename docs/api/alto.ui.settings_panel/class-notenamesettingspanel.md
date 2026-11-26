---
title: NoteNameSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-notenamesettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NoteNameSettingsPanel(
    cfg: NoteNameSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="NoteNameSettingsPanel" line=264 %}{% raw %}

</div>

Bases: `NoteAnswerSettingsPanel`

The settings of the note identification exercise: a menu leading to
a page for each group of settings.

Two layers: the menu (Clefs, Range, Key signatures, Note values,
Note names, Accidentals and Octave) and a page for
each. Edits are live: each changes the settings, saves them and
emits `changed`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `NoteNameSettings` | The settings being edited. |
| `stack` | `SlideStack` | The menu and its pages. |
| `boxes` | `dict of str to QCheckBox` | The clef checkboxes. |
| `key_boxes` | `dict of int to QCheckBox` | The key signature checkboxes. |
| `value_boxes` | `dict of str to QCheckBox` | The note value checkboxes. |
| `naming_radios` | `dict of str to QRadioButton` | The letters and solfège choices, plus caret and function notation in the Scale degrees group. |
| `octave_row` | `ToggleRow` | Whether the answer must include the written octave. |
| `range_editors` | `dict of str to RangeEditor` | The range editor of each clef in use, built when the Range page opens. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = NoteNameSettingsPanel(
...     NoteNameSettings()
... )
>>> panel.cfg.active_clefs()
['treble', 'bass']
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `NoteNameSettings` | The settings to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = NoteNameSettingsPanel(
...     NoteNameSettings()
... )
>>> panel.stack.count()  # the menu and five pages
6
```
{% endraw %}
