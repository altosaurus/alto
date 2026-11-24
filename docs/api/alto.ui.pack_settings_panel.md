---
title: alto.ui.pack_settings_panel
parent: api
package: alto.ui
permalink: /api/alto.ui.pack_settings_panel/
---
{% raw %}
The settings panels of exercises that plugins add.

A plugin exercise declares the controls it wants (a range, a sound,
accidentals ...) and gets a panel built from them, like
the built-in exercises' panels. Its options are saved under the
exercise's name.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> COMMIT_DELAY_MS
150
```

## PackSettingsPanel

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

- `exercise` (*type of PackExercise*): The exercise whose options are edited.
- `cfg` (*PackExerciseSettings*): The options being edited.
- `range_row` (*MenuRow*): The Range row, present only if the plugin declared a range.
- `sound_row` (*ToggleRow or None*): The plugin sound switch, if declared.
- `accidentals_row` (*ToggleRow or None*): The accidentals switch, if declared.
- `octave_row` (*ToggleRow or None*): The octave switch, if declared.

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

- `exercise` (*type of PackExercise*): The exercise to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Sounds(PackExercise):
...     controls = {"sound": "Demo sound"}
>>> panel = PackSettingsPanel(Sounds)
>>> panel.stack.count()
2
>>> _ = settings.pack_exercises.pop("Sounds")
```

## PackKeyboardSettingsPanel

<div class="api-signature" markdown="1">

```python
PackKeyboardSettingsPanel(
    exercise: type[PackExercise],
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="PackKeyboardSettingsPanel" line=438 %}{% raw %}

</div>

Bases: `KeyboardRangePanel`

The settings a plugin declared for a keyboard interval exercise: its
sound, the range of keys, and the intervals.

The plugin picks which controls appear. Edits are live: each changes
the options, saves them and emits `changed`.

**Attributes**

- `exercise` (*type of PackExercise*): The exercise whose options are edited.
- `cfg` (*PackExerciseSettings*): The options being edited.
- `stack` (*SlideStack*): The settings menu, then the range page and the intervals page, as the plugin offers them.
- `sound_row` (*ToggleRow or None*): The plugin sound switch, if declared.
- `range_row` (*MenuRow or None*): The Range row, if declared.
- `span` (*KeyboardSpan or None*): The draggable range selector, if a range is declared.
- `interval_page` (*ChoiceChecklist or None*): The interval checkboxes, keyed by interval name, if a choice of intervals is declared.
- `manual_page` (*ChoiceChecklist or None*): The keyboard checkboxes, keyed by keyboard name, if a choice of manuals is declared.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     controls = {
...         "range": True,
...         "intervals": True,
...         "manuals": True,
...     }
...     spec = {"type": "keyboard-intervals"}
...     key_span, key_default = (
...         (28, 89),
...         (48, 72),
...     )
...     interval_names = ("m2", "M2", "m3")
...     manual_names = (
...         "Upper manual",
...         "Lower manual",
...     )
>>> panel = PackKeyboardSettingsPanel(Demo)
>>> (
...     panel.stack.count(),
...     panel.low_label.text(),
...     panel.high_label.text(),
... )
(4, 'C3', 'C5')
>>> _ = settings.pack_exercises.pop("Demo")
```

**Constructor**

Build the menu and the pages the plugin offers.

**Parameters**

- `exercise` (*type of PackExercise*): The exercise to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Sounds(PackExercise):
...     controls = {"sound": "Demo sound"}
...     spec = {"type": "keyboard-intervals"}
>>> panel = PackKeyboardSettingsPanel(Sounds)
>>> panel.stack.count()
2
>>> _ = settings.pack_exercises.pop("Sounds")
```

### PackKeyboardSettingsPanel.flush

<div class="api-signature" markdown="1">

```python
def flush() -> None
```

{% endraw %}{% include api-source.html name="PackKeyboardSettingsPanel.flush" line=1009 %}{% raw %}

</div>

Save the options and ask a new question now, if an edit is
waiting.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     controls = {"sound": "Demo sound"}
...     spec = {"type": "keyboard-intervals"}
>>> panel = PackKeyboardSettingsPanel(Demo)
>>> panel._sound_chosen("piano")
>>> panel.flush()
>>> panel._commit_timer.isActive()
False
>>> _ = settings.pack_exercises.pop("Demo")
```

### PackKeyboardSettingsPanel.hideEvent

<div class="api-signature" markdown="1">

```python
def hideEvent(event: QHideEvent) -> None
```

{% endraw %}{% include api-source.html name="PackKeyboardSettingsPanel.hideEvent" line=1031 %}{% raw %}

</div>

Keep an edit that is still waiting when the panel closes.

**Parameters**

- `event` (*QHideEvent*): The event.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     controls = {"sound": "Demo sound"}
...     spec = {"type": "keyboard-intervals"}
>>> panel = PackKeyboardSettingsPanel(Demo)
>>> panel._sound_chosen("piano")
>>> panel.show()
>>> panel.hide()
>>> panel._commit_timer.isActive()
False
>>> _ = settings.pack_exercises.pop("Demo")
```
{% endraw %}
