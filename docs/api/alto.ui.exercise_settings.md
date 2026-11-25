---
title: alto.ui.exercise_settings
parent: api
package: alto.ui
permalink: /api/alto.ui.exercise_settings/
---
{% raw %}
Load and save each exercise's settings.

The settings themselves are plain dataclasses in `alto.settings`, one
shared object per exercise. The functions here read them
from the saved preferences when Alto starts (`load_exercise_settings`)
and write them back when a settings panel changes them.
Values saved by older versions are converted, and anything saved that is
not valid any more is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_note_names()
>>> settings.note_names.naming in NAMINGS
True
```

## load_note_names

<div class="api-signature" markdown="1">

```python
def load_note_names() -> None
```

{% endraw %}{% include api-source.html name="load_note_names" line=52 %}{% raw %}

</div>

Load the saved note identification settings into the shared settings
object.

Settings saved by an older version, which had a switch between the
grand staff and single clefs, are converted. Anything
in the saved data that is not valid is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

<div class="api-signature" markdown="1">

```python
def save_note_names() -> None
```

{% endraw %}{% include api-source.html name="save_note_names" line=124 %}{% raw %}

</div>

Save the note identification settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg_ = settings.note_names
>>> cfg_.naming = "solfege"
>>> save_note_names()
>>> str(store().value("noteNames/naming"))
'solfege'
>>> cfg_.naming = "letters"
>>> save_note_names()
```

## load_keyboard

<div class="api-signature" markdown="1">

```python
def load_keyboard() -> None
```

{% endraw %}{% include api-source.html name="load_keyboard" line=163 %}{% raw %}

</div>

Load the saved keyboard exercise settings into the shared settings
object.

A saved range that is not a valid span of keys, or a key list with
nothing usable in it, is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

<div class="api-signature" markdown="1">

```python
def save_keyboard() -> None
```

{% endraw %}{% include api-source.html name="save_keyboard" line=216 %}{% raw %}

</div>

Save the keyboard exercise settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg_ = settings.keyboard
>>> save_keyboard()
>>> int(
...     store().value("keyboard/low")
... ) == cfg_.low
True
```

## load_keyboard_intervals

<div class="api-signature" markdown="1">

```python
def load_keyboard_intervals() -> None
```

{% endraw %}{% include api-source.html name="load_keyboard_intervals" line=248 %}{% raw %}

</div>

Load keyboard interval settings, ignoring invalid values and
intervals that cannot fit.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_keyboard_intervals()
>>> settings.keyboard_intervals.bounds()[
...     0
... ] < settings.keyboard_intervals.bounds()[1]
True
```

## save_keyboard_intervals

<div class="api-signature" markdown="1">

```python
def save_keyboard_intervals(cfg: settings.KeyboardIntervalSettings) -> None
```

{% endraw %}{% include api-source.html name="save_keyboard_intervals" line=315 %}{% raw %}

</div>

Save the keyboard interval range and selected distances.

**Parameters**

- `cfg` (*KeyboardIntervalSettings*): The settings to save.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_keyboard_intervals(
...     settings.KeyboardIntervalSettings()
... )
>>> int(store().value("keyboardIntervals/low"))
48
```

## load_construction

<div class="api-signature" markdown="1">

```python
def load_construction() -> None
```

{% endraw %}{% include api-source.html name="load_construction" line=353 %}{% raw %}

</div>

Load the saved note construction settings into the shared settings
object.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "construction/accidentals", "true"
... )
>>> load_construction()
>>> settings.construction.accidentals
False
```

## save_construction

<div class="api-signature" markdown="1">

```python
def save_construction(cfg: settings.ConstructionSettings) -> None
```

{% endraw %}{% include api-source.html name="save_construction" line=423 %}{% raw %}

</div>

Save the note construction settings.

**Parameters**

- `cfg` (*ConstructionSettings*): The settings to save.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings.construction.degrees = {1, 3}
>>> save_construction(settings.construction)
>>> str(store().value("construction/degrees"))
'1,3'
>>> settings.construction.degrees = set(
...     range(1, 8)
... )
>>> save_construction(settings.construction)
```

## load_arpeggio

<div class="api-signature" markdown="1">

```python
def load_arpeggio() -> None
```

{% endraw %}{% include api-source.html name="load_arpeggio" line=470 %}{% raw %}

</div>

Load the saved arpeggio settings into the shared settings object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue("arpeggio/types", "major")
>>> load_arpeggio()
>>> settings.arpeggio.types
{'major'}
>>> settings.arpeggio.types = {
...     "major",
...     "minor",
...     "dominant 7th",
...     "diminished 7th",
... }
>>> store().setValue(
...     "arpeggio/types",
...     ",".join(
...         settings.arpeggio.active_types()
...     ),
... )
```

## save_arpeggio

<div class="api-signature" markdown="1">

```python
def save_arpeggio(cfg: settings.ArpeggioSettings) -> None
```

{% endraw %}{% include api-source.html name="save_arpeggio" line=524 %}{% raw %}

</div>

Save the arpeggio settings.

**Parameters**

- `cfg` (*ArpeggioSettings*): The settings to save.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_arpeggio(settings.arpeggio)
>>> str(
...     store().value("arpeggio/clefs")
... ) == ",".join(
...     settings.arpeggio.active_clefs()
... )
True
```

## load_intervals

<div class="api-signature" markdown="1">

```python
def load_intervals(
    cfg: settings.IntervalSettings | None = None,
    *,
    prefix: str = 'intervals',
) -> None
```

{% endraw %}{% include api-source.html name="load_intervals" line=558 %}{% raw %}

</div>

Restore the saved staff interval options, keeping valid choices and
per-clef ranges.

**Parameters**

- `cfg` (*IntervalSettings or None*): Settings to populate. Defaults to Interval Identification.
- `prefix` (*str*): Independent settings-store group for the exercise.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_intervals()
>>> bool(settings.intervals.active_clefs())
True
```

## save_key_settings

<div class="api-signature" markdown="1">

```python
def save_key_settings(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str,
) -> None
```

{% endraw %}{% include api-source.html name="save_key_settings" line=801 %}{% raw %}

</div>

Save the settings of a key exercise: its clefs, scales and key
signatures, and the options of the kind of exercise it is.

**Parameters**

- `cfg` (*KeySignatureSettings*): The settings to save; the scale and Order of Keys exercises save their own options too.
- `prefix` (*str*): What the exercise's saved settings are filed under, such as "keySignatures". Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> saved_ = settings.ScaleConstructionSettings(
...     modes={"Major (Ionian)", "Dorian"},
...     steps=True,
... )
>>> save_key_settings(
...     saved_, prefix="doctestScales"
... )
>>> loaded_ = (
...     settings.ScaleConstructionSettings()
... )
>>> _load_key_settings(
...     loaded_, prefix="doctestScales"
... )
>>> sorted(loaded_.modes), loaded_.steps
(['Dorian', 'Major (Ionian)'], True)
>>> store().remove("doctestScales")
```

## load_key_signatures

<div class="api-signature" markdown="1">

```python
def load_key_signatures() -> None
```

{% endraw %}{% include api-source.html name="load_key_signatures" line=887 %}{% raw %}

</div>

Load the saved key signature identification settings into the shared
settings object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "keySignatures/clefs", "alto"
... )
>>> load_key_signatures()
>>> settings.key_signatures.clefs
{'alto'}
>>> settings.key_signatures.clefs = {
...     "treble",
...     "bass",
... }
>>> store().setValue(
...     "keySignatures/clefs", "treble,bass"
... )
```

## load_key_construction

<div class="api-signature" markdown="1">

```python
def load_key_construction() -> None
```

{% endraw %}{% include api-source.html name="load_key_construction" line=914 %}{% raw %}

</div>

Load the saved key signature construction settings into the shared
settings object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "keyConstruction/keys", "-3,4"
... )
>>> load_key_construction()
>>> settings.key_construction.active_keys()
[-3, 4]
>>> settings.key_construction.keys = set(
...     range(-7, 8)
... )
>>> store().remove("keyConstruction")
```

## load_order_of_keys

<div class="api-signature" markdown="1">

```python
def load_order_of_keys() -> None
```

{% endraw %}{% include api-source.html name="load_order_of_keys" line=938 %}{% raw %}

</div>

Restore the clefs, scales, and key signatures selected for Order of
Keys.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_order_of_keys()
```

## load_scale_identification

<div class="api-signature" markdown="1">

```python
def load_scale_identification() -> None
```

{% endraw %}{% include api-source.html name="load_scale_identification" line=955 %}{% raw %}

</div>

Load the saved scale identification options independently of scale
construction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_scale_identification()
>>> settings.scale_identification.active_staff_keys()
[0]
```

## load_scale_construction

<div class="api-signature" markdown="1">

```python
def load_scale_construction() -> None
```

{% endraw %}{% include api-source.html name="load_scale_construction" line=972 %}{% raw %}

</div>

Load the saved scale construction settings into the shared settings
object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "scaleConstruction/keys", "1,-1"
... )
>>> store().setValue(
...     "scaleConstruction/steps", "true"
... )
>>> store().setValue(
...     "scaleConstruction/octave", "true"
... )
>>> load_scale_construction()
>>> (
...     settings.scale_construction.active_keys(),
...     settings.scale_construction.steps,
...     settings.scale_construction.octave,
... )
([-1, 1], True, True)
>>> (
...     settings.scale_construction.keys,
...     settings.scale_construction.steps,
... ) = set(range(-7, 8)), False
>>> settings.scale_construction.octave = False
>>> store().remove("scaleConstruction")
```

## saved_notation_terms

<div class="api-signature" markdown="1">

```python
def saved_notation_terms() -> set[str]
```

{% endraw %}{% include api-source.html name="saved_notation_terms" line=1008 %}{% raw %}

</div>

Read the last nonempty selection of notation terms.

**Returns**

- *set of str*: The saved terms that still exist, or all terms for a new profile.

**Examples**

```text
Switching Select none off restores these checkboxes.
```

## load_notation_terms

<div class="api-signature" markdown="1">

```python
def load_notation_terms() -> None
```

{% endraw %}{% include api-source.html name="load_notation_terms" line=1030 %}{% raw %}

</div>

Restore the question type and term selection, defaulting to Answer
Button and all terms.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_notation_terms()
>>> bool(settings.notation.terms)
True
```

## load_clef_basics

<div class="api-signature" markdown="1">

```python
def load_clef_basics() -> None
```

{% endraw %}{% include api-source.html name="load_clef_basics" line=1057 %}{% raw %}

</div>

Load the saved clef basics settings into the shared settings object.

Anything in the saved data that is not a clef or a kind of question
is ignored, and a list with no clef in it leaves the
setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "clefBasics/clefs", "alto,subbass,flute"
... )
>>> store().setValue(
...     "clefBasics/type", "identification"
... )
>>> load_clef_basics()
>>> (
...     settings.clef_basics.active_clefs(),
...     settings.clef_basics.question_type,
... )
(['alto', 'subbass'], 'identification')
>>> (
...     settings.clef_basics.clefs,
...     settings.clef_basics.question_type,
... ) = (
...     {"treble", "bass"},
...     "construction",
... )
>>> store().remove("clefBasics")
```

## save_clef_basics

<div class="api-signature" markdown="1">

```python
def save_clef_basics(cfg: settings.ClefBasicsSettings) -> None
```

{% endraw %}{% include api-source.html name="save_clef_basics" line=1099 %}{% raw %}

</div>

Save clef basics settings, the form `load_clef_basics` reads.

**Parameters**

- `cfg` (*ClefBasicsSettings*): The settings to save.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_clef_basics(
...     settings.ClefBasicsSettings(
...         clefs={"french", "treble"},
...         question_type="identification",
...     )
... )
>>> (
...     str(store().value("clefBasics/clefs")),
...     str(store().value("clefBasics/type")),
... )
('treble,french', 'identification')
>>> store().remove("clefBasics")
```

## load_circle

<div class="api-signature" markdown="1">

```python
def load_circle() -> None
```

{% endraw %}{% include api-source.html name="load_circle" line=1128 %}{% raw %}

</div>

Load the saved circle of fifths settings into the shared settings
object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was. A
saved color scheme that no longer exists (it was deleted, or comes
from a newer Alto) leaves the default.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "circle/questions", "numeral,nonsense"
... )
>>> store().setValue(
...     "circle/scheme", "midnight"
... )
>>> load_circle()
>>> (
...     settings.circle.questions,
...     settings.circle.scheme,
... )
({'numeral'}, 'midnight')
>>> settings.circle.questions = set(
...     settings.CIRCLE_QUESTIONS
... )
>>> settings.circle.scheme = DEFAULT_SCHEME
>>> store().remove("circle")
```

## save_circle

<div class="api-signature" markdown="1">

```python
def save_circle(cfg: settings.CircleSettings) -> None
```

{% endraw %}{% include api-source.html name="save_circle" line=1183 %}{% raw %}

</div>

Save the circle of fifths settings.

**Parameters**

- `cfg` (*CircleSettings*): The settings to save.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_circle(
...     settings.CircleSettings(scheme="ink")
... )
>>> store().value("circle/scheme")
'ink'
>>> store().remove("circle")
```

## load_pack_options

<div class="api-signature" markdown="1">

```python
def load_pack_options() -> None
```

{% endraw %}{% include api-source.html name="load_pack_options" line=1207 %}{% raw %}

</div>

Restore the options learners chose for each plugin exercise that
offers settings.

Anything in the saved data that is not valid is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_pack_options()
```

## save_pack_options

<div class="api-signature" markdown="1">

```python
def save_pack_options(name: str) -> None
```

{% endraw %}{% include api-source.html name="save_pack_options" line=1289 %}{% raw %}

</div>

Save the options chosen for one plugin exercise.

**Parameters**

- `name` (*str*): The exercise's class name.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_pack_options("pack.nothing.here")
```

## load_choice_buttons

<div class="api-signature" markdown="1">

```python
def load_choice_buttons() -> None
```

{% endraw %}{% include api-source.html name="load_choice_buttons" line=1328 %}{% raw %}

</div>

Restore the independent button preferences for each multiple-choice
exercise.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_choice_buttons()
>>> from alto.exercises.library import NoteNames
>>> NoteNames.button_settings().button_mode in {
...     "all",
...     "limited",
... }
True
```

## load_exercise_settings

<div class="api-signature" markdown="1">

```python
def load_exercise_settings() -> None
```

{% endraw %}{% include api-source.html name="load_exercise_settings" line=1368 %}{% raw %}

</div>

Load the saved exercise options before creating a practice or export
settings panel.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_exercise_settings()
```
{% endraw %}
