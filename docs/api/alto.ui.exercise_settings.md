---
title: alto.ui.exercise_settings
parent: api
package: alto.ui
permalink: /api/alto.ui.exercise_settings/
---
{% raw %}
Load and save each exercise's settings.

The settings themselves are plain dataclasses in `alto.settings`, one shared object per exercise. The functions here read them
from the saved preferences when Alto starts (`load_exercise_settings`) and write them back when a settings panel changes them.
Values saved by older versions are converted, and anything saved that is not valid any more is ignored.

**Examples**

```pycon
>>> load_note_names()
>>> settings.note_names.naming in NAMINGS
True
```

## load_note_names

```python
def load_note_names() -> None
```

Load the saved note identification settings into the shared settings object.

Settings saved by an older version, which had a switch between the grand staff and single clefs, are converted. Anything
in the saved data that is not valid is ignored.

**Examples**

```pycon
>>> cfg_ = settings.note_names
>>> cfg_.clefs = {"alto"}
>>> save_note_names()
>>> cfg_.clefs = {"treble"}
>>> load_note_names()
>>> cfg_.clefs
{'alto'}
>>> cfg_.clefs = {"treble", "bass"}
>>> save_note_names()
```

## save_note_names

```python
def save_note_names() -> None
```

Save the note identification settings.

**Examples**

```pycon
>>> cfg_ = settings.note_names
>>> cfg_.naming = "solfege"
>>> save_note_names()
>>> str(store().value("noteNames/naming"))
'solfege'
>>> cfg_.naming = "letters"
>>> save_note_names()
```

## load_keyboard

```python
def load_keyboard() -> None
```

Load the saved keyboard exercise settings into the shared settings object.

A saved range that is not a valid span of keys, or a key list with nothing usable in it, is ignored.

**Examples**

```pycon
>>> cfg_ = settings.keyboard
>>> cfg_.require_octave = True
>>> save_keyboard()
>>> cfg_.require_octave = False
>>> load_keyboard()
>>> cfg_.require_octave
True
>>> cfg_.require_octave = False
>>> save_keyboard()
```

## save_keyboard

```python
def save_keyboard() -> None
```

Save the keyboard exercise settings.

**Examples**

```pycon
>>> cfg_ = settings.keyboard
>>> save_keyboard()
>>> int(store().value("keyboard/low")) == cfg_.low
True
```

## load_keyboard_intervals

```python
def load_keyboard_intervals() -> None
```

Load keyboard interval settings, ignoring invalid values and intervals that cannot fit.

**Examples**

```pycon
>>> load_keyboard_intervals()
>>> settings.keyboard_intervals.bounds()[0] < settings.keyboard_intervals.bounds()[1]
True
```

## save_keyboard_intervals

```python
def save_keyboard_intervals(cfg: settings.KeyboardIntervalSettings) -> None
```

Save the keyboard interval range and selected distances.

**Parameters**

- `cfg` (*KeyboardIntervalSettings*): The settings to save.

**Examples**

```pycon
>>> save_keyboard_intervals(settings.KeyboardIntervalSettings())
>>> int(store().value("keyboardIntervals/low"))
48
```

## load_construction

```python
def load_construction() -> None
```

Load the saved note construction settings into the shared settings object.

**Examples**

```pycon
>>> store().setValue("construction/accidentals", "true")
>>> load_construction()
>>> settings.construction.accidentals
False
```

## save_construction

```python
def save_construction(cfg: settings.ConstructionSettings) -> None
```

Save the note construction settings.

**Parameters**

- `cfg` (*ConstructionSettings*): The settings to save.

**Examples**

```pycon
>>> settings.construction.degrees = {1, 3}
>>> save_construction(settings.construction)
>>> str(store().value("construction/degrees"))
'1,3'
>>> settings.construction.degrees = set(range(1, 8))
>>> save_construction(settings.construction)
```

## load_arpeggio

```python
def load_arpeggio() -> None
```

Load the saved arpeggio settings into the shared settings object.

Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

**Examples**

```pycon
>>> store().setValue("arpeggio/types", "major")
>>> load_arpeggio()
>>> settings.arpeggio.types
{'major'}
>>> settings.arpeggio.types = {"major", "minor", "dominant 7th", "diminished 7th"}
>>> store().setValue("arpeggio/types", ",".join(settings.arpeggio.active_types()))
```

## save_arpeggio

```python
def save_arpeggio(cfg: settings.ArpeggioSettings) -> None
```

Save the arpeggio settings.

**Parameters**

- `cfg` (*ArpeggioSettings*): The settings to save.

**Examples**

```pycon
>>> save_arpeggio(settings.arpeggio)
>>> str(store().value("arpeggio/clefs")) == ",".join(settings.arpeggio.active_clefs())
True
```

## load_intervals

```python
def load_intervals(
    cfg: settings.IntervalSettings | None = None,
    *,
    prefix: str = 'intervals',
) -> None
```

Restore the saved staff interval options, keeping valid choices and per-clef ranges.

**Parameters**

- `cfg` (*IntervalSettings or None*): Settings to populate. Defaults to Interval Identification.
- `prefix` (*str*): Independent settings-store group for the exercise.

**Examples**

```pycon
>>> load_intervals()
>>> bool(settings.intervals.active_clefs())
True
```

## save_key_settings

```python
def save_key_settings(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str,
) -> None
```

Save the settings of a key exercise: its clefs, scales and key signatures, and the options of the kind of exercise it is.

**Parameters**

- `cfg` (*KeySignatureSettings*): The settings to save; the scale and Order of Keys exercises save their own options too.
- `prefix` (*str*): What the exercise's saved settings are filed under, such as "keySignatures". Keyword-only.

**Examples**

```pycon
>>> saved_ = settings.ScaleConstructionSettings(modes={"Major (Ionian)", "Dorian"}, steps=True)
>>> save_key_settings(saved_, prefix="doctestScales")
>>> loaded_ = settings.ScaleConstructionSettings()
>>> _load_key_settings(loaded_, prefix="doctestScales")
>>> sorted(loaded_.modes), loaded_.steps
(['Dorian', 'Major (Ionian)'], True)
>>> store().remove("doctestScales")
```

## load_key_signatures

```python
def load_key_signatures() -> None
```

Load the saved key signature identification settings into the shared settings object.

Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

**Examples**

```pycon
>>> store().setValue("keySignatures/clefs", "alto")
>>> load_key_signatures()
>>> settings.key_signatures.clefs
{'alto'}
>>> settings.key_signatures.clefs = {"treble", "bass"}
>>> store().setValue("keySignatures/clefs", "treble,bass")
```

## load_key_construction

```python
def load_key_construction() -> None
```

Load the saved key signature construction settings into the shared settings object.

Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

**Examples**

```pycon
>>> store().setValue("keyConstruction/keys", "-3,4")
>>> load_key_construction()
>>> settings.key_construction.active_keys()
[-3, 4]
>>> settings.key_construction.keys = set(range(-7, 8))
>>> store().remove("keyConstruction")
```

## load_order_of_keys

```python
def load_order_of_keys() -> None
```

Restore the clefs, scales, and key signatures selected for Order of Keys.

**Examples**

```pycon
>>> load_order_of_keys()
```

## load_scale_identification

```python
def load_scale_identification() -> None
```

Load the saved scale identification options independently of scale construction.

**Examples**

```pycon
>>> load_scale_identification()
>>> settings.scale_identification.active_staff_keys()
[0]
```

## load_scale_construction

```python
def load_scale_construction() -> None
```

Load the saved scale construction settings into the shared settings object.

Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

**Examples**

```pycon
>>> store().setValue("scaleConstruction/keys", "1,-1")
>>> store().setValue("scaleConstruction/steps", "true")
>>> store().setValue("scaleConstruction/octave", "true")
>>> load_scale_construction()
>>> settings.scale_construction.active_keys(), settings.scale_construction.steps, settings.scale_construction.octave
([-1, 1], True, True)
>>> settings.scale_construction.keys, settings.scale_construction.steps = set(range(-7, 8)), False
>>> settings.scale_construction.octave = False
>>> store().remove("scaleConstruction")
```

## saved_notation_terms

```python
def saved_notation_terms() -> set[str]
```

Read the last nonempty selection of notation terms.

**Returns**

- *set of str*: The saved terms that still exist, or all terms for a new profile.

**Examples**

```pycon
Switching Select none off restores these checkboxes.
```

## load_notation_terms

```python
def load_notation_terms() -> None
```

Restore the question type and term selection, defaulting to Answer Button and all terms.

**Examples**

```pycon
>>> load_notation_terms()
>>> bool(settings.notation.terms)
True
```

## load_clef_basics

```python
def load_clef_basics() -> None
```

Load the saved clef basics settings into the shared settings object.

Anything in the saved data that is not a clef or a kind of question is ignored, and a list with no clef in it leaves the
setting as it was.

**Examples**

```pycon
>>> store().setValue("clefBasics/clefs", "alto,subbass,flute")
>>> store().setValue("clefBasics/type", "identification")
>>> load_clef_basics()
>>> settings.clef_basics.active_clefs(), settings.clef_basics.question_type
(['alto', 'subbass'], 'identification')
>>> settings.clef_basics.clefs, settings.clef_basics.question_type = {"treble", "bass"}, "construction"
>>> store().remove("clefBasics")
```

## save_clef_basics

```python
def save_clef_basics(cfg: settings.ClefBasicsSettings) -> None
```

Save clef basics settings, the form `load_clef_basics` reads.

**Parameters**

- `cfg` (*ClefBasicsSettings*): The settings to save.

**Examples**

```pycon
>>> save_clef_basics(settings.ClefBasicsSettings(clefs={"french", "treble"}, question_type="identification"))
>>> str(store().value("clefBasics/clefs")), str(store().value("clefBasics/type"))
('treble,french', 'identification')
>>> store().remove("clefBasics")
```

## load_circle

```python
def load_circle() -> None
```

Load the saved circle of fifths settings into the shared settings object.

Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was. A
saved color scheme that no longer exists (it was deleted, or comes from a newer Alto) leaves the default.

**Examples**

```pycon
>>> store().setValue("circle/questions", "numeral,nonsense")
>>> store().setValue("circle/scheme", "midnight")
>>> load_circle()
>>> settings.circle.questions, settings.circle.scheme
({'numeral'}, 'midnight')
>>> settings.circle.questions = set(settings.CIRCLE_QUESTIONS)
>>> settings.circle.scheme = DEFAULT_SCHEME
>>> store().remove("circle")
```

## save_circle

```python
def save_circle(cfg: settings.CircleSettings) -> None
```

Save the circle of fifths settings.

**Parameters**

- `cfg` (*CircleSettings*): The settings to save.

**Examples**

```pycon
>>> save_circle(settings.CircleSettings(scheme="ink"))
>>> store().value("circle/scheme")
'ink'
>>> store().remove("circle")
```

## load_pack_options

```python
def load_pack_options() -> None
```

Restore the options learners chose for each plugin exercise that offers settings.

Anything in the saved data that is not valid is ignored.

**Examples**

```pycon
>>> load_pack_options()
```

## save_pack_options

```python
def save_pack_options(name: str) -> None
```

Save the options chosen for one plugin exercise.

**Parameters**

- `name` (*str*): The exercise's class name.

**Examples**

```pycon
>>> save_pack_options("pack.nothing.here")
```

## load_choice_buttons

```python
def load_choice_buttons() -> None
```

Restore the independent button preferences for each multiple-choice exercise.

**Examples**

```pycon
>>> load_choice_buttons()
>>> from alto.exercises.library import NoteNames
>>> NoteNames.button_settings().button_mode in {"all", "limited"}
True
```

## load_exercise_settings

```python
def load_exercise_settings() -> None
```

Load the saved exercise options before creating a practice or export settings panel.

**Examples**

```pycon
>>> load_exercise_settings()
```
{% endraw %}
