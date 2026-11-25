---
title: alto.settings
parent: api
package: alto
permalink: /api/alto.settings/
---
{% raw %}
User settings. Pure Python (no Qt); persistence lives in
ui/exercise_settings.py.

Each exercise with settings has a small dataclass here
(`NoteNameSettings`, `KeyboardSettings` and so on) and one shared
instance of it (`note_names`, `keyboard` ...) that the exercise and its
settings panel both read and write.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings().active_clefs()
['treble', 'bass']
>>> spell(Note.parse("F#4"))
'F♯'
```

## spell

<div class="api-signature" markdown="1">

```python
def spell(
    note: Note,
    *,
    naming: str = 'letters',
    key: int = 0,
    octave: bool = False,
    minor: bool = False,
) -> str
```

{% endraw %}{% include api-source.html name="spell" line=203 %}{% raw %}

</div>

Return a note name in the chosen naming system, optionally including
its octave.

**Parameters**

- `note` (*Note*): The note.
- `naming` (*str, default "letters"*): "letters" for C D E, "solfege" for Do Re Mi, "degrees" for caret scale degrees, or "functions" for function names. Keyword-only.
- `key` (*int, default 0*): The major key signature for scale degrees: sharps if positive, flats if negative. Zero means C major. Keyword-only.
- `octave` (*bool, default False*): Include the note's octave, separated from a scale degree by " / ". Keyword-only.
- `minor` (*bool, default False*): Use the relative natural minor as the scale degree reference. Keyword-only.

**Returns**

- *str*: The name and, if requested, octave. Carets use accidental prefixes; function names use Raised or Lowered prefixes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> spell(Note.parse("F#4"))
'F♯'
>>> spell(Note.parse("F#4"), naming="solfege")
'Fa♯'
>>> spell(
...     Note.parse("F#4"),
...     naming="degrees",
...     key=1,
... )
'7̂'
>>> spell(
...     Note.parse("F4"),
...     naming="degrees",
...     key=1,
... )
'♭7̂'
>>> spell(Note.parse("Eb4"), naming="degrees")
'♭3̂'
>>> spell(
...     Note.parse("G4"),
...     naming="functions",
...     key=1,
... )
'Tonic'
>>> spell(
...     Note.parse("F4"),
...     naming="functions",
...     key=1,
... )
'Lowered Leading tone'
>>> spell(
...     Note.parse("G4"),
...     naming="degrees",
...     key=1,
...     octave=True,
... )
'1̂ / 4'
```

## diatonic_name

<div class="api-signature" markdown="1">

```python
def diatonic_name(d: int) -> str
```

{% endraw %}{% include api-source.html name="diatonic_name" line=305 %}{% raw %}

</div>

Return the name and octave of the natural note on a staff step.

**Parameters**

- `d` (*int*): The staff-step index (see `Note.diatonic`).

**Returns**

- *str*: For example 'E4'.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> diatonic_name(30)
'E4'
```

## ClefChoice

<div class="api-signature" markdown="1">

```python
class ClefChoice
```

{% endraw %}{% include api-source.html name="ClefChoice" line=328 %}{% raw %}

</div>

Settings with a set of chosen clefs, which are always used in the
same order.

**Attributes**

- `CLEF_ORDER` (*tuple of str*): Every clef the settings may hold, in the order they are offered and used. Each subclass sets it.
- `clefs` (*set of str*): The chosen clefs. The dataclass that uses this mixin declares the field and its default.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings(
...     clefs={"tenor", "alto"}
... ).active_clefs()
['alto', 'tenor']
```

### ClefChoice.active_clefs

<div class="api-signature" markdown="1">

```python
def active_clefs() -> list[str]
```

{% endraw %}{% include api-source.html name="ClefChoice.active_clefs" line=353 %}{% raw %}

</div>

Return the clefs to use, in canonical order.

**Returns**

- *list of str*: The chosen clefs in the order of `CLEF_ORDER`, or the treble clef if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings(
...     clefs={"grand", "tenor"}
... ).active_clefs()
['tenor', 'grand']
>>> ClefBasicsSettings(
...     clefs={"subbass", "treble"}
... ).active_clefs()
['treble', 'subbass']
>>> NoteNameSettings(clefs=set()).active_clefs()
['treble']
```

## KeyChoice

<div class="api-signature" markdown="1">

```python
class KeyChoice
```

{% endraw %}{% include api-source.html name="KeyChoice" line=379 %}{% raw %}

</div>

Settings with a set of chosen key signatures.

**Attributes**

- `keys` (*set of int*): The chosen key signatures, as sharps (positive) or flats (negative). The dataclass that uses this mixin declares the field and its default.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardSettings(keys={3, -2}).active_keys()
[-2, 3]
```

### KeyChoice.active_keys

<div class="api-signature" markdown="1">

```python
def active_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="KeyChoice.active_keys" line=398 %}{% raw %}

</div>

Return the key signatures to draw from, lowest first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ConstructionSettings(
...     keys={2, -1}
... ).active_keys()
[-1, 2]
>>> KeySignatureSettings(
...     keys=set()
... ).active_keys()
[0]
```

## StaffRangeSettings

<div class="api-signature" markdown="1">

```python
StaffRangeSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    ranges: dict[str, tuple[int, int]] = field(default_factory=dict),
    note_values: set[str] = field(default_factory=lambda: {'whole'}),
)
```

{% endraw %}{% include api-source.html name="StaffRangeSettings" line=423 %}{% raw %}

</div>

Bases: `ClefChoice`

Selected clefs and inclusive pitch limits for each staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StaffRangeSettings().active_clefs()
['treble', 'bass']
```

### StaffRangeSettings.active_values

<div class="api-signature" markdown="1">

```python
def active_values() -> list[str]
```

{% endraw %}{% include api-source.html name="StaffRangeSettings.active_values" line=445 %}{% raw %}

</div>

Return the note values to draw, from longest to shortest.

**Returns**

- *list of str*: The chosen values in the order of `NOTE_VALUES`, or whole notes if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings(
...     note_values={"half", "whole"}
... ).active_values()
['whole', 'half']
```

### StaffRangeSettings.range_for

<div class="api-signature" markdown="1">

```python
def range_for(clef: str) -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="StaffRangeSettings.range_for" line=464 %}{% raw %}

</div>

Return the range of notes that may be asked on a clef.

**Parameters**

- `clef` (*str*): A key of `DEFAULT_RANGES`.

**Returns**

- *tuple of (int, int)*: The lowest and highest staff step, inclusive; the user's override if there is one, otherwise the default.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings().range_for("treble")
(22, 52)
>>> NoteNameSettings(
...     ranges={"treble": (40, 30)}
... ).range_for(
...     "treble"
... )  # given in the wrong order
(30, 40)
```

## NoteNameSettings

<div class="api-signature" markdown="1">

```python
NoteNameSettings(
    *,
    key_signatures: set[int] = field(default_factory=lambda: {0}),
    naming: str = 'letters',
    minor_degrees: bool = False,
    accidentals: bool = False,
    require_octave: bool = False,
)
```

{% endraw %}{% include api-source.html name="NoteNameSettings" line=495 %}{% raw %}

</div>

Bases: `StaffRangeSettings`

The settings of the note identification exercise.

**Attributes**

- `clefs` (*set of str*): The clefs to ask on, any of `RANGE_KEYS`, so "grand" is allowed.
- `ranges` (*dict of str to tuple of (int, int)*): Overrides of `DEFAULT_RANGES`, as inclusive staff-step ranges. Keyword-only.
- `key_signatures` (*set of int*): The keys to use, as sharps (positive) or flats (negative). Keyword-only.
- `note_values` (*set of str*): The note values to draw, from `NOTE_VALUES`. Keyword-only.
- `naming` (*str, default "letters"*): A key of `NAMINGS`. Keyword-only.
- `accidentals` (*bool, default False*): Also ask notes with explicit sharps, flats and naturals. Keyword-only.
- `require_octave` (*bool, default False*): Also require the written octave as part of the answer. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = NoteNameSettings(
...     clefs={"bass"}, key_signatures={2}
... )
>>> cfg.active_clefs(), cfg.active_keys()
(['bass'], [2])
```

### NoteNameSettings.active_keys

<div class="api-signature" markdown="1">

```python
def active_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="NoteNameSettings.active_keys" line=544 %}{% raw %}

</div>

Return the key signatures to draw from, lowest first.

The field is named `key_signatures` rather than `keys`, as in
`KeyChoice`, because the name is part of the practice
signature that stored questions are matched by; renaming it
would orphan every learner's saved questions.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings(
...     key_signatures={2, -1}
... ).active_keys()
[-1, 2]
```

## PackExerciseSettings

<div class="api-signature" markdown="1">

```python
PackExerciseSettings(
    *,
    sound: str | None = None,
    accidentals: bool = False,
    require_octave: bool = False,
    keys: tuple[int, int] | None = None,
    intervals: frozenset[str] | None = None,
    manuals: frozenset[str] | None = None,
)
```

{% endraw %}{% include api-source.html name="PackExerciseSettings" line=573 %}{% raw %}

</div>

Bases: `StaffRangeSettings`

The options a plugin's exercise offers the learner, such as its
range and whether to ask accidentals.

Only the options the plugin declares for the exercise are shown and
used; the rest keep their defaults.

**Attributes**

- `clefs` (*set of str*): The one clef the exercise's range is drawn on.
- `ranges` (*dict of str to tuple of (int, int)*): The range of notes asked, as staff steps, under the clef.
- `sound` (*str or None, default None*): The key of the instrument that sounds in this exercise instead of the plugin's own, or None for the plugin's own. Keyword-only.
- `accidentals` (*bool, default False*): Also ask the notes between the listed ones, written with sharps or flats. Keyword-only.
- `require_octave` (*bool, default False*): The answer also includes the note's written octave. Keyword-only.
- `keys` (*tuple of int or None, default None*): For a keyboard interval exercise, the lowest and highest key asked, as MIDI numbers. None asks the plugin's own default range. Keyword-only.
- `intervals` (*frozenset of str or None, default None*): For a keyboard interval exercise, the names of the intervals asked. None asks every interval the plugin lists. Keyword-only.
- `manuals` (*frozenset of str or None, default None*): For a keyboard interval exercise, the names of the keyboards the highlighted keys may sit on. None uses them all. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PackExerciseSettings(
...     clefs={"alto"}
... ).sound is None
True
>>> PackExerciseSettings(
...     clefs={"alto"}
... ).keys is None
True
```

## IntervalSettings

<div class="api-signature" markdown="1">

```python
IntervalSettings(
    *,
    staff_keys: set[int] = field(default_factory=lambda: {0}),
    displays: set[str] = field(default_factory=lambda: {'Harmonic'}),
    directions: set[str] = field(default_factory=lambda: {'ascending'}),
    button_mode: str = 'limited',
    button_count: int = 6,
    accidentals: set[int] = field(default_factory=lambda: set(DEFAULT_INTERVAL_ACCIDENTALS)),
    quality_mode: str = 'combined',
    inversions: bool = False,
    consonance: bool = False,
    intervals: set[str] = field(default_factory=lambda: {name for name, iv in WRITTEN_INTERVALS.items() if 2 <= iv.number <= 7 or name == 'P8'}),
)
```

{% endraw %}{% include api-source.html name="IntervalSettings" line=662 %}{% raw %}

</div>

Bases: `StaffRangeSettings`

Staff signatures, presentations, answer format and spelled intervals
for Interval Identification.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalSettings().quality_mode
'combined'
```

### IntervalSettings.staff_span

<div class="api-signature" markdown="1">

```python
def staff_span(clef: str) -> int
```

{% endraw %}{% include api-source.html name="IntervalSettings.staff_span" line=695 %}{% raw %}

</div>

Count the written staff positions in a clef's selected range,
including both endpoints.

**Parameters**

- `clef` (*str*): The clef whose range to measure.

**Returns**

- *int*: The largest diatonic interval number that fits.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalSettings(
...     ranges={"treble": (28, 30)}
... ).staff_span("treble")
3
```

## key_name

<div class="api-signature" markdown="1">

```python
def key_name(midi: int) -> str
```

{% endraw %}{% include api-source.html name="key_name" line=785 %}{% raw %}

</div>

Return the name of a MIDI note with its octave, black keys as
sharps.

**Parameters**

- `midi` (*int*): The MIDI note number.

**Returns**

- *str*: For example 'C4' for 60 and 'C♯4' for 61.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_name(60), key_name(61)
('C4', 'C♯4')
```

## KeyboardSettings

<div class="api-signature" markdown="1">

```python
KeyboardSettings(
    black_keys: bool = True,
    *,
    naming: str = 'letters',
    require_octave: bool = False,
    low: int = KEYBOARD_DEFAULT[0],
    high: int = KEYBOARD_DEFAULT[1],
    key_signature: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
)
```

{% endraw %}{% include api-source.html name="KeyboardSettings" line=809 %}{% raw %}

</div>

Bases: `KeyChoice`

The settings of the keyboard identification exercise.

**Attributes**

- `naming` (*str, default "letters"*): Naming system for the highlighted key. Keyword-only.
- `black_keys` (*bool, default True*): Also ask the black keys, answered by either enharmonic name.
- `require_octave` (*bool, default False*): The answer must include the octave number as well. Keyword-only.
- `low` (*int*): The lowest key asked, as a MIDI number. Keyword-only.
- `high` (*int*): The highest key asked, as a MIDI number, inclusive. Keyword-only.
- `key_signature` (*bool, default False*): Show a key signature, and require the name that fits it (no enharmonic spelling). Keyword-only.
- `keys` (*set of int*): The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = KeyboardSettings()
>>> key_name(cfg.low), key_name(cfg.high)
('C3', 'C5')
```

## keyboard_interval_name

<div class="api-signature" markdown="1">

```python
def keyboard_interval_name(distance: int) -> str
```

{% endraw %}{% include api-source.html name="keyboard_interval_name" line=887 %}{% raw %}

</div>

Name a keyboard interval by its distance, including compound
intervals.

**Parameters**

- `distance` (*int*): The distance in half steps, from 1 through the full piano span.

**Returns**

- *str*: A conventional interval name, with both spellings for tritones.

**Raises**

- *ValueError*: If the distance cannot occur between two distinct piano keys.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     keyboard_interval_name(13),
...     keyboard_interval_name(18),
...     keyboard_interval_name(24),
... )
('m9', 'A11 / d12', 'P15')
>>> keyboard_interval_name(87)
'm52'
```

## KeyboardIntervalSettings

<div class="api-signature" markdown="1">

```python
KeyboardIntervalSettings(
    low: int = KEYBOARD_DEFAULT[0],
    high: int = KEYBOARD_DEFAULT[1],
    intervals: set[int] = field(default_factory=lambda: set(range(1, 13))),
    all_interval_buttons: bool = False,
    compact_buttons: bool = False,
    button_count: int = 6,
)
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings" line=936 %}{% raw %}

</div>

The keyboard range and interval distances used for keyboard interval
identification.

**Attributes**

- `low` (*int*): The lowest key, as a MIDI number. Keyword-only.
- `high` (*int*): The highest key, inclusive. Keyword-only.
- `intervals` (*set of int*): Selected distances in half steps, up to the full piano span. Keyword-only.
- `button_count` (*int, default 6*): Maximum answer buttons in limited mode. Keyword-only.
- `compact_buttons` (*bool, default False*): Answer with separate quality-letter and interval-number buttons. Keyword-only.
- `all_interval_buttons` (*bool, default False*): Show a fixed answer button for every selected interval instead of a limited number of choices. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings().bounds()
(48, 72)
```

### KeyboardIntervalSettings.answer_button_limit

<div class="api-signature" markdown="1">

```python
def answer_button_limit() -> int
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings.answer_button_limit" line=973 %}{% raw %}

</div>

Return the requested count within the supported range of 1 to 87
buttons.

**Returns**

- *int*: The bounded maximum number of answer buttons in limited mode.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings().answer_button_limit()
6
>>> KeyboardIntervalSettings(
...     button_count=0
... ).answer_button_limit()
1
```

### KeyboardIntervalSettings.bounds

<div class="api-signature" markdown="1">

```python
def bounds() -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings.bounds" line=995 %}{% raw %}

</div>

Return a piano range containing at least two distinct keys.

**Returns**

- *tuple of (int, int)*: Sorted bounds within the full piano range, widened by one key if necessary.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings(
...     low=60, high=60
... ).bounds()
(60, 61)
```

### KeyboardIntervalSettings.active_intervals

<div class="api-signature" markdown="1">

```python
def active_intervals() -> list[int]
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings.active_intervals" line=1023 %}{% raw %}

</div>

Return selected interval distances that fit the keyboard range.

**Returns**

- *list of int*: Sorted positive distances that fit; empty if none are selected. Invalid nonempty selections use a minor second.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings(
...     low=60, high=64, intervals={3, 4, 12}
... ).active_intervals()
[3, 4]
>>> KeyboardIntervalSettings(
...     intervals=set()
... ).active_intervals()
[]
```

## ConstructionSettings

<div class="api-signature" markdown="1">

```python
ConstructionSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    accidentals: bool = False,
    key_signature: bool = False,
    question_type: str = 'scale',
    degrees: set[int] = field(default_factory=lambda: set(range(1, 8))),
    octave: bool = True,
    staff_keys: set[int] | None = None,
    major: bool = True,
    minor: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
    minor_keys: set[int] | None = None,
)
```

{% endraw %}{% include api-source.html name="ConstructionSettings" line=1058 %}{% raw %}

</div>

Bases: `ClefChoice, KeyChoice`

The settings of the note construction exercise.

**Attributes**

- `clefs` (*set of str*): The clefs to ask on, any of `RANGE_KEYS`, so "grand" is allowed.
- `accidentals` (*bool, default False*): Also ask for sharps and flats, which the answer then has to include. Keyword-only.
- `key_signature` (*bool, default False*): Draw a key signature; it applies to the note unless the note is given its own sign. Keyword-only.
- `question_type` (*str, default "scale"*): Use the selected scale keys or ask for notes without a scale key. Keyword-only.
- `degrees` (*set of int*): Scale degrees to ask for in Scale and Degree mode. Keyword-only.
- `octave` (*bool, default True*): Require the note to be placed in a specific octave. Keyword-only.
- `staff_keys` (*set of int or None*): Staff signatures chosen independently. None uses the question key. Keyword-only.
- `major` (*bool, default True*): Use major keys. With key signatures off, use C major. Keyword-only.
- `minor` (*bool, default False*): Use relative minor keys. With key signatures off, use A minor. Keyword-only.
- `keys` (*set of int*): The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only.
- `minor_keys` (*set of int or None*): Signatures selected for minor keys. None uses the original shared selection. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ConstructionSettings(
...     clefs={"grand"}
... ).active_clefs()
['grand']
```

## ArpeggioSettings

<div class="api-signature" markdown="1">

```python
ArpeggioSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    types: set[str] = field(default_factory=lambda: {'major', 'minor', 'dominant 7th', 'diminished 7th'}),
    inversions: set[int] = field(default_factory=lambda: set(INVERSIONS)),
    key_signature: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
)
```

{% endraw %}{% include api-source.html name="ArpeggioSettings" line=1168 %}{% raw %}

</div>

Bases: `ClefChoice, KeyChoice`

The settings of the arpeggio identification exercise.

**Attributes**

- `clefs` (*set of str*): The clefs to draw on, any of `CLEFS`.
- `types` (*set of str*): The chord types to ask, from `ARPEGGIO_TYPES`. Keyword-only.
- `inversions` (*set of int*): The inversions to ask: 0 for root position up to 3 for the third inversion. Keyword-only.
- `key_signature` (*bool, default False*): Draw a key signature, so the arpeggio only gets signs where it differs from it. Keyword-only.
- `keys` (*set of int*): The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings().active_types()
['major', 'minor', 'dominant 7th', 'diminished 7th']
```

### ArpeggioSettings.active_types

<div class="api-signature" markdown="1">

```python
def active_types() -> list[str]
```

{% endraw %}{% include api-source.html name="ArpeggioSettings.active_types" line=1222 %}{% raw %}

</div>

Return the chord types to ask, triads first and then seventh
chords.

**Returns**

- *list of str*: The chosen types in the order of `ARPEGGIO_TYPES`, or "major" if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings(
...     types={"minor 7th", "major"}
... ).active_types()
['major', 'minor 7th']
```

### ArpeggioSettings.active_inversions

<div class="api-signature" markdown="1">

```python
def active_inversions() -> list[int]
```

{% endraw %}{% include api-source.html name="ArpeggioSettings.active_inversions" line=1242 %}{% raw %}

</div>

Return the inversions to ask, root position first.

**Returns**

- *list of int*: The chosen inversions, or root position (0) if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings(
...     inversions={2, 0}
... ).active_inversions()
[0, 2]
```

### ArpeggioSettings.inversions_for

<div class="api-signature" markdown="1">

```python
def inversions_for(chord_type: str) -> list[int]
```

{% endraw %}{% include api-source.html name="ArpeggioSettings.inversions_for" line=1261 %}{% raw %}

</div>

Return the inversions that can be asked for a chord type.

A triad has no third inversion. If none of the chosen inversions
applies (only the third, for a triad), root position is
used.

**Parameters**

- `chord_type` (*str*): A key of `CHORDS`, such as "major" or "dominant 7th".

**Returns**

- *list of int*: The inversions to choose from.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = ArpeggioSettings()
>>> (
...     cfg.inversions_for("major"),
...     cfg.inversions_for("dominant 7th"),
... )
([0, 1, 2], [0, 1, 2, 3])
>>> ArpeggioSettings(
...     inversions={3}
... ).inversions_for("major")
[0]
```

## KeySignatureSettings

<div class="api-signature" markdown="1">

```python
KeySignatureSettings(
    *,
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    modes: set[str] = field(default_factory=lambda: {'Major (Ionian)', 'Natural minor (Aeolian)'}),
    keys: set[int] = field(default_factory=lambda: set(range(-7, 8))),
)
```

{% endraw %}{% include api-source.html name="KeySignatureSettings" line=1326 %}{% raw %}

</div>

Bases: `ClefChoice, KeyChoice`

The settings of the key signature identification exercise.

**Attributes**

- `clefs` (*set of str*): The clefs a signature is drawn on, any of `CLEFS`. Keyword-only.
- `modes` (*set of str*): The scales to ask about, from `KEY_MODES`. Keyword-only.
- `keys` (*set of int*): The key signatures asked, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = KeySignatureSettings()
>>> cfg.active_clefs(), len(cfg.active_keys())
(['treble', 'bass'], 15)
```

### KeySignatureSettings.active_modes

<div class="api-signature" markdown="1">

```python
def active_modes() -> list[str]
```

{% endraw %}{% include api-source.html name="KeySignatureSettings.active_modes" line=1358 %}{% raw %}

</div>

Return the scales to ask about, in the order of `KEY_MODES`.

**Returns**

- *list of str*: The chosen modes, or major if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatureSettings().active_modes()
['Major (Ionian)', 'Natural minor (Aeolian)']
```

## OrderOfKeysSettings

<div class="api-signature" markdown="1">

```python
OrderOfKeysSettings(
    *,
    starting_accidentals: set[int] = field(default_factory=lambda: {0}),
)
```

{% endraw %}{% include api-source.html name="OrderOfKeysSettings" line=1379 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

Choose the starting signs for writing a key signature.

**Attributes**

- `starting_accidentals` (*set of int*): Allowed counts of given signs. Negative counts represent flats and positive counts represent sharps.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeysSettings(
...     keys={-2, 4}
... ).available_starts()
range(-2, 5)
```

### OrderOfKeysSettings.available_starts

<div class="api-signature" markdown="1">

```python
def available_starts() -> range
```

{% endraw %}{% include api-source.html name="OrderOfKeysSettings.available_starts" line=1400 %}{% raw %}

</div>

Return starting counts that fit at least one selected signature.

**Returns**

- *range*: Counts from the flattest eligible start through the sharpest, always including zero.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> list(
...     OrderOfKeysSettings(
...         keys={-2}
...     ).available_starts()
... )
[-2, -1, 0]
```

## KeyConstructionSettings

<div class="api-signature" markdown="1">

```python
KeyConstructionSettings()
```

{% endraw %}{% include api-source.html name="KeyConstructionSettings" line=1427 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

The settings of the key signature construction exercise: the same
choices as key signature identification.

**Attributes**

- `clefs` (*set of str*): The clefs the blank staff is drawn in, any of `CLEFS`. Keyword-only.
- `modes` (*set of str*): The scales to ask for, from `KEY_MODES`. Keyword-only.
- `keys` (*set of int*): The key signatures to build, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = KeyConstructionSettings(keys={-2})
>>> cfg.active_keys(), cfg.active_modes()
([-2], ['Major (Ionian)', 'Natural minor (Aeolian)'])
```

## ScaleIdentificationSettings

<div class="api-signature" markdown="1">

```python
ScaleIdentificationSettings(
    *,
    question_type: str = 'combined',
    button_mode: str = 'limited',
    button_count: int = 6,
    minor_keys: set[int] | None = None,
    motion: str = 'ascending',
    staff_keys: set[int] = field(default_factory=lambda: {0}),
)
```

{% endraw %}{% include api-source.html name="ScaleIdentificationSettings" line=1455 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

Choose the clefs, scale types and independent staff and scale key
signatures for identification.

**Attributes**

- `staff_keys` (*set of int*): Signatures drawn on the staff, independently of the scale's own signature. Keyword-only.
- `motion` (*str, default "ascending"*): Direction of the scale, "ascending" or "descending". Keyword-only.
- `button_mode` (*str, default "limited"*): Show a limited set of complete answers or separate tonic and mode buttons in "all" mode. Keyword-only.
- `button_count` (*int, default 6*): Maximum number of answer buttons in limited mode. Keyword-only.
- `question_type` (*str, default "combined"*): Ask for the mode, the tonic (key), or both. Keyword-only.
- `minor_keys` (*set of int or None*): Signatures for natural minor. None uses the shared key selection. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = ScaleIdentificationSettings(
...     keys={2}, staff_keys={-3}
... )
>>> cfg.active_keys(), cfg.active_staff_keys()
([2], [-3])
```

### ScaleIdentificationSettings.active_staff_keys

<div class="api-signature" markdown="1">

```python
def active_staff_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="ScaleIdentificationSettings.active_staff_keys" line=1500 %}{% raw %}

</div>

Return the selected staff signatures, falling back to no
signature.

**Returns**

- *list of int*: Signature counts in ascending order.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleIdentificationSettings(
...     staff_keys=set()
... ).active_staff_keys()
[0]
```

## ScaleConstructionSettings

<div class="api-signature" markdown="1">

```python
ScaleConstructionSettings(
    *,
    minor_keys: set[int] | None = None,
    motion: str = 'ascending',
    steps: bool = False,
    octave: bool = False,
    staff_keys: set[int] = field(default_factory=lambda: {0}),
)
```

{% endraw %}{% include api-source.html name="ScaleConstructionSettings" line=1524 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

The settings of the scale construction exercise: the same choices as
key signature identification.

Here "keys" chooses the scale by the signature it has: G major and E
minor both have one sharp. `staff_keys` is a
separate choice: the key signature drawn on the staff, which need
not be the scale's. On a staff with two flats a C
major scale has to be placed with naturals where the staff would
otherwise flatten the notes.

**Attributes**

- `clefs` (*set of str*): The clefs the scale is placed on, any of `CLEFS`. Keyword-only.
- `modes` (*set of str*): The kinds of scale to ask for, from `KEY_MODES`. Keyword-only.
- `keys` (*set of int*): The key signatures the scales have, as sharps (positive) or flats (negative). Keyword-only.
- `steps` (*bool, default False*): Also mark the whole and half steps between the notes, once the notes are placed. Keyword-only.
- `staff_keys` (*set of int*): The key signatures that may be drawn on the staff, as sharps (positive) or flats (negative); 0 is none. Keyword-only.
- `octave` (*bool, default False*): Name the octave of the first note, such as "G2 Major", and require the scale to start there; any scale asked then fits on the staff and its ledger lines. Without it any octave is accepted. Keyword-only.
- `motion` (*str, default "ascending"*): Direction of the scale, "ascending" or "descending". Keyword-only.
- `minor_keys` (*set of int or None*): Signatures for natural minor. None uses the shared key selection. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = ScaleConstructionSettings(keys={3})
>>> (
...     cfg.active_keys(),
...     cfg.active_clefs(),
...     cfg.steps,
...     cfg.octave,
...     cfg.active_staff_keys(),
... )
([3], ['treble', 'bass'], False, False, [0])
```

### ScaleConstructionSettings.active_staff_keys

<div class="api-signature" markdown="1">

```python
def active_staff_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="ScaleConstructionSettings.active_staff_keys" line=1590 %}{% raw %}

</div>

Return the key signatures that may be drawn on the staff, lowest
first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleConstructionSettings(
...     staff_keys={-2, 3}
... ).active_staff_keys()
[-2, 3]
>>> ScaleConstructionSettings(
...     staff_keys=set()
... ).active_staff_keys()
[0]
```

## ClefBasicsSettings

<div class="api-signature" markdown="1">

```python
ClefBasicsSettings(
    *,
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    question_type: str = 'construction',
)
```

{% endraw %}{% include api-source.html name="ClefBasicsSettings" line=1634 %}{% raw %}

</div>

Bases: `ClefChoice`

The settings of the clef basics exercise: what kind of question is
asked, and which clefs.

Every clef is one of three symbols, the G, C or F clef, put on a
line of the staff: the mezzo-soprano clef is the C clef
on the second line. The three symbols can always be chosen from.

**Attributes**

- `clefs` (*set of str*): The clefs that are asked for, any of `CLEF_BASICS_CLEFS`. Keyword-only.
- `question_type` (*str, default "construction"*): "construction" to put a named clef on a blank staff, or "identification" to name the clef shown on a staff by pressing a button. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasicsSettings(
...     clefs={"subbass", "alto"}
... ).active_clefs()
['alto', 'subbass']
>>> ClefBasicsSettings().question_type
'construction'
```

### ClefBasicsSettings.active_type

<div class="api-signature" markdown="1">

```python
def active_type() -> str
```

{% endraw %}{% include api-source.html name="ClefBasicsSettings.active_type" line=1671 %}{% raw %}

</div>

Return the kind of question to ask.

**Returns**

- *str*: "construction" or "identification"; construction if the setting is anything else.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasicsSettings(
...     question_type="identification"
... ).active_type()
'identification'
>>> ClefBasicsSettings(
...     question_type="nonsense"
... ).active_type()
'construction'
```

### ClefBasicsSettings.answer_clefs

<div class="api-signature" markdown="1">

```python
def answer_clefs() -> list[str]
```

{% endraw %}{% include api-source.html name="ClefBasicsSettings.answer_clefs" line=1698 %}{% raw %}

</div>

Return the clefs to offer as buttons when a clef is to be named:
those asked for, and enough others to have a choice.

**Returns**

- *list of str*: In canonical order; at least two, the treble and bass clefs being added if only one is asked for.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasicsSettings(
...     clefs={"alto", "tenor"}
... ).answer_clefs()
['alto', 'tenor']
>>> ClefBasicsSettings(
...     clefs={"alto"}
... ).answer_clefs()
['treble', 'alto']
```

## NotationSettings

<div class="api-signature" markdown="1">

```python
NotationSettings(
    terms: set[str] = field(default_factory=lambda: set(NOTATION_TERMS)),
    question_type: str = 'button',
)
```

{% endraw %}{% include api-source.html name="NotationSettings" line=1734 %}{% raw %}

</div>

Terms eligible to be highlighted in Notation Identification.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Notehead" in NotationSettings().terms
True
```

## CircleSettings

<div class="api-signature" markdown="1">

```python
CircleSettings(
    questions: set[str] = field(default_factory=lambda: set(CIRCLE_QUESTIONS)),
    scheme: str = DEFAULT_SCHEME,
    customs: list[CustomRecord] = field(default_factory=list),
)
```

{% endraw %}{% include api-source.html name="CircleSettings" line=1765 %}{% raw %}

</div>

The settings of the circle of fifths exercise.

**Attributes**

- `questions` (*set of str*): The kinds of question to ask, keys of `CIRCLE_QUESTIONS`: the relative major of a minor key, the relative minor of a major key, and the Roman numeral of a chord of a key.
- `scheme` (*str*): The key of the color scheme the circle is drawn in: a preset of `alto.circle_schemes` or one of `customs`.
- `customs` (*list of CustomRecord*): The color schemes the user made.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettings().active_questions()
['major', 'minor', 'numeral']
>>> CircleSettings(
...     questions={"numeral"}
... ).active_questions()
['numeral']
>>> CircleSettings().active_scheme().name
'Cyan to indigo'
```

### CircleSettings.active_questions

<div class="api-signature" markdown="1">

```python
def active_questions() -> list[str]
```

{% endraw %}{% include api-source.html name="CircleSettings.active_questions" line=1799 %}{% raw %}

</div>

Return the kinds of question to ask, in the order they are
listed.

**Returns**

- *list of str*: The chosen kinds, or all of them if none is chosen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettings(
...     questions=set()
... ).active_questions()
['major', 'minor', 'numeral']
>>> CircleSettings(
...     questions={"minor", "nonsense"}
... ).active_questions()
['minor']
```

### CircleSettings.active_scheme

<div class="api-signature" markdown="1">

```python
def active_scheme() -> Scheme
```

{% endraw %}{% include api-source.html name="CircleSettings.active_scheme" line=1824 %}{% raw %}

</div>

Return the color scheme to draw the circle in.

**Returns**

- *Scheme*: The chosen scheme, or the default if the saved choice is no longer available, such as a deleted custom scheme.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettings(
...     scheme="midnight"
... ).active_scheme().name
'Midnight'
>>> CircleSettings(
...     scheme="deleted"
... ).active_scheme().key
'cyan-indigo'
```
{% endraw %}
