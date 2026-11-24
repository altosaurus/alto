---
title: alto.ui.settings_panel
parent: api
package: alto.ui
permalink: /api/alto.ui.settings_panel/
---
{% raw %}
The settings panels of the built-in exercises, and `settings_panel_for`,
which picks the panel for any exercise.

Each exercise with settings has a panel: a menu of rows (Clefs, Range,
Key signatures ...) that each lead to a page. Edits
are live: they change the shared settings object, are saved, and a
`changed` signal tells the exercise to ask a new
question. The widgets the panels are built from are in
`alto.ui.settings_menu`, plugin exercises' panels are in
`alto.ui.pack_settings_panel`, and loading and saving the settings is in
`alto.ui.exercise_settings`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = settings_panel_for(ClefBasics())
>>> type(panel).__name__
'ClefBasicsSettingsPanel'
```

## NoteNameSettingsPanel

<div class="api-signature" markdown="1">

```python
NoteNameSettingsPanel(
    cfg: NoteNameSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="NoteNameSettingsPanel" line=145 %}{% raw %}

</div>

Bases: `NoteAnswerSettingsPanel`

The settings of the note identification exercise: a menu leading to
a page for each group of settings.

Two layers: the menu (Clefs, Range, Key signatures, Note values,
Note names, Accidentals and Octave) and a page for
each. Edits are live: each changes the settings, saves them and
emits `changed`.

**Attributes**

- `cfg` (*NoteNameSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes.
- `key_boxes` (*dict of int to QCheckBox*): The key signature checkboxes.
- `value_boxes` (*dict of str to QCheckBox*): The note value checkboxes.
- `naming_radios` (*dict of str to QRadioButton*): The letters and solfège choices, plus caret and function notation in the Scale degrees group.
- `octave_row` (*ToggleRow*): Whether the answer must include the written octave.
- `range_editors` (*dict of str to RangeEditor*): The range editor of each clef in use, built when the Range page opens.

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

- `cfg` (*NoteNameSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = NoteNameSettingsPanel(
...     NoteNameSettings()
... )
>>> panel.stack.count()  # the menu and five pages
6
```

## KeyboardSettingsPanel

<div class="api-signature" markdown="1">

```python
KeyboardSettingsPanel(
    cfg: settings.KeyboardSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyboardSettingsPanel" line=437 %}{% raw %}

</div>

Bases: `KeyboardRangePanel`

The settings of the keyboard exercise: a menu with a page for the
range of keys.

The menu has Range, Black keys, Octave number and Key signatures.
Edits are live: each changes the settings, saves them
and emits `changed`.

**Attributes**

- `cfg` (*KeyboardSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `span` (*KeyboardSpan*): The miniature piano on the Range page, which can be dragged to choose the keys.
- `low_label, high_label` (*QLabel*): The names of the lowest and highest key asked.
- `key_page` (*KeySignaturePage*): The key signature sub-page.

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

- `cfg` (*KeyboardSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardSettingsPanel(
...     settings.KeyboardSettings()
... ).stack.count()  # the menu, the range and the keys
3
```

## NoteConstructionSettingsPanel

<div class="api-signature" markdown="1">

```python
NoteConstructionSettingsPanel(
    cfg: settings.ConstructionSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="NoteConstructionSettingsPanel" line=761 %}{% raw %}

</div>

Bases: `ClefsPanel`

The settings of the note construction exercise: a menu with a page
for the staff and one for the keys.

The menu has Clefs, Staff Key, Question Type, and Octave. Edits are
live: each changes the settings, saves them and
emits `changed`.

**Attributes**

- `cfg` (*ConstructionSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes, including the grand staff.
- `key_tabs` (*QTabWidget*): The key signature sub-page.

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

- `cfg` (*ConstructionSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstructionSettingsPanel(
...     settings.ConstructionSettings()
... ).stack.count()
4
```

## IntervalSettingsPanel

<div class="api-signature" markdown="1">

```python
IntervalSettingsPanel(
    cfg: settings.IntervalSettings,
    *,
    prefix: str = 'intervals',
)
```

{% endraw %}{% include api-source.html name="IntervalSettingsPanel" line=1070 %}{% raw %}

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

- `cfg` (*IntervalSettings*): The interval exercise settings.
- `prefix` (*str*): Settings-store group for identification or construction.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalSettingsPanel(
...     settings.IntervalSettings()
... ).quality_row.value.text()
'Interval and Quality'
```

## KeyboardIntervalSettingsPanel

<div class="api-signature" markdown="1">

```python
KeyboardIntervalSettingsPanel(
    cfg: settings.KeyboardIntervalSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettingsPanel" line=1553 %}{% raw %}

</div>

Bases: `KeyboardRangePanel`

Range and interval selection pages for keyboard interval
identification.

**Attributes**

- `cfg` (*KeyboardIntervalSettings*): The settings being edited.
- `stack` (*SlideStack*): The settings menu, range page, and interval page.
- `span` (*KeyboardSpan*): The draggable range selector.
- `interval_range` (*QWidget*): The interval range controls directly below Select all.
- `interval_slider` (*IntervalRangeSlider*): The two-handle interval selector.
- `interval_low_label, interval_high_label` (*FieldComboBox*): Clickable endpoint notation with scrollable interval lists.
- `interval_page` (*ChoiceChecklist*): The interval checkboxes, keyed by distance in half steps.

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

- `cfg` (*KeyboardIntervalSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

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

## ArpeggioSettingsPanel

<div class="api-signature" markdown="1">

```python
ArpeggioSettingsPanel(
    cfg: settings.ArpeggioSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ArpeggioSettingsPanel" line=2235 %}{% raw %}

</div>

Bases: `ClefsPanel`

The settings of the arpeggio exercise: a menu with a page for each
group of settings.

The menu has Clefs, Arpeggio types, Inversions and Key signatures.
Edits are live: each changes the settings, saves them
and emits `changed`.

**Attributes**

- `cfg` (*ArpeggioSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes.
- `types` (*ChoiceChecklist*): The chord types.
- `inversions` (*ChoiceChecklist*): The inversions.
- `key_page` (*KeySignaturePage*): The key signature sub-page.

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

- `cfg` (*ArpeggioSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettingsPanel(
...     settings.ArpeggioSettings()
... ).stack.count()  # the menu and four pages
5
```

## KeySignatureSettingsPanel

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

{% endraw %}{% include api-source.html name="KeySignatureSettingsPanel" line=2508 %}{% raw %}

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

- `cfg` (*KeySignatureSettings*): The settings being edited.
- `prefix` (*str*): What the settings are saved under, such as "keySignatures".
- `stack` (*SlideStack*): The menu and its pages.
- `boxes` (*dict of str to QCheckBox*): The clef checkboxes.
- `modes` (*ChoiceChecklist*): The scales (major, minor and the modes).
- `key_list` (*KeyChecklist*): The key signatures (of the scales, in scale construction).
- `staff_key_list` (*KeyChecklist or None*): The key signatures that may be drawn on the staff; only scale construction has it.

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

- `cfg` (*KeySignatureSettings*): The settings to edit.
- `prefix` (*str, default "keySignatures"*): What the settings are saved under. Keyword-only.
- `keys_title` (*str, default "Key signatures"*): Title for the signature checklist when the exercise uses a single list. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatureSettingsPanel(
...     settings.KeySignatureSettings()
... ).stack.count()  # the menu and three pages
4
```

## NotationSettingsPanel

<div class="api-signature" markdown="1">

```python
NotationSettingsPanel()
```

{% endraw %}{% include api-source.html name="NotationSettingsPanel" line=3062 %}{% raw %}

</div>

Bases: `ExerciseSettingsPanel`

Choose the question type and the notation terms to practice.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Trill" in NotationSettingsPanel().terms.boxes
True
```

**Constructor**

Build the settings menu and its Question Type and Terms pages.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(
...     NotationSettingsPanel().terms.boxes
... ) == len(settings.NOTATION_TERMS)
True
```

## ClefBasicsSettingsPanel

<div class="api-signature" markdown="1">

```python
ClefBasicsSettingsPanel(
    cfg: settings.ClefBasicsSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ClefBasicsSettingsPanel" line=3245 %}{% raw %}

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

- `cfg` (*ClefBasicsSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its two pages.
- `types` (*dict of str to QRadioButton*): The choice of question, by key of `CLEF_QUESTION_TYPES`.
- `boxes` (*dict of str to QCheckBox*): The checkbox of each clef.

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

- `cfg` (*ClefBasicsSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

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

## settings_inversion_names

<div class="api-signature" markdown="1">

```python
def settings_inversion_names() -> tuple[str, ...]
```

{% endraw %}{% include api-source.html name="settings_inversion_names" line=3425 %}{% raw %}

</div>

Return the inversions as they are written in the settings.

**Returns**

- *tuple of str*: 'Root position', '1st inversion', '2nd inversion' and '3rd inversion'.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_inversion_names()
('Root position', '1st inversion', '2nd inversion', '3rd inversion')
```

## CircleSettingsPanel

<div class="api-signature" markdown="1">

```python
CircleSettingsPanel(
    cfg: settings.CircleSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="CircleSettingsPanel" line=3443 %}{% raw %}

</div>

Bases: `ExerciseSettingsPanel`

The settings of the circle of fifths exercise: which kinds of
question to ask, and the colors of the circle.

The menu has two rows. Questions opens a page of switches. Colors
opens a page of color schemes to choose from, with a
button to make one of your own, which opens an editor. Edits are
live: each changes the settings and saves them. A new kind
of question emits `changed`, and a new color scheme emits
`restyled`, which keeps the question.

**Attributes**

- `cfg` (*CircleSettings*): The settings being edited.
- `stack` (*SlideStack*): The menu and its pages: the menu, the questions, the color schemes and the editor of a scheme.
- `questions_row` (*MenuRow*): The menu row for the questions.
- `colors_row` (*MenuRow*): The menu row for the colors; its value is the name of the chosen scheme.
- `questions` (*ChoiceChecklist*): The kinds of question: relative major, relative minor and Roman numerals.
- `schemes` (*SchemePage*): The color schemes.
- `editor` (*SchemeEditor*): The editor of a scheme of your own.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = CircleSettingsPanel(
...     settings.CircleSettings()
... )
>>> (
...     panel.questions_row.value.text(),
...     panel.colors_row.value.text(),
... )
('3 of 3', 'Cyan to indigo')
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

- `cfg` (*CircleSettings*): The settings to edit.
- `parent` (*QWidget or None, default None*): The widget that owns the panel. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettingsPanel(
...     settings.CircleSettings()
... # the menu, the questions, the colors and the editor
... ).stack.count()
4
```

## settings_panel_for

<div class="api-signature" markdown="1">

```python
def settings_panel_for(
    exercise: Exercise,
    *,
    learner: Learner | None = None,
) -> ExerciseSettingsPanel
```

{% endraw %}{% include api-source.html name="settings_panel_for" line=3782 %}{% raw %}

</div>

Return the settings panel for an exercise.

**Parameters**

- `exercise` (*Exercise*): The exercise.
- `learner` (*Learner or None*): Profile whose calendar limits can be overridden.

**Returns**

- *ExerciseSettingsPanel*: A panel with the exercise options and the shared Next Question setting.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     IntervalNames,
...     NoteNames,
... )
>>> type(
...     settings_panel_for(NoteNames())
... ).__name__
'NoteNameSettingsPanel'
>>> type(
...     settings_panel_for(IntervalNames())
... ).__name__
'IntervalSettingsPanel'
```
{% endraw %}
