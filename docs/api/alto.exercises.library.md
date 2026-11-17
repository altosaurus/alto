---
title: alto.exercises.library
parent: api
package: alto.exercises
order: 9
permalink: /api/alto.exercises.library/
---
{% raw %}
The exercises: note names, intervals, key signatures, scales, chords, arpeggios, keyboard keys and note construction.

Each class makes one kind of `Question` and registers itself with `@register`, so importing this module is what adds
the exercises to the home screen.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> [cls.name for cls in REGISTRY][:3]
['Note Identification', 'Keyboard Note Identification', 'Note Construction']
```

## NoteNames

```python
NoteNames(accidentals: bool = False)
```

Bases: `Exercise`

Name the note shown on a staff.

**Examples**

```pycon
>>> q = NoteNames().generate(random.Random(1))
>>> len(q.staff), q.answer in q.choices
(1, True)
```

**Constructor**

Create the exercise.

**Parameters**

- `accidentals` (*bool, default False*): Ask notes with explicit sharps, flats and naturals, whatever the settings say.

**Constructor examples**

```pycon
>>> NoteNames(accidentals=True).accidentals
True
```

### NoteNames.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, ranges, key signatures, note values and naming in force, and whether accidentals are asked.

**Examples**

```pycon
>>> NoteNames().settings_signature() != NoteNames(accidentals=True).settings_signature()
True
```

### NoteNames.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "Press the button with its name" in NoteNames().instructions()
True
```

### NoteNames.generate

```python
def generate(rng: random.Random) -> Question
```

Make a note to name, on one of the chosen clefs, in a chosen key.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The note drawn on a staff, with one button for each name that could be the answer.

**Examples**

```pycon
>>> q = NoteNames().generate(random.Random(2))
>>> q.clef in ("treble", "bass", "alto", "tenor", "soprano", "mezzo", "baritone", "grand")
True
```

## IntervalNames

```python
class IntervalNames(Exercise)
```

Name the interval between two notes, up to an octave.

**Attributes**

- `QUALITIES` (*dict of int to str*): For each interval number, the qualities that can occur, separated by spaces.

**Examples**

```pycon
>>> q = IntervalNames().generate(random.Random(3))
>>> len(q.staff), q.answer in q.choices
(2, True)
```

### IntervalNames.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "quality followed by a number" in IntervalNames().instructions()
True
```

### IntervalNames.generate

```python
def generate(rng: random.Random) -> Question
```

Make two notes whose interval is to be named.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The lower and higher note on a staff, and the interval (such as 'M3' or 'P5') as the answer.

**Examples**

```pycon
>>> q = IntervalNames().generate(random.Random(4))
>>> q.answer[0] in "PMmAd" and q.answer[1:].isdigit()
True
```

## KeyboardIntervals

```python
class KeyboardIntervals(Exercise)
```

Identify the ascending interval between two highlighted piano keys.

**Attributes**

- `INTERVALS` (*tuple of str*): Conventional names for every distance on the piano, including compound intervals and combined tritone answers.

**Examples**

```pycon
>>> q = KeyboardIntervals().generate(random.Random(5))
>>> len(q.keyboard_notes), q.answer in q.choices, q.staff
(2, True, [])
```

### KeyboardIntervals.settings_signature

```python
def settings_signature() -> str
```

Identify the keyboard range and selected intervals for stored-question reviews.

**Returns**

- *str*: The settings that determine which questions can be asked.

**Examples**

```pycon
>>> bool(KeyboardIntervals().settings_signature())
True
```

### KeyboardIntervals.instructions

```python
def instructions() -> str
```

Explain how to identify an interval from two highlighted keys.

**Returns**

- *str*: HTML explaining interval names and enharmonic ambiguity on the keyboard.

**Examples**

```pycon
>>> "A4 / d5" in KeyboardIntervals().instructions()
True
```

### KeyboardIntervals.generate

```python
def generate(rng: random.Random) -> Question
```

Highlight two distinct keys at a selected interval within the chosen range.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: Two highlighted keys and either a limited number of choices or a fixed bank for every selected interval. A prompt is returned if none are selected.

**Examples**

```pycon
>>> q = KeyboardIntervals().generate(random.Random(7))
>>> 1 <= q.keyboard_notes[1].midi - q.keyboard_notes[0].midi <= 12
True
```

## KeySignatures

```python
class KeySignatures(Exercise)
```

Read a key signature drawn on a staff and name the key it belongs to.

**Examples**

```pycon
>>> q = KeySignatures().generate(random.Random(5))
>>> q.answer in q.choices
True
```

### KeySignatures.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The kinds of question, clefs, scales and key signatures in force.

**Examples**

```pycon
>>> KeySignatures().settings_signature().startswith("[")
True
```

### KeySignatures.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "Key Signature Identification" in KeySignatures().instructions()
True
```

### KeySignatures.refresh

```python
def refresh(question: Question) -> Question
```

Give a stored signature question the caption on its staff that older versions did not write.

**Parameters**

- `question` (*Question*): The question as it was stored.

**Returns**

- *Question*: The same question, captioned '_ Major' (or '_ minor', '_ Dorian' and so on) if it shows a staff and had no caption.

**Examples**

```pycon
>>> old = Question("Which minor key has this key signature?", choices=["C"], answer="C", key=-3, show_staff=True)
>>> KeySignatures().refresh(old).caption
'_ minor'
```

### KeySignatures.generate

```python
def generate(rng: random.Random) -> Question
```

Make a key signature to read.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: A signature on a staff; the answer is the tonic of the scale that has it.

**Examples**

```pycon
>>> q = KeySignatures().generate(random.Random(6))
>>> q.show_staff and q.answer in q.choices
True
```

## KeySignatureConstruction

```python
class KeySignatureConstruction(Exercise)
```

Build the key signature of a named key on a blank staff, with the fork.

**Examples**

```pycon
>>> q = KeySignatureConstruction().generate(random.Random(5))
>>> q.build_key, q.staff, q.choices
(True, [], [])
```

### KeySignatureConstruction.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, scales and key signatures in force.

**Examples**

```pycon
>>> KeySignatureConstruction().settings_signature().startswith("[")
True
```

### KeySignatureConstruction.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "Key Signature Construction" in KeySignatureConstruction().instructions()
True
```

### KeySignatureConstruction.generate

```python
def generate(rng: random.Random) -> Question
```

Name a key whose signature is to be built.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: A blank staff captioned with the key, such as 'D Major'; the answer is its sharps or flats.

**Examples**

```pycon
>>> q = KeySignatureConstruction().generate(random.Random(1))
>>> q.caption.split()[0] in {"C", "D", "E", "F", "G", "A", "B"} or "♯" in q.caption or "♭" in q.caption
True
>>> q.answer == format_key_signature(q.key)
True
```

## ScaleIdentification

```python
class ScaleIdentification(Exercise)
```

Identify the tonic and type of a scale drawn on a staff.

**Examples**

```pycon
>>> q = ScaleIdentification().generate(random.Random(7))
>>> len(q.staff), q.answer in q.choices
(8, True)
```

### ScaleIdentification.settings_signature

```python
def settings_signature() -> str
```

Identify the clefs, scale types and staff and scale signatures in force.

**Returns**

- *str*: The serialized question settings.

**Examples**

```pycon
>>> ScaleIdentification().settings_signature().startswith("[")
True
```

### ScaleIdentification.instructions

```python
def instructions() -> str
```

Explain how to identify the scale, including a staff with a different signature.

**Returns**

- *str*: Simple HTML help text.

**Examples**

```pycon
>>> "Scale Identification" in ScaleIdentification().instructions()
True
```

### ScaleIdentification.generate

```python
def generate(rng: random.Random) -> Question
```

Draw a one-octave scale and offer scale names without revealing the answer on the staff.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: Eight staff notes and a choice of tonic and scale type.

**Examples**

```pycon
>>> q = ScaleIdentification().generate(random.Random(8))
>>> q.staff[0][0].name == q.staff[-1][0].name and not q.caption
True
```

## ScaleConstruction

```python
class ScaleConstruction(Exercise)
```

Place the notes of a named scale on a blank staff, one after another.

**Examples**

```pycon
>>> q = ScaleConstruction().generate(random.Random(5))
>>> len(q.construct_scale or []), q.choices, q.key
(8, [], 0)
```

### ScaleConstruction.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, scales and key signatures in force.

**Examples**

```pycon
>>> ScaleConstruction().settings_signature().startswith("[")
True
```

### ScaleConstruction.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "Scale Construction" in ScaleConstruction().instructions()
True
```

### ScaleConstruction.generate

```python
def generate(rng: random.Random) -> Question
```

Name a scale to be placed on the staff.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: A blank staff captioned with the scale, such as 'D Major'. The eight notes in the selected direction are stored in `construct_scale`.

**Examples**

```pycon
>>> q = ScaleConstruction().generate(random.Random(1))
>>> scale = q.construct_scale or []
>>> scale[0].name == scale[-1].name and q.accidentals
True
>>> q.check_scale(scale)
True
```

## CircleOfFifths

```python
class CircleOfFifths(Exercise)
```

Questions on the circle of fifths: a relative major, a relative minor, or the Roman numeral of a chord.

**Examples**

```pycon
>>> q = CircleOfFifths().generate(random.Random(3))
>>> q.circle is not None and q.answer in q.choices
True
```

### CircleOfFifths.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The kinds of question in force.

**Examples**

```pycon
>>> CircleOfFifths().settings_signature().startswith("[")
True
```

### CircleOfFifths.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML, with a paragraph for each kind of question that is switched on.

**Examples**

```pycon
>>> "circle of fifths" in CircleOfFifths().instructions()
True
```

### CircleOfFifths.generate

```python
def generate(rng: random.Random) -> Question
```

Pick a kind of question that is switched on, and ask it.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: A question on the circle: `circle_kind` says which kind.

**Examples**

```pycon
>>> settings.circle.questions = {"minor"}
>>> q = CircleOfFifths().generate(random.Random(5))
>>> q.circle_kind, q.prompt
('minor', 'Which minor key is the relative minor of F major?')
>>> settings.circle.questions = set(settings.CIRCLE_QUESTIONS)
```

## ChordQualities

```python
class ChordQualities(Exercise)
```

Identify the quality of a triad or seventh chord in root position.

**Examples**

```pycon
>>> q = ChordQualities().generate(random.Random(9))
>>> len(q.staff[0]) in (3, 4) and q.answer in q.choices
True
```

### ChordQualities.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "root position" in ChordQualities().instructions()
True
```

### ChordQualities.generate

```python
def generate(rng: random.Random) -> Question
```

Make a chord in root position whose quality is to be named.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The chord drawn as one stack of notes, with its type (such as 'minor 7th') as the answer.

**Examples**

```pycon
>>> q = ChordQualities().generate(random.Random(10))
>>> q.answer in CHORDS
True
```

## ArpeggioNames

```python
class ArpeggioNames(Exercise)
```

Name the type and the inversion of a broken chord.

**Examples**

```pycon
>>> q = ArpeggioNames().generate(random.Random(11))
>>> q.octaves is not None and len(q.staff) >= 4
True
```

### ArpeggioNames.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, chord types, inversions and key signatures in force.

**Examples**

```pycon
>>> ArpeggioNames().settings_signature().startswith("[")
True
```

### ArpeggioNames.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "inversion" in ArpeggioNames().instructions()
True
```

### ArpeggioNames.generate

```python
def generate(rng: random.Random) -> Question
```

Make an arpeggio on one of the chosen clefs, in a chosen position.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The arpeggio's notes one after another on a staff; the answer is the chord type and inversion, such as 'major · 1st inversion'.

**Raises**

- *RuntimeError*: If no arpeggio fits the chosen clefs, chord types and inversions.

**Examples**

```pycon
>>> q = ArpeggioNames().generate(random.Random(12))
>>> " · " in q.answer
True
```

## KeyboardNotes

```python
class KeyboardNotes(Exercise)
```

Name the highlighted key on a piano keyboard.

**Examples**

```pycon
>>> q = KeyboardNotes().generate(random.Random(13))
>>> q.keyboard is not None and q.answer in q.choices
True
```

### KeyboardNotes.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The keyboard range, black keys, octave and key signature settings, and the naming in force.

**Examples**

```pycon
>>> KeyboardNotes().settings_signature().startswith("[")
True
```

### KeyboardNotes.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML, with paragraphs added for the octave and key signature settings that are on.

**Examples**

```pycon
>>> "highlighted" in KeyboardNotes().instructions()
True
```

### KeyboardNotes.generate

```python
def generate(rng: random.Random) -> Question
```

Make a keyboard with one key highlighted.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The keyboard, a grid of name buttons (and a row of octave buttons if octaves are asked), and the key's name as the answer, with the other spelling of a black key accepted.

**Examples**

```pycon
>>> q = KeyboardNotes().generate(random.Random(14))
>>> # noinspection PyUnresolvedReferences
>>> q.keyboard_range[0] <= q.keyboard.midi <= q.keyboard_range[1]
True
```

## NoteConstruction

```python
class NoteConstruction(Exercise)
```

Place a named note on the staff.

**Examples**

```pycon
>>> q = NoteConstruction().generate(random.Random(15))
>>> q.construct is not None and q.prompt.startswith("Place ")
True
```

### NoteConstruction.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, accidentals and key signature settings, and the naming in force.

**Examples**

```pycon
>>> NoteConstruction().settings_signature().startswith("[")
True
```

### NoteConstruction.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML, with paragraphs added for the key signature and accidental settings that are on.

**Examples**

```pycon
>>> "Click the staff" in NoteConstruction().instructions()
True
```

### NoteConstruction.generate

```python
def generate(rng: random.Random) -> Question
```

Make a note name to be placed on the staff.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: A prompt such as 'Place F♯4 on the staff.'; the answer is the note's name, and `construct` is the note to place.

**Examples**

```pycon
>>> q = NoteConstruction().generate(random.Random(16))
>>> q.answer in q.prompt
True
```

## ClefBasics

```python
class ClefBasics(Exercise)
```

Put a named clef on a blank staff: choose the G, C or F symbol and put it on the line that makes the clef asked for.

**Examples**

```pycon
>>> q = ClefBasics().generate(random.Random(1))
>>> q.answer == q.place_clef and q.place_clef in settings.CLEF_BASICS_CLEFS
True
```

### ClefBasics.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs asked for.

**Examples**

```pycon
>>> ClefBasics().settings_signature().startswith("[")
True
```

### ClefBasics.instructions

```python
def instructions() -> str
```

Return the help text for the exercise, for the kind of question that is being asked.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> "Clef Basics" in ClefBasics().instructions()
True
```

### ClefBasics.generate

```python
def generate(rng: random.Random) -> Question
```

Name a clef to place, or draw a clef to name.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: For construction, a blank staff and the name of the clef, which is the question written under the staff. For identification, a staff with the clef drawn on it, and a button for each clef that can be asked for.

**Examples**

```pycon
>>> q = ClefBasics().generate(random.Random(3))
>>> q.prompt.startswith("Place the ") and q.caption == q.prompt
True
>>> settings.clef_basics.question_type = "identification"
>>> q = ClefBasics().generate(random.Random(3))
>>> q.answer in q.choices, q.place_clef, q.caption
(True, '', 'Which clef is this?')
>>> settings.clef_basics.question_type = "construction"
```
{% endraw %}
