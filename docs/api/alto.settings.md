---
title: alto.settings
parent: api
package: alto
order: 6
permalink: /api/alto.settings/
---
{% raw %}
User settings. Pure Python (no Qt); persistence lives in ui/settings_panel.py.

Each exercise with settings has a small dataclass here (`NoteNameSettings`, `KeyboardSettings` and so on) and one shared
instance of it (`note_names`, `keyboard` ...) that the exercise and its settings panel both read and write.

**Examples**

```pycon
>>> NoteNameSettings().active_clefs()
['treble', 'bass']
>>> spell(Note.parse("F#4"))
'F♯'
```

## spell

```python
def spell(
    note: Note,
    *,
    naming: str = 'letters',
    key: int = 0,
    octave: bool = False,
) -> str
```

Return a note name in the chosen naming system, optionally including its octave.

**Parameters**

- `note` (*Note*): The note.
- `naming` (*str, default "letters"*): "letters" for C D E, "solfege" for Do Re Mi, "degrees" for caret scale degrees, or "functions" for function names. Keyword-only.
- `key` (*int, default 0*): The major key signature for scale degrees: sharps if positive, flats if negative. Zero means C major. Keyword-only.
- `octave` (*bool, default False*): Include the note's octave, separated from a scale degree by " / ". Keyword-only.

**Returns**

- *str*: The name and, if requested, octave. Carets use accidental prefixes; function names use Raised or Lowered prefixes.

**Examples**

```pycon
>>> spell(Note.parse("F#4"))
'F♯'
>>> spell(Note.parse("F#4"), naming="solfege")
'Fa♯'
>>> spell(Note.parse("F#4"), naming="degrees", key=1)
'7̂'
>>> spell(Note.parse("F4"), naming="degrees", key=1)
'♭7̂'
>>> spell(Note.parse("Eb4"), naming="degrees")
'♭3̂'
>>> spell(Note.parse("G4"), naming="functions", key=1)
'Tonic'
>>> spell(Note.parse("F4"), naming="functions", key=1)
'Lowered Leading tone'
>>> spell(Note.parse("G4"), naming="degrees", key=1, octave=True)
'1̂ / 4'
```

## diatonic_name

```python
def diatonic_name(d: int) -> str
```

Return the name and octave of the natural note on a staff step.

**Parameters**

- `d` (*int*): The staff-step index (see `Note.diatonic`).

**Returns**

- *str*: For example 'E4'.

**Examples**

```pycon
>>> diatonic_name(30)
'E4'
```

## NoteNameSettings

```python
NoteNameSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    ranges: dict[str, tuple[int, int]] = field(default_factory=dict),
    key_signatures: set[int] = field(default_factory=lambda: {0}),
    note_values: set[str] = field(default_factory=lambda: {'whole'}),
    naming: str = 'letters',
    accidentals: bool = False,
    require_octave: bool = False,
)
```

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

```pycon
>>> cfg = NoteNameSettings(clefs={"bass"}, key_signatures={2})
>>> cfg.active_clefs(), cfg.active_keys()
(['bass'], [2])
```

### NoteNameSettings.active_clefs

```python
def active_clefs() -> list[str]
```

Return the clefs to draw from, in canonical order.

**Returns**

- *list of str*: The chosen clefs, or the treble clef if none are chosen.

**Examples**

```pycon
>>> NoteNameSettings(clefs={"grand", "tenor"}).active_clefs()
['tenor', 'grand']
>>> NoteNameSettings(clefs=set()).active_clefs()
['treble']
```

### NoteNameSettings.active_keys

```python
def active_keys() -> list[int]
```

Return the key signatures to draw from, lowest first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```pycon
>>> NoteNameSettings(key_signatures={2, -1}).active_keys()
[-1, 2]
```

### NoteNameSettings.active_values

```python
def active_values() -> list[str]
```

Return the note values to draw, from longest to shortest.

**Returns**

- *list of str*: The chosen values in the order of `NOTE_VALUES`, or whole notes if none are chosen.

**Examples**

```pycon
>>> NoteNameSettings(note_values={"half", "whole"}).active_values()
['whole', 'half']
```

### NoteNameSettings.range_for

```python
def range_for(clef: str) -> tuple[int, int]
```

Return the range of notes that may be asked on a clef.

**Parameters**

- `clef` (*str*): A key of `DEFAULT_RANGES`.

**Returns**

- *tuple of (int, int)*: The lowest and highest staff step, inclusive; the user's override if there is one, otherwise the default.

**Examples**

```pycon
>>> NoteNameSettings().range_for("treble")
(22, 52)
>>> NoteNameSettings(ranges={"treble": (40, 30)}).range_for("treble")  # given the wrong way round
(30, 40)
```

## key_name

```python
def key_name(midi: int) -> str
```

Return the name of a MIDI note with its octave, black keys as sharps.

**Parameters**

- `midi` (*int*): The MIDI note number.

**Returns**

- *str*: For example 'C4' for 60 and 'C♯4' for 61.

**Examples**

```pycon
>>> key_name(60), key_name(61)
('C4', 'C♯4')
```

## KeyboardSettings

```python
KeyboardSettings(
    black_keys: bool = True,
    *,
    require_octave: bool = False,
    low: int = KEYBOARD_DEFAULT[0],
    high: int = KEYBOARD_DEFAULT[1],
    key_signature: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
)
```

The settings of the keyboard identification exercise.

**Attributes**

- `black_keys` (*bool, default True*): Also ask the black keys, answered by either enharmonic name.
- `require_octave` (*bool, default False*): The answer must include the octave number as well. Keyword-only.
- `low` (*int*): The lowest key asked, as a MIDI number. Keyword-only.
- `high` (*int*): The highest key asked, as a MIDI number, inclusive. Keyword-only.
- `key_signature` (*bool, default False*): Show a key signature, and require the name that fits it (no enharmonic spelling). Keyword-only.
- `keys` (*set of int*): The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```pycon
>>> cfg = KeyboardSettings()
>>> key_name(cfg.low), key_name(cfg.high)
('C3', 'C5')
```

### KeyboardSettings.active_keys

```python
def active_keys() -> list[int]
```

Return the key signatures to draw from, lowest first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```pycon
>>> KeyboardSettings().active_keys()
[-3, -2, -1, 0, 1, 2, 3]
```

## ConstructionSettings

```python
ConstructionSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    accidentals: bool = False,
    key_signature: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
)
```

The settings of the note construction exercise.

**Attributes**

- `clefs` (*set of str*): The clefs to ask on, any of `RANGE_KEYS`, so "grand" is allowed.
- `accidentals` (*bool, default False*): Also ask for sharps and flats, which the answer then has to include. Keyword-only.
- `key_signature` (*bool, default False*): Draw a key signature; it applies to the note unless the note is given its own sign. Keyword-only.
- `keys` (*set of int*): The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```pycon
>>> ConstructionSettings(clefs={"grand"}).active_clefs()
['grand']
```

### ConstructionSettings.active_clefs

```python
def active_clefs() -> list[str]
```

Return the clefs to draw from, in canonical order.

**Returns**

- *list of str*: The chosen clefs, or the treble clef if none are chosen.

**Examples**

```pycon
>>> ConstructionSettings().active_clefs()
['treble', 'bass']
```

### ConstructionSettings.active_keys

```python
def active_keys() -> list[int]
```

Return the key signatures to draw from, lowest first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```pycon
>>> ConstructionSettings(keys={3, -2}).active_keys()
[-2, 3]
```

## ArpeggioSettings

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

The settings of the arpeggio identification exercise.

**Attributes**

- `clefs` (*set of str*): The clefs to draw on, any of `CLEFS`.
- `types` (*set of str*): The chord types to ask, from `ARPEGGIO_TYPES`. Keyword-only.
- `inversions` (*set of int*): The inversions to ask: 0 for root position up to 3 for the third inversion. Keyword-only.
- `key_signature` (*bool, default False*): Draw a key signature, so the arpeggio only gets signs where it differs from it. Keyword-only.
- `keys` (*set of int*): The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```pycon
>>> ArpeggioSettings().active_types()
['major', 'minor', 'dominant 7th', 'diminished 7th']
```

### ArpeggioSettings.active_clefs

```python
def active_clefs() -> list[str]
```

Return the clefs to draw from, in canonical order.

**Returns**

- *list of str*: The chosen clefs, or the treble clef if none are chosen.

**Examples**

```pycon
>>> ArpeggioSettings(clefs={"tenor", "alto"}).active_clefs()
['alto', 'tenor']
```

### ArpeggioSettings.active_types

```python
def active_types() -> list[str]
```

Return the chord types to ask, triads first and then seventh chords.

**Returns**

- *list of str*: The chosen types in the order of `ARPEGGIO_TYPES`, or "major" if none are chosen.

**Examples**

```pycon
>>> ArpeggioSettings(types={"minor 7th", "major"}).active_types()
['major', 'minor 7th']
```

### ArpeggioSettings.active_inversions

```python
def active_inversions() -> list[int]
```

Return the inversions to ask, root position first.

**Returns**

- *list of int*: The chosen inversions, or root position (0) if none are chosen.

**Examples**

```pycon
>>> ArpeggioSettings(inversions={2, 0}).active_inversions()
[0, 2]
```

### ArpeggioSettings.inversions_for

```python
def inversions_for(chord_type: str) -> list[int]
```

Return the inversions that can be asked for a chord type.

A triad has no third inversion. If none of the chosen inversions applies (only the third, for a triad), root position is
used.

**Parameters**

- `chord_type` (*str*): A key of `CHORDS`, such as "major" or "dominant 7th".

**Returns**

- *list of int*: The inversions to choose from.

**Examples**

```pycon
>>> cfg = ArpeggioSettings()
>>> cfg.inversions_for("major"), cfg.inversions_for("dominant 7th")
([0, 1, 2], [0, 1, 2, 3])
>>> ArpeggioSettings(inversions={3}).inversions_for("major")
[0]
```

### ArpeggioSettings.active_keys

```python
def active_keys() -> list[int]
```

Return the key signatures to draw from, lowest first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```pycon
>>> ArpeggioSettings(keys={1}).active_keys()
[1]
```

## KeySignatureSettings

```python
KeySignatureSettings(
    *,
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    modes: set[str] = field(default_factory=lambda: {'Major (Ionian)', 'Natural minor (Aeolian)'}),
    keys: set[int] = field(default_factory=lambda: set(range(-7, 8))),
)
```

The settings of the key signature identification exercise.

**Attributes**

- `clefs` (*set of str*): The clefs a signature is drawn on, any of `CLEFS`. Keyword-only.
- `modes` (*set of str*): The scales to ask about, from `KEY_MODES`. Keyword-only.
- `keys` (*set of int*): The key signatures asked, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```pycon
>>> cfg = KeySignatureSettings()
>>> cfg.active_clefs(), len(cfg.active_keys())
(['treble', 'bass'], 15)
```

### KeySignatureSettings.active_clefs

```python
def active_clefs() -> list[str]
```

Return the clefs to draw signatures on, in canonical order.

**Returns**

- *list of str*: The chosen clefs, or the treble clef if none are chosen.

**Examples**

```pycon
>>> KeySignatureSettings().active_clefs()
['treble', 'bass']
```

### KeySignatureSettings.active_modes

```python
def active_modes() -> list[str]
```

Return the scales to ask about, in the order of `KEY_MODES`.

**Returns**

- *list of str*: The chosen modes, or major if none are chosen.

**Examples**

```pycon
>>> KeySignatureSettings().active_modes()
['Major (Ionian)', 'Natural minor (Aeolian)']
```

### KeySignatureSettings.active_keys

```python
def active_keys() -> list[int]
```

Return the key signatures to ask about, lowest first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```pycon
>>> KeySignatureSettings(keys={3, -4}).active_keys()
[-4, 3]
```

## KeyConstructionSettings

```python
KeyConstructionSettings()
```

Bases: `KeySignatureSettings`

The settings of the key signature construction exercise: the same choices as key signature identification.

**Attributes**

- `clefs` (*set of str*): The clefs the blank staff is drawn in, any of `CLEFS`. Keyword-only.
- `modes` (*set of str*): The scales to ask for, from `KEY_MODES`. Keyword-only.
- `keys` (*set of int*): The key signatures to build, as sharps (positive) or flats (negative). Keyword-only.

**Examples**

```pycon
>>> cfg = KeyConstructionSettings(keys={-2})
>>> cfg.active_keys(), cfg.active_modes()
([-2], ['Major (Ionian)', 'Natural minor (Aeolian)'])
```

## ScaleIdentificationSettings

```python
ScaleIdentificationSettings(
    *,
    staff_keys: set[int] = field(default_factory=lambda: {0}),
)
```

Bases: `KeySignatureSettings`

Choose the clefs, scale types and independent staff and scale key signatures for identification.

**Attributes**

- `staff_keys` (*set of int*): Signatures drawn on the staff, independently of the scale's own signature. Keyword-only.

**Examples**

```pycon
>>> cfg = ScaleIdentificationSettings(keys={2}, staff_keys={-3})
>>> cfg.active_keys(), cfg.active_staff_keys()
([2], [-3])
```

### ScaleIdentificationSettings.active_staff_keys

```python
def active_staff_keys() -> list[int]
```

Return the selected staff signatures, falling back to no signature.

**Returns**

- *list of int*: Signature counts in ascending order.

**Examples**

```pycon
>>> ScaleIdentificationSettings(staff_keys=set()).active_staff_keys()
[0]
```

## ScaleConstructionSettings

```python
ScaleConstructionSettings(
    *,
    steps: bool = False,
    octave: bool = False,
    staff_keys: set[int] = field(default_factory=lambda: {0}),
)
```

Bases: `KeySignatureSettings`

The settings of the scale construction exercise: the same choices as key signature identification.

Here "keys" chooses the scale by the signature it has: G major and E minor both have one sharp. `staff_keys` is a
separate choice: the key signature drawn on the staff, which need not be the scale's. On a staff with two flats a C
major scale has to be placed with naturals where the staff would otherwise flatten the notes.

**Attributes**

- `clefs` (*set of str*): The clefs the scale is placed on, any of `CLEFS`. Keyword-only.
- `modes` (*set of str*): The kinds of scale to ask for, from `KEY_MODES`. Keyword-only.
- `keys` (*set of int*): The key signatures the scales have, as sharps (positive) or flats (negative). Keyword-only.
- `steps` (*bool, default False*): Also mark the whole and half steps between the notes, once the notes are placed. Keyword-only.
- `staff_keys` (*set of int*): The key signatures that may be drawn on the staff, as sharps (positive) or flats (negative); 0 is none. Keyword-only.
- `octave` (*bool, default False*): Name the octave of the first note, such as "G2 Major", and require the scale to start there; any scale asked then fits on the staff and its ledger lines. Without it any octave is accepted. Keyword-only.

**Examples**

```pycon
>>> cfg = ScaleConstructionSettings(keys={3})
>>> cfg.active_keys(), cfg.active_clefs(), cfg.steps, cfg.octave, cfg.active_staff_keys()
([3], ['treble', 'bass'], False, False, [0])
```

### ScaleConstructionSettings.active_staff_keys

```python
def active_staff_keys() -> list[int]
```

Return the key signatures that may be drawn on the staff, lowest first.

**Returns**

- *list of int*: Sharps (positive) or flats (negative); no sharps or flats if none are chosen.

**Examples**

```pycon
>>> ScaleConstructionSettings(staff_keys={-2, 3}).active_staff_keys()
[-2, 3]
>>> ScaleConstructionSettings(staff_keys=set()).active_staff_keys()
[0]
```

## ClefBasicsSettings

```python
ClefBasicsSettings(
    *,
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    question_type: str = 'construction',
)
```

The settings of the clef basics exercise: what kind of question is asked, and which clefs.

Every clef is one of three symbols, the G, C or F clef, put on a line of the staff: the mezzo-soprano clef is the C clef
on the second line. The three symbols can always be chosen from.

**Attributes**

- `clefs` (*set of str*): The clefs that are asked for, any of `CLEF_BASICS_CLEFS`. Keyword-only.
- `question_type` (*str, default "construction"*): "construction" to put a named clef on a blank staff, or "identification" to name the clef shown on a staff by pressing a button. Keyword-only.

**Examples**

```pycon
>>> ClefBasicsSettings(clefs={"subbass", "alto"}).active_clefs()
['alto', 'subbass']
>>> ClefBasicsSettings().question_type
'construction'
```

### ClefBasicsSettings.active_clefs

```python
def active_clefs() -> list[str]
```

Return the clefs to ask for, in canonical order.

**Returns**

- *list of str*: The chosen clefs, or the treble clef if none are chosen.

**Examples**

```pycon
>>> ClefBasicsSettings().active_clefs()
['treble', 'bass']
>>> ClefBasicsSettings(clefs=set()).active_clefs()
['treble']
```

### ClefBasicsSettings.active_type

```python
def active_type() -> str
```

Return the kind of question to ask.

**Returns**

- *str*: "construction" or "identification"; construction if the setting is anything else.

**Examples**

```pycon
>>> ClefBasicsSettings(question_type="identification").active_type()
'identification'
>>> ClefBasicsSettings(question_type="nonsense").active_type()
'construction'
```

### ClefBasicsSettings.answer_clefs

```python
def answer_clefs() -> list[str]
```

Return the clefs to offer as buttons when a clef is to be named: those asked for, and enough others to have a choice.

**Returns**

- *list of str*: In canonical order; at least two, the treble and bass clefs being added if only one is asked for.

**Examples**

```pycon
>>> ClefBasicsSettings(clefs={"alto", "tenor"}).answer_clefs()
['alto', 'tenor']
>>> ClefBasicsSettings(clefs={"alto"}).answer_clefs()
['treble', 'alto']
```

## CircleSettings

```python
CircleSettings(
    questions: set[str] = field(default_factory=lambda: set(CIRCLE_QUESTIONS)),
    scheme: str = DEFAULT_SCHEME,
    customs: list[CustomRecord] = field(default_factory=list),
)
```

The settings of the circle of fifths exercise.

**Attributes**

- `questions` (*set of str*): The kinds of question to ask, keys of `CIRCLE_QUESTIONS`: the relative major of a minor key, the relative minor of a major key, and the Roman numeral of a chord of a key.
- `scheme` (*str*): The key of the colour scheme the circle is drawn in: a preset of `alto.circle_schemes` or one of `customs`.
- `customs` (*list of CustomRecord*): The colour schemes the user made.

**Examples**

```pycon
>>> CircleSettings().active_questions()
['major', 'minor', 'numeral']
>>> CircleSettings(questions={"numeral"}).active_questions()
['numeral']
>>> CircleSettings().active_scheme().name
'Cyan to indigo'
```

### CircleSettings.active_questions

```python
def active_questions() -> list[str]
```

Return the kinds of question to ask, in the order they are listed.

**Returns**

- *list of str*: The chosen kinds, or all of them if none is chosen.

**Examples**

```pycon
>>> CircleSettings(questions=set()).active_questions()
['major', 'minor', 'numeral']
>>> CircleSettings(questions={"minor", "nonsense"}).active_questions()
['minor']
```

### CircleSettings.active_scheme

```python
def active_scheme() -> Scheme
```

Return the colour scheme to draw the circle in.

**Returns**

- *Scheme*: The chosen scheme, or the default one if the choice is not a scheme any more (a deleted one of the user's own).

**Examples**

```pycon
>>> CircleSettings(scheme="midnight").active_scheme().name
'Midnight'
>>> CircleSettings(scheme="deleted").active_scheme().key
'cyan-indigo'
```
{% endraw %}
