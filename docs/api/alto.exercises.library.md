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

<div class="api-signature" markdown="1">

```python
NoteNames(accidentals: bool = False)
```

{% endraw %}{% include api-source.html name="NoteNames" line=251 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="NoteNames.card_prompt" line=267 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="NoteNames.practice_signature" line=291 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="NoteNames.instructions" line=314 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="NoteNames.make_question" line=369 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_count() -> int
```

{% endraw %}{% include api-source.html name="NoteNames.card_count" line=422 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="NoteNames.daily_candidates" line=451 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

{% endraw %}{% include api-source.html name="NoteNames.review_question" line=505 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class IntervalNames(Exercise)
```

{% endraw %}{% include api-source.html name="IntervalNames" line=776 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="IntervalNames.card_prompt" line=798 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="IntervalNames.instructions" line=836 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="IntervalNames.settings_signature" line=877 %}{% raw %}

</div>

Identify the settings used to generate and grade the interval.

**Returns**

- *str*: The stored-question review signature.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Harmonic" in IntervalNames().settings_signature()
True
```

### IntervalNames.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="IntervalNames.refresh" line=933 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="IntervalNames.generate" line=977 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class IntervalConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="IntervalConstruction" line=1281 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="IntervalConstruction.instructions" line=1305 %}{% raw %}

</div>

Explain staff placement and spelling for interval construction.

**Returns**

- *str*: Instructions for mouse and keyboard input.

**Examples**

```text
The reference describes the difference between melodic and
harmonic placement.
```

### IntervalConstruction.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="IntervalConstruction.settings_signature" line=1330 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="IntervalConstruction.generate" line=1349 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class KeyboardIntervals(Exercise)
```

{% endraw %}{% include api-source.html name="KeyboardIntervals" line=1376 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.card_prompt" line=1405 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.settings_signature" line=1429 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.instructions" line=1448 %}{% raw %}

</div>

Explain how to identify an interval from two highlighted keys.

**Returns**

- *str*: HTML explaining interval names and enharmonic ambiguity on the keyboard.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "A4 / d5" in KeyboardIntervals().instructions()
True
```

### KeyboardIntervals.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.generate" line=1482 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class KeySignatures(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="KeySignatures" line=1631 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="KeySignatures.practice_signature" line=1651 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeySignatures.instructions" line=1670 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="KeySignatures.refresh" line=1703 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeySignatures.make_question" line=1765 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class KeySignatureConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction" line=1899 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction.settings_signature" line=1919 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction.instructions" line=1937 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction.generate" line=1972 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class OrderOfKeys(Exercise)
```

{% endraw %}{% include api-source.html name="OrderOfKeys" line=2030 %}{% raw %}

</div>

Write the accidentals of a named key signature in order.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeys().generate(
...     random.Random(1)
... ).place_signature
True
```

### OrderOfKeys.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="OrderOfKeys.settings_signature" line=2048 %}{% raw %}

</div>

Identify the selections used to generate a practice question.

**Returns**

- *str*: The original empty signature at the defaults, so earlier questions remain available for review.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeys().settings_signature()
''
```

### OrderOfKeys.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="OrderOfKeys.instructions" line=2077 %}{% raw %}

</div>

Explain how to enter and submit a signature.

**Returns**

- *str*: The exercise help text.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Undo" in OrderOfKeys().instructions()
True
```

### OrderOfKeys.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="OrderOfKeys.generate" line=2103 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class ScaleIdentification(Exercise)
```

{% endraw %}{% include api-source.html name="ScaleIdentification" line=2280 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="ScaleIdentification.settings_signature" line=2298 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ScaleIdentification.instructions" line=2331 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ScaleIdentification.generate" line=2366 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class ScaleConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="ScaleConstruction" line=2460 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="ScaleConstruction.settings_signature" line=2483 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ScaleConstruction.instructions" line=2509 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Scale Construction" in ScaleConstruction().instructions()
True
```

### ScaleConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ScaleConstruction.generate" line=2600 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class CircleOfFifths(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="CircleOfFifths" line=2768 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="CircleOfFifths.practice_signature" line=2790 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="CircleOfFifths.instructions" line=2808 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML, with a paragraph for each kind of question that is switched on.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "circle of fifths" in CircleOfFifths().instructions()
True
```

### CircleOfFifths.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="CircleOfFifths.make_question" line=2873 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class ChordQualities(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="ChordQualities" line=3068 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="ChordQualities.card_prompt" line=3090 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ChordQualities.instructions" line=3114 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "root position" in ChordQualities().instructions()
True
```

### ChordQualities.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ChordQualities.make_question" line=3136 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class ArpeggioNames(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="ArpeggioNames" line=3197 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="ArpeggioNames.practice_signature" line=3215 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ArpeggioNames.instructions" line=3234 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "inversion" in ArpeggioNames().instructions()
True
```

### ArpeggioNames.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ArpeggioNames.make_question" line=3264 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class KeyboardNotes(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="KeyboardNotes" line=3586 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="KeyboardNotes.card_prompt" line=3604 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="KeyboardNotes.practice_signature" line=3643 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeyboardNotes.instructions" line=3665 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML, with paragraphs added for the octave and key signature settings that are on.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "highlighted" in KeyboardNotes().instructions()
True
```

### KeyboardNotes.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeyboardNotes.make_question" line=3727 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class NoteConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="NoteConstruction" line=3898 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="NoteConstruction.card_prompt" line=3918 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="NoteConstruction.settings_signature" line=3957 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="NoteConstruction.instructions" line=4006 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

- *str*: Simple HTML, with paragraphs added for the key signature and accidental settings that are on.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Click the staff" in NoteConstruction().instructions()
True
```

### NoteConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="NoteConstruction.generate" line=4076 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_count() -> int
```

{% endraw %}{% include api-source.html name="NoteConstruction.card_count" line=4261 %}{% raw %}

</div>

Count distinct construction cards without rendering them.

**Returns**

- *int*: Number of eligible written placements under the current settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstruction().card_count() > 0
True
```

### NoteConstruction.daily_candidates

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="NoteConstruction.daily_candidates" line=4280 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

{% endraw %}{% include api-source.html name="NoteConstruction.review_question" line=4343 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class ClefBasics(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="ClefBasics" line=4580 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="ClefBasics.settings_signature" line=4601 %}{% raw %}

</div>

Use button preferences for reviews only when the learner answers
with buttons.

**Returns**

- *str*: The signature for the active question type.

**Examples**

```text
Changing Button count leaves staff-placement reviews available.
```

### ClefBasics.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="ClefBasics.practice_signature" line=4621 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ClefBasics.instructions" line=4639 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ClefBasics.make_question" line=4689 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
class NotationIdentification(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="NotationIdentification" line=4761 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="NotationIdentification.settings_signature" line=4786 %}{% raw %}

</div>

Use button preferences for reviews only when the learner answers
with buttons.

**Returns**

- *str*: The signature for the active question type.

**Examples**

```text
Changing Button count leaves staff-placement reviews available.
```

### NotationIdentification.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="NotationIdentification.practice_signature" line=4806 %}{% raw %}

</div>

Identify the terms eligible for review.

**Returns**

- *str*: The selected terms, or the original empty signature when all terms are enabled.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NotationIdentification().settings_signature()
''
```

### NotationIdentification.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="NotationIdentification.instructions" line=4829 %}{% raw %}

</div>

Explain how to answer the notation question.

**Returns**

- *str*: Help for mouse and keyboard users.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "number" in NotationIdentification().instructions()
True
```

### NotationIdentification.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="NotationIdentification.refresh" line=4924 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="NotationIdentification.make_question" line=4953 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_groups() -> dict[str, str]
```

{% endraw %}{% include api-source.html name="NotationIdentification.card_groups" line=5236 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="NotationIdentification.daily_candidates" line=5258 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

{% endraw %}{% include api-source.html name="NotationIdentification.review_question" line=5329 %}{% raw %}

</div>

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

## beat_meter

<div class="api-signature" markdown="1">

```python
def beat_meter(answer: str) -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="beat_meter" line=5406 %}{% raw %}

</div>

Look up the written time signature for either kind of answer.

**Parameters**

- `answer` (*str*): A time signature or meter classification from the exercise.

**Returns**

- *tuple of int*: Numerator and denominator for engraving the rhythm.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> beat_meter("Compound duple")
(6, 8)
```

## BeatIdentification

<div class="api-signature" markdown="1">

```python
class BeatIdentification(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="BeatIdentification" line=5431 %}{% raw %}

</div>

Identify the time signature or classify the meter of a rhythm.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = BeatIdentification().generate(random.Random(2))
>>> q.answer in q.choices and bool(q.rhythm)
True
```

### BeatIdentification.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="BeatIdentification.practice_signature" line=5447 %}{% raw %}

</div>

Keep separate review settings for the two rhythm components.

**Returns**

- *str*: The original empty signature for time signature practice, or the selected component for classification practice.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatIdentification().practice_signature()
''
```

### BeatIdentification.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="BeatIdentification.instructions" line=5471 %}{% raw %}

</div>

Explain how to answer from the two written measures.

**Returns**

- *str*: The task and its keyboard shortcut directions.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "keys" in BeatIdentification().instructions()
True
```

### BeatIdentification.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="BeatIdentification.make_question" line=5505 %}{% raw %}

</div>

Generate two complete measures in a randomly chosen meter.

**Parameters**

- `rng` (*random.Random*): Chooses the time signature and how each beat is written.

**Returns**

- *Question*: The rhythm and the answers for the selected component.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = BeatIdentification().make_question(random.Random(0))
>>> q.prompt
'What is the time signature?'
```

## beat_positions

<div class="api-signature" markdown="1">

```python
def beat_positions(meter: tuple[int, int]) -> frozenset[int]
```

{% endraw %}{% include api-source.html name="beat_positions" line=5841 %}{% raw %}

</div>

Get the main beat starts in two measures, measured in eighth notes.

**Parameters**

- `meter` (*tuple of int*): One of the supported time signatures.

**Returns**

- *frozenset of int*: Zero-based positions from the start of the first measure.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sorted(beat_positions((6, 8)))
[0, 3, 6, 9]
```

## BeatConstruction

<div class="api-signature" markdown="1">

```python
class BeatConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="BeatConstruction" line=5866 %}{% raw %}

</div>

Mark where the main beats begin in two written measures.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = BeatConstruction().generate(random.Random(2))
>>> q.answer in BEAT_METERS and not q.choices
True
```

### BeatConstruction.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="BeatConstruction.settings_signature" line=5882 %}{% raw %}

</div>

Identify the note types used in a saved construction question.

**Returns**

- *str*: Empty for the original selection, otherwise its signature.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatConstruction().settings_signature()
''
```

### BeatConstruction.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="BeatConstruction.instructions" line=5903 %}{% raw %}

</div>

Explain how to place and submit the beats.

**Returns**

- *str*: Counting guidance and keyboard controls.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "arrow keys" in BeatConstruction().instructions()
True
```

### BeatConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="BeatConstruction.generate" line=5930 %}{% raw %}

</div>

Choose a time signature and write two measures to mark.

**Parameters**

- `rng` (*random.Random*): Chooses the meter and the written rhythm.

**Returns**

- *Question*: The rhythm and its time signature, without answer choices.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatConstruction().generate(random.Random(1)).prompt
'Place the beats in both measures.'
```

## RythmicEquations

<div class="api-signature" markdown="1">

```python
class RythmicEquations(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="RythmicEquations" line=5964 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="RythmicEquations.instructions" line=5986 %}{% raw %}

</div>

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

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="RythmicEquations.card_prompt" line=6007 %}{% raw %}

</div>

Ask for the missing symbol or number on an exported card.

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

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="RythmicEquations.practice_signature" line=6034 %}{% raw %}

</div>

Keep review questions tied to the options that generated them.

**Returns**

- *str*: The selected operators and symbols, or an empty string for the original defaults.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RythmicEquations().practice_signature()
''
```

### RythmicEquations.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="RythmicEquations.make_question" line=6108 %}{% raw %}

</div>

Write a rhythm equation and hide a symbol or number.

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
