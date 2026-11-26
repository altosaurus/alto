---
title: PackSettingsPanel
parent: alto.ui.pack_settings_panel
api_module: alto.ui.pack_settings_panel
package: alto.ui
permalink: /api/alto.ui.pack_settings_panel/class-packsettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackSettingsPanel(
    exercise: type[PackExercise],
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="PackSettingsPanel" line=149 %}{% raw %}

</div>

Bases: `NoteAnswerSettingsPanel`

The settings a plugin declared for one of its note exercises, drawn
from a fixed set of controls.

The plugin picks which controls appear: a switch for its own sound,
a range selector on one clef, and switches for
accidentals and for the octave. Edits are live: each changes the
options, saves them and emits `changed`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `exercise` | `type of PackExercise` | The exercise whose options are edited. |
| `cfg` | `PackExerciseSettings` | The options being edited. |
| `range_row` | `MenuRow` | The Range row, present only if the plugin declared a range. |
| `sound_row` | `ToggleRow or None` | The plugin sound switch, if declared. |
| `accidentals_row` | `ToggleRow or None` | The accidentals switch, if declared. |
| `octave_row` | `ToggleRow or None` | The octave switch, if declared. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     controls = {"octave": True}
>>> panel = PackSettingsPanel(Demo)
>>> panel.octave_row is not None and not hasattr(
...     panel, "range_row"
... )
True
>>> _ = settings.pack_exercises.pop("Demo")
```

**Constructor**

Build the menu and, if the plugin offers a range, its page.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `exercise` | `type of PackExercise` | The exercise to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Sounds(PackExercise):
...     controls = {"sound": "Demo sound"}
>>> panel = PackSettingsPanel(Sounds)
>>> panel.stack.count()
2
>>> _ = settings.pack_exercises.pop("Sounds")
```
{% endraw %}
