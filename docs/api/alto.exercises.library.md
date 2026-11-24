---
title: alto.exercises.library
parent: api
package: alto.exercises
permalink: /api/alto.exercises.library/
---
{% raw %}
The exercises: note names, intervals, key signatures, scales, chords,
arpeggios, keyboard keys and note construction.

Each class makes one kind of `Question` and registers itself with
`@register`, so importing this module is what adds
the exercises to the home screen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> [cls.name for cls in REGISTRY][:3]
['Note Identification', 'Keyboard Note Identification', 'Note
Construction']
```

## NoteNames

```python
NoteNames(accidentals: bool = False)
```

Bases: `ChoiceExercise`

Name the note shown on a staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NoteNames().generate(random.Random(1))
>>> len(q.staff), q.answer in q.choices
(1, True)
```

**Constructor**

Create the exercise.

**Parameters**

- `accidentals` (*bool, default False*): Ask notes with explicit sharps, flats and naturals, whatever the settings say.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames(accidentals=True).accidentals
True
```

### NoteNames.card_prompt

```python
def card_prompt(question: Question) -> str
```

Say what to name on a flashcard, and in which form: letters,
solfège or a scale degree, with the octave if it counts.

**Parameters**

- `question` (*Question*): The question on the card.

**Returns**

- *str*: The instruction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames().card_prompt(
...     Question("", choices=[], answer="C")
... )
'Identify the note.'
```

### NoteNames.practice_signature

```python
def practice_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, ranges, key signatures, note values and naming in force, and whether accidentals are asked.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames().settings_signature() != NoteNames(
...     accidentals=True
... ).settings_signature()
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Press the button with its name"
...     in NoteNames().instructions()
... )
True
```

### NoteNames.make_question

```python
def make_question(rng: random.Random) -> Question
```

Make a note to name, on one of the chosen clefs, in a chosen
key.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The note drawn on a staff, with one button for each name that could be the answer.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NoteNames().generate(random.Random(2))
>>> q.clef in (
...     "treble",
...     "bass",
...     "alto",
...     "tenor",
...     "soprano",
...     "mezzo",
...     "baritone",
...     "grand",
... )
True
```

### NoteNames.card_count

```python
def card_count() -> int
```

Count written pitches across the selected ranges, clefs and
signatures.

**Returns**

- *int*: Each staff position contributes one spelling, or three when accidentals are enabled.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames().card_count() > 0
True
```

### NoteNames.daily_candidates

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

Visit each selectable written note once, in shuffled order.

**Parameters**

- `rng` (*random.Random*): Source of the daily order and answer choices.

**Yields**

- *Question*: A distinct question within the selected clefs, ranges and keys.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> isinstance(
...     next(
...         NoteNames().daily_candidates(
...             random.Random(0)
...         )
...     ),
...     Question,
... )
True
```

### NoteNames.review_question

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

Rebuild a previously seen note when its pitch and answer are
eligible.

**Parameters**

- `question` (*Question*): Saved note and answer.
- `same_settings` (*bool*): Whether its original settings are active.

**Returns**

- *Question or None*: The note with the current answer bank, or None outside the selected material.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NoteNames()
>>> q = ex.generate(random.Random(1))
>>> ex.review_question(
...     q, same_settings=True
... ) == q
True
```

## IntervalNames

```python
class IntervalNames(Exercise)
```

Name the interval between two written notes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = IntervalNames().generate(
...     random.Random(3)
... )
>>> (
...     [len(chord) for chord in q.staff],
...     q.answer in q.choices,
... )
([2], True)
```

### IntervalNames.card_prompt

```python
def card_prompt(question: Question) -> str
```

Say whether to name the interval's number, its quality, both, or
its inversion.

**Parameters**

- `question` (*Question*): The question on the card.

**Returns**

- *str*: The instruction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalNames().card_prompt(
...     Question("", choices=[], answer="3")
... )
'Identify the numeric interval.'
>>> IntervalNames().card_prompt(
...     Question("", choices=[], answer="M3")
... )
'Identify the interval and quality.'
```

### IntervalNames.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "quality followed by a number"
...     in IntervalNames().instructions()
... )
True
```

### IntervalNames.settings_signature

```python
def settings_signature() -> str
```

Identify the settings used to generate and grade the interval.

**Returns**

- *str*: The stored-question review signature.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Harmonic" in IntervalNames().settings_signature()
True
```

### IntervalNames.refresh

```python
def refresh(question: Question) -> Question
```

Arrange written interval answers by quality, with interval
numbers in columns.

**Parameters**

- `question` (*Question*): A new or saved interval question.

**Returns**

- *Question*: The same answer choices in reading order. Perfect and major share a row.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "",
...     choices=["d3", "m3", "P4", "M3", "A3"],
...     answer="m3",
... )
>>> IntervalNames().refresh(q).choices
['A3', 'M3', 'P4', 'm3', 'd3']
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = IntervalNames().generate(
...     random.Random(4)
... )
>>> q.answer[0] in "PMmAd" and q.answer[
...     1:
... ].isdigit()
True
```

## IntervalConstruction

```python
class IntervalConstruction(Exercise)
```

Place a second written note at the requested interval from a given
note.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = IntervalConstruction().generate(
...     random.Random(2)
... )
>>> q.construct is not None and q.check_placed(
...     q.construct
... )
True
```

### IntervalConstruction.instructions

```python
def instructions() -> str
```

Explain staff placement and spelling for interval construction.

**Returns**

- *str*: Instructions for mouse and keyboard input.

**Examples**

```text
The reference describes the difference between melodic and
harmonic placement.
```

### IntervalConstruction.settings_signature

```python
def settings_signature() -> str
```

Identify the construction settings used to generate a stored
card.

**Returns**

- *str*: Stable signature of the exercise options.

**Examples**

```text
A change in staff ranges changes which stored questions are
eligible.
```

### IntervalConstruction.generate

```python
def generate(rng: random.Random) -> Question
```

Generate a staff, an interval prompt, and its eligible
placements.

**Parameters**

- `rng` (*random.Random*): Generator for the presentation.

**Returns**

- *Question*: Written interval to construct.

**Examples**

```text
A harmonic question asks for a note above its starting note.
```

## KeyboardIntervals

```python
class KeyboardIntervals(Exercise)
```

Identify the ascending interval between two highlighted piano keys.

**Attributes**

- `INTERVALS` (*tuple of str*): Conventional names for every distance on the piano, including compound intervals and combined tritone answers.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeyboardIntervals().generate(
...     random.Random(5)
... )
>>> (
...     len(q.keyboard_notes),
...     q.answer in q.choices,
...     q.staff,
... )
(2, True, [])
```

### KeyboardIntervals.card_prompt

```python
def card_prompt(question: Question) -> str
```

Say what to name on a flashcard.

**Parameters**

- `question` (*Question*): The question on the card.

**Returns**

- *str*: The instruction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervals().card_prompt(
...     Question("", choices=[], answer="P5")
... )
'Identify the interval.'
```

### KeyboardIntervals.settings_signature

```python
def settings_signature() -> str
```

Identify the keyboard range and selected intervals for
stored-question reviews.

**Returns**

- *str*: The settings that determine which questions can be asked.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bool(
...     KeyboardIntervals().settings_signature()
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> "A4 / d5" in KeyboardIntervals().instructions()
True
```

### KeyboardIntervals.generate

```python
def generate(rng: random.Random) -> Question
```

Highlight two distinct keys at a selected interval within the
chosen range.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: Two highlighted keys and either a limited number of choices or a fixed bank for every selected interval. A prompt is returned if none are selected.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeyboardIntervals().generate(
...     random.Random(7)
... )
>>> 1 <= q.keyboard_notes[
...     1
... ].midi - q.keyboard_notes[0].midi <= 12
True
```

## KeySignatures

```python
class KeySignatures(ChoiceExercise)
```

Read a key signature drawn on a staff and name the key it belongs
to.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatures().generate(
...     random.Random(5)
... )
>>> q.answer in q.choices
True
```

### KeySignatures.practice_signature

```python
def practice_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The kinds of question, clefs, scales and key signatures in force.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatures().settings_signature().startswith(
...     "["
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Key Signature Identification"
...     in KeySignatures().instructions()
... )
True
```

### KeySignatures.refresh

```python
def refresh(question: Question) -> Question
```

Give a stored signature question the caption on its staff that
older versions did not write.

**Parameters**

- `question` (*Question*): The question as it was stored.

**Returns**

- *Question*: The same question, captioned '_ Major' (or '_ minor', '_ Dorian' and so on) if it shows a staff and had no caption.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> old = Question(
...     "Which minor key has this key signature?",
...     choices=["C"],
...     answer="C",
...     key=-3,
...     show_staff=True,
... )
>>> KeySignatures().refresh(old).caption
'_ minor'
```

### KeySignatures.make_question

```python
def make_question(rng: random.Random) -> Question
```

Make a key signature to read.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: A signature on a staff; the answer is the tonic of the scale that has it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatures().generate(
...     random.Random(6)
... )
>>> q.show_staff and q.answer in q.choices
True
```

## KeySignatureConstruction

```python
class KeySignatureConstruction(Exercise)
```

Build the key signature of a named key on a blank staff, with the
fork.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatureConstruction().generate(
...     random.Random(5)
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatureConstruction().settings_signature().startswith(
...     "["
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Key Signature Construction"
...     in KeySignatureConstruction().instructions()
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatureConstruction().generate(
...     random.Random(1)
... )
>>> q.caption.split()[0] in {
...     "C",
...     "D",
...     "E",
...     "F",
...     "G",
...     "A",
...     "B",
... } or "♯" in q.caption or "♭" in q.caption
True
>>> q.answer == format_key_signature(q.key)
True
```

## OrderOfKeys

```python
class OrderOfKeys(Exercise)
```

Write the accidentals of a named key signature in order.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeys().generate(
...     random.Random(1)
... ).place_signature
True
```

### OrderOfKeys.settings_signature

```python
def settings_signature() -> str
```

Identify the selections used to generate a practice question.

**Returns**

- *str*: The original empty signature at the defaults, so earlier questions remain available for review.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeys().settings_signature()
''
```

### OrderOfKeys.instructions

```python
def instructions() -> str
```

Explain how to enter and submit a signature.

**Returns**

- *str*: The exercise help text.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Undo" in OrderOfKeys().instructions()
True
```

### OrderOfKeys.generate

```python
def generate(rng: random.Random) -> Question
```

Choose a key from the selected scales and signatures and spell
it in a selected clef.

**Parameters**

- `rng` (*random.Random*): Source for the key, mode, and clef.

**Returns**

- *Question*: The named key and the ordered signs with their exact staff octaves.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = OrderOfKeys().generate(random.Random(2))
>>> q.show_staff and not q.choices
True
```

## ScaleIdentification

```python
class ScaleIdentification(Exercise)
```

Identify the tonic and type of a scale drawn on a staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleIdentification().generate(
...     random.Random(7)
... )
>>> len(q.staff), q.answer in q.choices
(8, True)
```

### ScaleIdentification.settings_signature

```python
def settings_signature() -> str
```

Identify the clefs, scale types and staff and scale signatures
in force.

**Returns**

- *str*: The serialized question settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleIdentification().settings_signature().startswith(
...     "["
... )
True
```

### ScaleIdentification.instructions

```python
def instructions() -> str
```

Explain how to identify the scale, including a staff with a
different signature.

**Returns**

- *str*: Simple HTML help text.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Scale Identification"
...     in ScaleIdentification().instructions()
... )
True
```

### ScaleIdentification.generate

```python
def generate(rng: random.Random) -> Question
```

Draw a one-octave scale and offer scale names without revealing
the answer on the staff.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: Eight staff notes and a choice of tonic and scale type.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleIdentification().generate(
...     random.Random(8)
... )
>>> q.staff[0][0].name == q.staff[-1][
...     0
... ].name and not q.caption
True
```

## ScaleConstruction

```python
class ScaleConstruction(Exercise)
```

Place the notes of a named scale on a blank staff, one after
another.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleConstruction().generate(
...     random.Random(5)
... )
>>> (
...     len(q.construct_scale or []),
...     q.choices,
...     q.key,
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleConstruction().settings_signature().startswith(
...     "["
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleConstruction().generate(
...     random.Random(1)
... )
>>> scale = q.construct_scale or []
>>> scale[0].name == scale[
...     -1
... ].name and q.accidentals
True
>>> q.check_scale(scale)
True
```

## CircleOfFifths

```python
class CircleOfFifths(ChoiceExercise)
```

Questions on the circle of fifths: a relative major, a relative
minor, or the Roman numeral of a chord.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = CircleOfFifths().generate(
...     random.Random(3)
... )
>>> q.circle is not None and q.answer in q.choices
True
```

### CircleOfFifths.practice_signature

```python
def practice_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The kinds of question in force.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleOfFifths().settings_signature().startswith(
...     "["
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> "circle of fifths" in CircleOfFifths().instructions()
True
```

### CircleOfFifths.make_question

```python
def make_question(rng: random.Random) -> Question
```

Pick a kind of question that is switched on, and ask it.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: A question on the circle: `circle_kind` says which kind.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings.circle.questions = {"minor"}
>>> q = CircleOfFifths().generate(
...     random.Random(5)
... )
>>> q.circle_kind, q.prompt
('minor', 'Which minor key is the relative minor of F major?')
>>> settings.circle.questions = set(
...     settings.CIRCLE_QUESTIONS
... )
```

## ChordQualities

```python
class ChordQualities(ChoiceExercise)
```

Identify the quality of a triad or seventh chord in root position.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ChordQualities().generate(
...     random.Random(9)
... )
>>> len(q.staff[0]) in (
...     3,
...     4,
... ) and q.answer in q.choices
True
```

### ChordQualities.card_prompt

```python
def card_prompt(question: Question) -> str
```

Say what to name on a flashcard.

**Parameters**

- `question` (*Question*): The question on the card.

**Returns**

- *str*: The instruction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ChordQualities().card_prompt(
...     Question("", choices=[], answer="Major")
... )
'Identify the Chord Quality.'
```

### ChordQualities.instructions

```python
def instructions() -> str
```

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "root position" in ChordQualities().instructions()
True
```

### ChordQualities.make_question

```python
def make_question(rng: random.Random) -> Question
```

Make a chord in root position whose quality is to be named.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The chord drawn as one stack of notes, with its type (such as 'minor 7th') as the answer.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ChordQualities().generate(
...     random.Random(10)
... )
>>> q.answer in CHORDS
True
```

## ArpeggioNames

```python
class ArpeggioNames(ChoiceExercise)
```

Name the type and the inversion of a broken chord.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ArpeggioNames().generate(
...     random.Random(11)
... )
>>> q.octaves is not None and len(q.staff) >= 4
True
```

### ArpeggioNames.practice_signature

```python
def practice_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, chord types, inversions and key signatures in force.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioNames().settings_signature().startswith(
...     "["
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> "inversion" in ArpeggioNames().instructions()
True
```

### ArpeggioNames.make_question

```python
def make_question(rng: random.Random) -> Question
```

Make an arpeggio on one of the chosen clefs, in a chosen
position.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The arpeggio's notes one after another on a staff; the answer is the chord type and inversion, such as 'major · 1st inversion'.

**Raises**

- *RuntimeError*: If no arpeggio fits the chosen clefs, chord types and inversions.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ArpeggioNames().generate(
...     random.Random(12)
... )
>>> " · " in q.answer
True
```

## KeyboardNotes

```python
class KeyboardNotes(ChoiceExercise)
```

Name the highlighted key on a piano keyboard.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeyboardNotes().generate(
...     random.Random(13)
... )
>>> q.keyboard is not None and q.answer in q.choices
True
```

### KeyboardNotes.card_prompt

```python
def card_prompt(question: Question) -> str
```

Say what to name on a flashcard. Letter names give the octave if
it counts, and follow the key signature if one is shown.

**Parameters**

- `question` (*Question*): The question on the card.

**Returns**

- *str*: The instruction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardNotes().card_prompt(
...     Question(
...         "",
...         choices=[],
...         answer="C4",
...         octaves=["C4"],
...     )
... )
'Identify the note by letter and octave.'
```

### KeyboardNotes.practice_signature

```python
def practice_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The keyboard range, black keys, octave and key signature settings, and the naming in force.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardNotes().settings_signature().startswith(
...     "["
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> "highlighted" in KeyboardNotes().instructions()
True
```

### KeyboardNotes.make_question

```python
def make_question(rng: random.Random) -> Question
```

Make a keyboard with one key highlighted.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: The keyboard, a grid of name buttons (and a row of octave buttons if octaves are asked), and the key's name as the answer, with the other spelling of a black key accepted.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeyboardNotes().generate(
...     random.Random(14)
... )
>>> # noinspection PyUnresolvedReferences
>>> q.keyboard_range[
...     0
... ] <= q.keyboard.midi <= q.keyboard_range[1]
True
```

## NoteConstruction

```python
class NoteConstruction(Exercise)
```

Place a named note on the staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NoteConstruction().generate(
...     random.Random(15)
... )
>>> q.construct is not None and q.prompt.startswith(
...     "Place "
... )
True
```

### NoteConstruction.card_prompt

```python
def card_prompt(question: Question) -> str
```

Say which note to place, whichever way the on-screen prompt
words it.

**Parameters**

- `question` (*Question*): The question on the card.

**Returns**

- *str*: The instruction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstruction().card_prompt(
...     Question(
...         "Place F♯4 on the staff.",
...         choices=[],
...         answer="F♯4",
...     )
... )
'Place F♯4 on the staff.'
>>> NoteConstruction().card_prompt(
...     Question("", choices=[], answer="B♭3")
... )
'Place B♭3 on the staff.'
```

### NoteConstruction.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs, accidentals and key signature settings, and the naming in force.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstruction().settings_signature().startswith(
...     "["
... )
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

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NoteConstruction().generate(
...     random.Random(16)
... )
>>> q.answer in q.prompt
True
```

### NoteConstruction.card_count

```python
def card_count() -> int
```

Count distinct construction cards without rendering them.

**Returns**

- *int*: Number of eligible written placements under the current settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstruction().card_count() > 0
True
```

### NoteConstruction.daily_candidates

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

Visit all eligible placements in a randomized order.

**Parameters**

- `rng` (*random.Random*): Source for the order of the signatures and placements.

**Yields**

- *Question*: One playable placement for each combination.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> next(
...     NoteConstruction().daily_candidates(
...         random.Random(5)
...     )
... ).construct is not None
True
```

### NoteConstruction.review_question

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

Determine whether an introduced placement belongs to the current
construction catalog.

**Parameters**

- `question` (*Question*): Stored construction card.
- `same_settings` (*bool*): Whether its original settings are still active.

**Returns**

- *Question or None*: The playable card if its placement and prompt remain eligible.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NoteConstruction()
>>> q = ex.generate(random.Random(3))
>>> ex.review_question(
...     q, same_settings=True
... ) == q
True
```

## ClefBasics

```python
class ClefBasics(ChoiceExercise)
```

Put a named clef on a blank staff: choose the G, C or F symbol and
put it on the line that makes the clef asked for.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ClefBasics().generate(random.Random(1))
>>> (
...     q.answer == q.place_clef
...     and q.place_clef in settings.CLEF_BASICS_CLEFS
... )
True
```

### ClefBasics.settings_signature

```python
def settings_signature() -> str
```

Use button preferences for reviews only when the learner answers
with buttons.

**Returns**

- *str*: The signature for the active question type.

**Examples**

```text
Changing Button count leaves staff-placement reviews available.
```

### ClefBasics.practice_signature

```python
def practice_signature() -> str
```

Return what identifies the settings that shape these questions.

**Returns**

- *str*: The clefs asked for.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasics().settings_signature().startswith(
...     "["
... )
True
```

### ClefBasics.instructions

```python
def instructions() -> str
```

Return the help text for the exercise, for the kind of question
that is being asked.

**Returns**

- *str*: Simple HTML.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Clef Basics" in ClefBasics().instructions()
True
```

### ClefBasics.make_question

```python
def make_question(rng: random.Random) -> Question
```

Name a clef to place, or draw a clef to name.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Question*: For construction, a blank staff and the name of the clef, which is the question written under the staff. For identification, a staff with the clef drawn on it, and a button for each clef that can be asked for.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ClefBasics().generate(random.Random(3))
>>> q.prompt.startswith(
...     "Place the "
... ) and q.caption == q.prompt
True
>>> settings.clef_basics.question_type = (
...     "identification"
... )
>>> q = ClefBasics().generate(random.Random(3))
>>> (
...     q.answer in q.choices,
...     q.place_clef,
...     q.caption,
... )
(True, '', 'Which clef is this?')
>>> settings.clef_basics.question_type = (
...     "construction"
... )
```

## NotationIdentification

```python
class NotationIdentification(ChoiceExercise)
```

Identify the highlighted part of a written phrase.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NotationIdentification().generate(
...     random.Random(2)
... )
>>> bool(
...     q.staff or q.notation_excerpt
... ) and q.answer in q.choices
True
```

### NotationIdentification.settings_signature

```python
def settings_signature() -> str
```

Use button preferences for reviews only when the learner answers
with buttons.

**Returns**

- *str*: The signature for the active question type.

**Examples**

```text
Changing Button count leaves staff-placement reviews available.
```

### NotationIdentification.practice_signature

```python
def practice_signature() -> str
```

Identify the terms eligible for review.

**Returns**

- *str*: The selected terms, or the original empty signature when all terms are enabled.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NotationIdentification().settings_signature()
''
```

### NotationIdentification.instructions

```python
def instructions() -> str
```

Explain how to answer the notation question.

**Returns**

- *str*: Help for mouse and keyboard users.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "number" in NotationIdentification().instructions()
True
```

### NotationIdentification.refresh

```python
def refresh(question: Question) -> Question
```

Replace unchecked distractors in older practice questions before
replay.

**Parameters**

- `question` (*Question*): Stored question matching the current settings signature.

**Returns**

- *Question*: The original notation with eligible answer buttons.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NotationIdentification()
>>> q = ex.generate(random.Random(1))
>>> ex.refresh(q) == q
True
```

### NotationIdentification.make_question

```python
def make_question(rng: random.Random) -> Question
```

Choose a phrase and a single visible feature to highlight.

**Parameters**

- `rng` (*random.Random*): Source for the phrase, feature, and its position.

**Returns**

- *Question*: A short phrase with the selected marking and checked answer choices.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NotationIdentification().generate(
...     random.Random(0)
... )
>>> q.notation_target[0] == q.answer
True
```

### NotationIdentification.card_groups

```python
def card_groups() -> dict[str, str]
```

Group the active question type’s playable examples by the symbol
being practiced.

**Returns**

- *dict of str to str*: Map from each eligible example’s item key to its selected term.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bool(NotationIdentification().card_groups())
True
```

### NotationIdentification.daily_candidates

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

Choose one example for each selected notation term.

**Parameters**

- `rng` (*random.Random*): Randomizes term order, examples and distractors.

**Yields**

- *Question*: A distinct playable card with the current answer controls.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> next(
...     NotationIdentification().daily_candidates(
...         random.Random(4)
...     )
... ).answer in settings.notation.terms
True
```

### NotationIdentification.review_question

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

Recover an eligible saved example under the current term and
button selections.

**Parameters**

- `question` (*Question*): Saved question.
- `same_settings` (*bool*): Whether the presentation settings still match.

**Returns**

- *Question or None*: The current presentation of the card, or None if its term or example is outside the catalog.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NotationIdentification()
>>> q = ex.generate(random.Random(4))
>>> ex.review_question(
...     q, same_settings=True
... ) == q
True
```

## RythmicEquations

```python
class RythmicEquations(ChoiceExercise)
```

Complete arithmetic equations with written note values.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = RythmicEquations().generate(
...     random.Random(2)
... )
>>> "_" in q.prompt and q.answer in q.choices
True
```

### RythmicEquations.instructions

```python
def instructions() -> str
```

Explain how to complete the equation with a button or its
shortcut.

**Returns**

- *str*: Instructions for the exercise.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "keys" in RythmicEquations().instructions()
True
```

### RythmicEquations.card_prompt

```python
def card_prompt(question: Question) -> str
```

Ask for the missing note or rest on an exported card.

**Parameters**

- `question` (*Question*): The equation on the card.

**Returns**

- *str*: The instruction shown above the equation.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RythmicEquations().card_prompt(
...     Question("", choices=[], answer="")
... )
'Which note or rest balances the equation?'
```

### RythmicEquations.practice_signature

```python
def practice_signature() -> str
```

Keep review questions tied to the options that generated them.

**Returns**

- *str*: The selected operators and symbols, or an empty string for the original defaults.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RythmicEquations().practice_signature()
''
```

### RythmicEquations.make_question

```python
def make_question(rng: random.Random) -> Question
```

Write a rhythm equation and hide one of its note values.

**Parameters**

- `rng` (*random.Random*): Chooses the note value, operation, and blank position.

**Returns**

- *Question*: The equation and the note values available as answers.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RythmicEquations().make_question(
...     random.Random(0)
... ).prompt.count("_")
1
```
{% endraw %}
