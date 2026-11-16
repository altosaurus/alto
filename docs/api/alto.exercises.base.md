---
title: alto.exercises.base
parent: api
package: alto.exercises
order: 8
permalink: /api/alto.exercises.base/
---
{% raw %}
Exercise framework. To add an exercise: subclass Exercise, decorate with @register.

An `Exercise` makes `Question` objects. The `Question` says what to show (a staff, a keyboard or only text), which
buttons to offer and which answer is right. The exercise screen and the scheduler work with those two classes only, so
a new exercise needs no new interface code.

**Examples**

```pycon
>>> question = Question("Name this note.", choices=["C", "D", "E"], answer="D")
>>> question.check("D"), question.check("E")
(True, False)
```

## Question

```python
Question(
    prompt: str,
    *,
    choices: list[str],
    answer: str,
    staff: list[list[Note]] = field(default_factory=list),
    clef: str = 'treble',
    explanation: str = '',
    key: int = 0,
    value: str = 'whole',
    grid: dict[str, tuple[int, int]] | None = None,
    keyboard: Note | None = None,
    key_staff: bool = False,
    keyboard_range: tuple[int, int] | None = None,
    octaves: list[str] | None = None,
    second_label: str = 'Octave',
    joiner: str = '',
    construct: Note | None = None,
    accidentals: bool = False,
    accept: tuple[str, ...] = (),
    show_staff: bool = False,
    caption: str = '',
    build_key: bool = False,
    construct_scale: list[Note] | None = None,
    construct_steps: list[str] | None = None,
    exact_octave: bool = False,
    circle: int | None = None,
    circle_kind: str = '',
    circle_ring: str = 'outer',
    circle_key: int | None = None,
    required: tuple[str, ...] = (),
    place_clef: str = '',
)
```

One question, with what to show for it and which answer is right.

**Attributes**

- `prompt` (*str*): The text shown above the question; may be empty.
- `choices` (*list of str*): The answer buttons, in the order they should be offered. Keyword-only.
- `answer` (*str*): The right answer, one of `choices` (or the note name for a "place this note" question). Keyword-only.
- `staff` (*list of list of Note*): What to draw on the staff: each inner list is one chord or note. Keyword-only.
- `clef` (*str, default "treble"*): The clef to draw on. Keyword-only.
- `explanation` (*str, default ""*): Text shown after the answer to say why it is right. Keyword-only.
- `key` (*int, default 0*): The key signature to draw: that many sharps if positive, flats if negative. Keyword-only.
- `value` (*str, default "whole"*): The note value to draw (single notes only). Keyword-only.
- `grid` (*dict of str to tuple of (int, int) or None*): Where to put each answer button, as (row, column). Without it the choices form one row. Keyword-only.
- `keyboard` (*Note or None*): A piano key to highlight, instead of drawing a staff. Keyword-only.
- `key_staff` (*bool, default False*): Draw `key` as a small key-signature staff above the keyboard. Keyword-only.
- `keyboard_range` (*tuple of (int, int) or None*): The keys (MIDI numbers, inclusive) the keyboard picture should show. Keyword-only.
- `octaves` (*list of str or None*): When set, the answer is a choice button plus one of these second-row buttons. Keyword-only.
- `second_label` (*str, default "Octave"*): What the second row of buttons is called. Keyword-only.
- `joiner` (*str, default ""*): Put between the two parts to make the answer ("" for a note and its octave: C + 4 gives C4). Keyword-only.
- `construct` (*Note or None*): The note to place on the staff: the answer is a position, not a button. Keyword-only.
- `accidentals` (*bool, default False*): Show the sharp, natural and flat buttons for a construct question. Keyword-only.
- `accept` (*tuple of str*): Other answers that count as right, such as the enharmonic name of a black key. Keyword-only.
- `show_staff` (*bool, default False*): Draw the staff even with no notes on it, to show only its clef and key signature. Keyword-only.
- `caption` (*str, default ""*): Text written on the staff itself, under the music, in place of the prompt above it. Keyword-only.
- `build_key` (*bool, default False*): The learner builds the key signature `key` on a blank staff with the fork widget, instead of pressing a button. Keyword-only.
- `construct_scale` (*list of Note or None*): The notes of a scale to place on the staff one after another, left to right: the answer is the whole row. Keyword-only.
- `construct_steps` (*list of str or None*): The steps between the notes of `construct_scale`, each "W" (whole) or "H" (half), to mark once the notes are placed; None if the steps are not asked. Keyword-only.
- `exact_octave` (*bool, default False*): The scale has to be placed in the octave asked, not in any octave. Keyword-only.
- `circle` (*int or None*): A question on the circle of fifths: the place asked about, clockwise from C at 0. Keyword-only.
- `circle_kind` (*str, default ""*): What the circle asks: "major" (the relative major of a minor key), "minor" (the relative minor of a major key) or "numeral" (the Roman numeral of a chord of a key). Keyword-only.
- `circle_ring` (*str, default "outer"*): Which ring the cell asked about is in: "outer" for the major keys or "inner" for the minor ones. Keyword-only.
- `circle_key` (*int or None*): For a Roman numeral question, the place of the key whose chords they are. Keyword-only.
- `required` (*tuple of str*): Answers that must all be given, one after another in any order, such as both names of a key with two: B and C♭. Empty for an ordinary question with one answer. Keyword-only.
- `place_clef` (*str, default ""*): The clef to put on a blank staff: the answer is a clef symbol (G, C or F) and a place on the staff, not a button. Empty for any other question. Keyword-only.

**Examples**

```pycon
>>> q = Question("Which note is this?", choices=["C", "D", "E"], answer="D", staff=[[Note.parse("D4")]])
>>> q.check("D")
True
>>> Question.from_dict(q.to_dict()) == q  # a question can be stored and asked again
True
```

### Question.check_placed

```python
def check_placed(note: Note) -> bool
```

Report whether a note placed on the staff is the one asked for.

The spelling and octave must match exactly, so G♯4 is not A♭4.

**Parameters**

- `note` (*Note*): The note the learner placed.

**Returns**

- *bool*: True if it equals the note in `construct`.

**Examples**

```pycon
>>> q = Question("Place C4", choices=[], answer="C4", construct=Note.parse("C4"))
>>> q.check_placed(Note.parse("C4"))
True
>>> q.check_placed(Note.parse("B#3"))  # sounds the same, but is spelled differently
False
```

### Question.check_scale

```python
def check_scale(notes: list[Note]) -> bool
```

Report whether the notes placed on the staff are the scale asked for.

The spelling and the order of the notes must match, so a G♯ is not an A♭. Unless `exact_octave` is set the octave
does not matter, as long as the whole scale is in the same one: the same scale an octave higher or lower is right,
but a scale with one note in the wrong octave is not. With `exact_octave` the scale has to be in the octave asked.

**Parameters**

- `notes` (*list of Note*): The notes the learner placed, left to right.

**Returns**

- *bool*: True if they are the notes of `construct_scale`, all moved by the same whole number of octaves (or, with `exact_octave`, not moved at all).

**Examples**

```pycon
>>> asked = [Note.parse("C4"), Note.parse("D4")]
>>> q = Question("Place C D.", choices=[], answer="C4 D4", construct_scale=asked)
>>> q.check_scale([Note.parse("C4"), Note.parse("D4")])
True
>>> q.check_scale([Note.parse("C5"), Note.parse("D5")])  # the same scale, an octave higher
True
>>> q.check_scale([Note.parse("C4"), Note.parse("D5")])  # one note in another octave
False
>>> q.check_scale([Note.parse("C4"), Note.parse("D4"), Note.parse("E4")])
False
>>> exact = Question("Place C D.", choices=[], answer="C4 D4", construct_scale=asked, exact_octave=True)
>>> exact.check_scale([Note.parse("C4"), Note.parse("D4")]), exact.check_scale([Note.parse("C5"), Note.parse("D5")])
(True, False)
```

### Question.check_steps

```python
def check_steps(steps: list[str]) -> bool
```

Report whether the steps marked between the notes of a scale are the right ones.

**Parameters**

- `steps` (*list of str*): The steps the learner marked, left to right, each "W" or "H".

**Returns**

- *bool*: True if the steps are not asked, or if they are those of `construct_steps`.

**Examples**

```pycon
>>> q = Question("Mark the steps.", choices=[], answer="W H", construct_steps=["W", "H"])
>>> q.check_steps(["W", "H"]), q.check_steps(["H", "W"]), q.check_steps(["W"])
(True, False, False)
>>> Question("No steps.", choices=[], answer="").check_steps([])
True
```

### Question.check_built

```python
def check_built(count: int) -> bool
```

Report whether a key signature built with the fork is the one asked for.

**Parameters**

- `count` (*int*): The signature the learner built: that many sharps if positive, flats if negative.

**Returns**

- *bool*: True if it equals `key`.

**Examples**

```pycon
>>> q = Question("Build D major.", choices=[], answer="2 sharps", key=2, show_staff=True, build_key=True)
>>> q.check_built(2), q.check_built(-2)
(True, False)
```

### Question.check

```python
def check(choice: str) -> bool
```

Report whether a chosen answer is right.

**Parameters**

- `choice` (*str*): The text of the button that was pressed.

**Returns**

- *bool*: True if it is the answer or one of the other accepted answers.

**Examples**

```pycon
>>> q = Question("", choices=["F♯", "G♭"], answer="F♯", accept=("G♭",))
>>> q.check("F♯"), q.check("G♭"), q.check("A")
(True, True, False)
>>> both = Question("", choices=["B", "C♭", "D"], answer="B", required=("B", "C♭"))
>>> both.check("B"), both.check("C♭"), both.check("D")  # each is right, but both are needed: see `complete`
(True, True, False)
```

### Question.complete

```python
def complete(given: set[str]) -> bool
```

Report whether the answers given so far are all of those needed.

**Parameters**

- `given` (*set of str*): The right answers given so far.

**Returns**

- *bool*: For an ordinary question, whether the answer has been given; for one with several `required`, whether all have.

**Examples**

```pycon
>>> both = Question("", choices=["B", "C♭"], answer="B", required=("B", "C♭"))
>>> both.complete({"B"}), both.complete({"C♭", "B"})
(False, True)
>>> Question("", choices=["C"], answer="C").complete({"C"})
True
```

### Question.item_key

```python
def item_key() -> str
```

Return a stable identity for the question, so the same one can be recognised when it comes round again.

It covers what is asked and where it is drawn, but not the note value or the order of the buttons.

**Returns**

- *str*: A 20-character hexadecimal string.

**Examples**

```pycon
>>> a = Question("Name it.", choices=["C", "D"], answer="C")
>>> b = Question("Name it.", choices=["D", "C"], answer="C")  # the same question, buttons in another order
>>> a.item_key() == b.item_key()
True
>>> len(a.item_key())
20
```

### Question.to_dict

```python
def to_dict() -> dict
```

Return the question as plain data, so it can be stored and asked again.

**Returns**

- *dict*: The fields of the question, with notes as dictionaries and tuples as lists.

**Examples**

```pycon
>>> data = Question("Name it.", choices=["C"], answer="C", staff=[[Note.parse("C4")]]).to_dict()
>>> data["answer"], data["staff"]
('C', [[{'octave': 4, 'letter': 0, 'accidental': 0}]])
```

### Question.from_dict

```python
@classmethod
def from_dict(d: dict) -> Question
```

Rebuild a question from the data that `to_dict` made.

**Parameters**

- `d` (*dict*): The stored data. Questions saved by older versions, which may carry a `play` field, are accepted.

**Returns**

- *Question*: The question.

**Examples**

```pycon
>>> q = Question("Name it.", choices=["C", "D"], answer="C", key=2, accept=("D",))
>>> Question.from_dict(q.to_dict()) == q
True
```

## note_from

```python
def note_from(v: dict | None) -> Note | None
```

Rebuild a note from stored data.

**Parameters**

- `v` (*dict or None*): A note as the dictionary `to_dict` stores, or None.

**Returns**

- *Note or None*: The note, or None if `v` was None.

**Examples**

```pycon
>>> note_from({"octave": 4, "letter": 0, "accidental": 0})
Note(octave=4, letter=0, accidental=0)
>>> note_from(None) is None
True
```

## signature

```python
def signature(*parts: object) -> str
```

Describe the exercise settings in force, so a stored question is only asked again under the settings it was made for.

**Parameters**

- `*parts` (*object*): The settings to describe: dataclasses, dictionaries, lists, sets and plain values, nested as needed.

**Returns**

- *str*: A JSON string that is the same for equal settings, however their sets and dictionaries happen to be ordered.

**Examples**

```pycon
>>> signature({"clefs": {"bass", "treble"}}, 3)
'[{"clefs": ["bass", "treble"]}, 3]'
>>> signature({"clefs": {"treble", "bass"}}, 3) == signature({"clefs": {"bass", "treble"}}, 3)
True
```

## Exercise

```python
class Exercise(ABC)
```

What every exercise provides: its name, how it makes questions and how long a good answer takes.

**Attributes**

- `name` (*str*): The title shown on the home screen and in the exercise list.
- `category` (*str*): The heading it is listed under.
- `description` (*str*): One line saying what the exercise is for.
- `par_seconds` (*float, default 5.0*): How long a good first answer takes; much quicker earns credit and much slower counts against the question.
- `has_sound` (*bool, default True*): False for an exercise that makes no sound at all, whatever the sound button says.

**Examples**

```pycon
>>> class Demo(Exercise):
...     name = "Demo"
...     def generate(self, rng):
...         return Question("Pick A.", choices=["A", "B"], answer="A")
>>> Demo().generate(random.Random(0)).answer
'A'
```

### Exercise.settings_signature

```python
def settings_signature() -> str
```

Return what identifies the settings that shape the questions.

A stored question is only asked again while this is unchanged. Exercises with settings override it.

**Returns**

- *str*: An identifier; empty for an exercise with no settings.

**Examples**

```pycon
>>> class Demo(Exercise):
...     def generate(self, rng):
...         return Question("?", choices=["A"], answer="A")
>>> Demo().settings_signature()
''
```

### Exercise.refresh

```python
def refresh(question: Question) -> Question
```

Bring a stored question up to date with how the exercise draws its questions now.

A question that is asked again comes from the copy stored when it was first asked, which an older version may
have drawn differently. The default leaves it as it is.

**Parameters**

- `question` (*Question*): The question as it was stored.

**Returns**

- *Question*: The question as the exercise would draw it today.

**Examples**

```pycon
>>> class Demo(Exercise):
...     def generate(self, rng):
...         return Question("?", choices=["A"], answer="A")
>>> q = Question("?", choices=["A"], answer="A")
>>> Demo().refresh(q) is q
True
```

### Exercise.instructions

```python
def instructions() -> str
```

Return the help text shown from the exercise's help button.

Exercises override it to describe themselves.

**Returns**

- *str*: Simple HTML; by default the one-line description.

**Examples**

```pycon
>>> class Demo(Exercise):
...     description = "Spot the note."
...     def generate(self, rng):
...         return Question("?", choices=["A"], answer="A")
>>> Demo().instructions()
'Spot the note.'
```

### Exercise.generate

```python
@abstractmethod
def generate(rng: random.Random) -> Question
```

Make one new question.

**Parameters**

- `rng` (*random.Random*): The random number generator to use, so tests can ask for a repeatable question.

**Returns**

- *Question*: The question.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> q = NoteNames().generate(random.Random(1))
>>> q.answer in q.choices
True
```

## register

```python
def register() -> type[Exercise]
```

Add an exercise to `REGISTRY`, next to the others of its category.

The categories come in the order they first appear, so the home screen and the exercise list can show each category
once, with all its exercises under it. Used as a class decorator.

**Parameters**

- `cls` (*type of Exercise*): The exercise class.

**Returns**

- *type of Exercise*: The same class, so the decorator can be applied to a class definition.

**Examples**

```pycon
>>> @register
... class Demo(Exercise):
...     name = "Demo"
...     category = "A category no other exercise has"
...     def generate(self, rng):
...         return Question("?", choices=["A"], answer="A")
>>> REGISTRY[-1] is Demo
True
>>> REGISTRY.remove(Demo)
```

## pick_distractors

```python
def pick_distractors(
    correct: str,
    *,
    pool: list[str],
    n: int,
    rng: random.Random,
) -> list[str]
```

Choose wrong answers to offer alongside the right one, and shuffle them all.

**Parameters**

- `correct` (*str*): The right answer. It is always in the result.
- `pool` (*list of str*): Where the wrong answers come from; repeats and the right answer are ignored. Keyword-only.
- `n` (*int*): How many wrong answers to include (fewer if the pool has fewer). Keyword-only.
- `rng` (*random.Random*): The random number generator used to choose and shuffle. Keyword-only.

**Returns**

- *list of str*: The right answer and up to `n` others, in a random order.

**Examples**

```pycon
>>> choices_ = pick_distractors("C", pool=["C", "D", "E", "F"], n=2, rng=random.Random(0))
>>> len(choices_), "C" in choices_
(3, True)
```
{% endraw %}
