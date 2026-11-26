---
title: Question
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/class-question/
---
{% raw %}
<div class="api-signature" markdown="1">

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
    staff_signature: int | None = None,
    minor: bool = False,
    value: str = 'whole',
    grid: dict[str, tuple[int, int]] | None = None,
    keyboard: Note | None = None,
    keyboard_notes: list[Note] = field(default_factory=list),
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
    place_signature: bool = False,
    starting_slots: list[int] = field(default_factory=list),
    construct_scale: list[Note] | None = None,
    construct_steps: list[str] | None = None,
    notes_only: bool = False,
    any_octave: bool = False,
    exact_octave: bool = False,
    circle: int | None = None,
    circle_kind: str = '',
    circle_ring: str = 'outer',
    circle_key: int | None = None,
    required: tuple[str, ...] = (),
    place_clef: str = '',
    picture: PicturePosition | None = None,
    fingerboard: FingerboardPosition | None = None,
    notation_target: tuple[str, int] | None = None,
    notation_excerpt: str | None = None,
    rhythm: tuple[str, ...] = (),
)
```

{% endraw %}{% include api-source.html name="Question" line=133 %}{% raw %}

</div>

One question, with what to show for it and which answer is right.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `prompt` | `str` | The text shown above the question; may be empty. |
| `choices` | `list of str` | The answer buttons, in the order they should be offered. Keyword-only. |
| `answer` | `str` | The right answer, one of `choices` (or the note name for a "place this note" question). Keyword-only. |
| `staff` | `list of list of Note` | What to draw on the staff: each inner list is one chord or note. Keyword-only. |
| `clef` | `str, default "treble"` | The clef to draw on. Keyword-only. |
| `explanation` | `str, default ""` | Text shown after the answer to say why it is right. Keyword-only. |
| `key` | `int, default 0` | The key signature to draw: that many sharps if positive, flats if negative. Keyword-only. |
| `value` | `str, default "whole"` | The written duration for single notes and interval voices. Keyword-only. |
| `staff_signature` | `int or None` | Override the signature shown on the staff while retaining the key for scale degrees. Keyword-only. |
| `minor` | `bool, default False` | Use the signature's relative minor for scale degree naming. Keyword-only. |
| `grid` | `dict of str to tuple of (int, int) or None` | Where to put each answer button, as (row, column). Without it the choices form one row. Keyword-only. |
| `picture` | `PicturePosition or None` | Pack image, marker coordinates and optional sounding pitch. Keyword-only. |
| `fingerboard` | `FingerboardPosition or None` | Tuning, string index, and marked pitch for a four-string identification question. Keyword-only. |
| `keyboard` | `Note or None` | A piano key to highlight, instead of drawing a staff. Keyword-only. |
| `keyboard_notes` | `list of Note` | Multiple piano keys to highlight together instead of drawing a staff. Keyword-only. |
| `key_staff` | `bool, default False` | Draw `key` as a small key-signature staff above the keyboard. Keyword-only. |
| `keyboard_range` | `tuple of (int, int) or None` | The keys (MIDI numbers, inclusive) the keyboard picture should show. Keyword-only. |
| `octaves` | `list of str or None` | When set, the answer is a choice button plus one of these second-row buttons. Keyword-only. |
| `second_label` | `str, default "Octave"` | What the second row of buttons is called. Keyword-only. |
| `joiner` | `str, default ""` | Put between the two parts to make the answer ("" for a note and its octave: C + 4 gives C4). Keyword-only. |
| `construct` | `Note or None` | The note to place on the staff: the answer is a position, not a button. Keyword-only. |
| `accidentals` | `bool, default False` | Show the sharp, natural and flat buttons for a construct question. Keyword-only. |
| `accept` | `tuple of str` | Other answers that count as right, such as the enharmonic name of a black key. Keyword-only. |
| `show_staff` | `bool, default False` | Draw the staff even with no notes on it, to show only its clef and key signature. Keyword-only. |
| `caption` | `str, default ""` | Text written on the staff itself, under the music, in place of the prompt above it. Keyword-only. |
| `build_key` | `bool, default False` | The learner builds the key signature `key` on a blank staff with the fork widget, instead of pressing a button. Keyword-only. |
| `place_signature` | `bool, default False` | Place each accidental of the named key on the staff. Keyword-only. |
| `starting_slots` | `list of int` | Zero-based positions of the accidentals already printed in an Order of Keys question. |
| `construct_scale` | `list of Note or None` | The notes of a scale to place on the staff one after another, left to right: the answer is the whole row. Keyword-only. |
| `construct_steps` | `list of str or None` | The steps between the notes of `construct_scale`, each "W" (whole) or "H" (half), to mark once the notes are placed; None if the steps are not asked. Keyword-only. |
| `notes_only` | `bool, default False` | Show note names without a scale degree context. Keyword-only. |
| `any_octave` | `bool, default False` | Accept a single constructed note with the right spelling in any octave. Keyword-only. |
| `exact_octave` | `bool, default False` | The scale has to be placed in the octave asked, not in any octave. Keyword-only. |
| `circle` | `int or None` | A question on the circle of fifths: the place asked about, clockwise from C at 0. Keyword-only. |
| `circle_kind` | `str, default ""` | What the circle asks: "major" (the relative major of a minor key), "minor" (the relative minor of a major key) or "numeral" (the Roman numeral of a chord of a key). Keyword-only. |
| `circle_ring` | `str, default "outer"` | Which ring the cell asked about is in: "outer" for the major keys or "inner" for the minor ones. Keyword-only. |
| `circle_key` | `int or None` | For a Roman numeral question, the place of the key whose chords they are. Keyword-only. |
| `required` | `tuple of str` | Answers that must all be given, one after another in any order, such as both names of a key with two: B and C♭. Empty for an ordinary question with one answer. Keyword-only. |
| `notation_target` | `tuple of (str, int) or None` | Notation part and zero-based note column or staff line to highlight. Keyword-only. |
| `notation_excerpt` | `str or None` | Versioned score containing the target. Its position is an index into the excerpt manifest. Keyword-only. |
| `rhythm` | `tuple of str, default ()` | Written rhythm values in reading order. Keyword-only. |
| `place_clef` | `str, default ""` | The clef to put on a blank staff: the answer is a clef symbol (G, C or F) and a place on the staff, not a button. Empty for any other question. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "Which note is this?",
...     choices=["C", "D", "E"],
...     answer="D",
...     staff=[[Note.parse("D4")]],
... )
>>> q.check("D")
True
>>> Question.from_dict(
...     q.to_dict()
... ) == q  # a question can be stored and asked again
True
```

## Question.check_placed

<div class="api-signature" markdown="1">

```python
def check_placed(note: Note) -> bool
```

{% endraw %}{% include api-source.html name="Question.check_placed" line=392 %}{% raw %}

</div>

Report whether a note placed on the staff is the one asked for.

The spelling must match exactly. The octave must also match
unless `any_octave` is set.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note` | The note the learner placed. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if it matches the requested note spelling and any required octave. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "Place C4",
...     choices=[],
...     answer="C4",
...     construct=Note.parse("C4"),
... )
>>> q.check_placed(Note.parse("C4"))
True
>>> q.check_placed(
...     Note.parse("B#3")
... )  # sounds the same, but is spelled differently
False
```

## Question.sounding_columns

<div class="api-signature" markdown="1">

```python
def sounding_columns() -> list[list[Note]]
```

{% endraw %}{% include api-source.html name="Question.sounding_columns" line=431 %}{% raw %}

</div>

Return pitches from the staff or keyboard in playback order.

**Returns**

| Type | Description |
| --- | --- |
| `list of list of Note` | Each column contains the pitches sounding together. |

**Examples**

```text
A keyboard interval plays both of its highlighted pitches.
```

## Question.placement_columns

<div class="api-signature" markdown="1">

```python
def placement_columns(note: Note | None) -> list[list[Note]]
```

{% endraw %}{% include api-source.html name="Question.placement_columns" line=450 %}{% raw %}

</div>

Return the given and placed notes grouped by onset, omitting the
answer until it is placed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note or None` | Pitch under the pointer or submitted by the learner. |

**Returns**

| Type | Description |
| --- | --- |
| `list of list of Note` | Visible notes in playback order. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "Place a major third.",
...     choices=[],
...     answer="E4",
...     staff=[
...         [Note.parse("C4"), Note.parse("E4")]
...     ],
... )
>>> q.placement_columns(None) == [
...     [Note.parse("C4")]
... ]
True
```

## Question.check_scale

<div class="api-signature" markdown="1">

```python
def check_scale(notes: list[Note]) -> bool
```

{% endraw %}{% include api-source.html name="Question.check_scale" line=487 %}{% raw %}

</div>

Report whether the notes placed on the staff are the scale asked
for.

The spelling and the order of the notes must match, so a G♯ is
not an A♭. Unless `exact_octave` is set the octave
does not matter, as long as the whole scale is in the same one:
the same scale an octave higher or lower is right,
but a scale with one note in the wrong octave is not. With
`exact_octave` the scale has to be in the octave asked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `notes` | `list of Note` | The notes the learner placed, left to right. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if they are the notes of `construct_scale`, all moved by the same whole number of octaves (or, with `exact_octave`, not moved at all). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> asked = [Note.parse("C4"), Note.parse("D4")]
>>> q = Question(
...     "Place C D.",
...     choices=[],
...     answer="C4 D4",
...     construct_scale=asked,
... )
>>> q.check_scale(
...     [Note.parse("C4"), Note.parse("D4")]
... )
True
>>> q.check_scale(
...     [Note.parse("C5"), Note.parse("D5")]
... )  # the same scale, an octave higher
True
>>> q.check_scale(
...     [Note.parse("C4"), Note.parse("D5")]
... )  # one note in another octave
False
>>> q.check_scale(
...     [
...         Note.parse("C4"),
...         Note.parse("D4"),
...         Note.parse("E4"),
...     ]
... )
False
>>> exact = Question(
...     "Place C D.",
...     choices=[],
...     answer="C4 D4",
...     construct_scale=asked,
...     exact_octave=True,
... )
>>> (
...     exact.check_scale(
...         [Note.parse("C4"), Note.parse("D4")]
...     ),
...     exact.check_scale(
...         [Note.parse("C5"), Note.parse("D5")]
...     ),
... )
(True, False)
```

## Question.check_steps

<div class="api-signature" markdown="1">

```python
def check_steps(steps: list[str]) -> bool
```

{% endraw %}{% include api-source.html name="Question.check_steps" line=570 %}{% raw %}

</div>

Report whether the steps marked between the notes of a scale are
the right ones.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `steps` | `list of str` | The steps the learner marked, left to right, each "W" or "H". |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the steps are not asked, or if they are those of `construct_steps`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "Mark the steps.",
...     choices=[],
...     answer="W H",
...     construct_steps=["W", "H"],
... )
>>> (
...     q.check_steps(["W", "H"]),
...     q.check_steps(["H", "W"]),
...     q.check_steps(["W"]),
... )
(True, False, False)
>>> Question(
...     "No steps.", choices=[], answer=""
... ).check_steps([])
True
```

## Question.check_built

<div class="api-signature" markdown="1">

```python
def check_built(count: int) -> bool
```

{% endraw %}{% include api-source.html name="Question.check_built" line=608 %}{% raw %}

</div>

Report whether a key signature built with the fork is the one
asked for.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `count` | `int` | The signature the learner built: that many sharps if positive, flats if negative. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if it equals `key`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "Build D major.",
...     choices=[],
...     answer="2 sharps",
...     key=2,
...     show_staff=True,
...     build_key=True,
... )
>>> q.check_built(2), q.check_built(-2)
(True, False)
```

## Question.places_sequence

<div class="api-signature" markdown="1">

```python
@property
def places_sequence() -> bool
```

{% endraw %}{% include api-source.html name="Question.places_sequence" line=640 %}{% raw %}

</div>

Report whether the learner enters successive positions on the
staff.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True for scales and handwritten key signatures. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Question(
...     "D major",
...     choices=[],
...     answer="F♯5 C♯5",
...     place_signature=True,
... ).places_sequence
True
```

## Question.check

<div class="api-signature" markdown="1">

```python
def check(choice: str) -> bool
```

{% endraw %}{% include api-source.html name="Question.check" line=662 %}{% raw %}

</div>

Report whether a chosen answer is right.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `choice` | `str` | The text of the button that was pressed. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if it is the answer or one of the other accepted answers. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "",
...     choices=["F♯", "G♭"],
...     answer="F♯",
...     accept=("G♭",),
... )
>>> q.check("F♯"), q.check("G♭"), q.check("A")
(True, True, False)
>>> both = Question(
...     "",
...     choices=["B", "C♭", "D"],
...     answer="B",
...     required=("B", "C♭"),
... )
>>> (
...     both.check("B"),
...     both.check("C♭"),
...     both.check("D"),
... )  # each is right, but both are needed: see `complete`
(True, True, False)
```

## Question.complete

<div class="api-signature" markdown="1">

```python
def complete(given: set[str]) -> bool
```

{% endraw %}{% include api-source.html name="Question.complete" line=706 %}{% raw %}

</div>

Report whether the answers given so far are all of those needed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `given` | `set of str` | The right answers given so far. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | For an ordinary question, whether the answer has been given; for one with several `required`, whether all have. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> both = Question(
...     "",
...     choices=["B", "C♭"],
...     answer="B",
...     required=("B", "C♭"),
... )
>>> (
...     both.complete({"B"}),
...     both.complete({"C♭", "B"}),
... )
(False, True)
>>> Question(
...     "", choices=["C"], answer="C"
... ).complete({"C"})
True
```

## Question.item_key

<div class="api-signature" markdown="1">

```python
def item_key() -> str
```

{% endraw %}{% include api-source.html name="Question.item_key" line=745 %}{% raw %}

</div>

Return a stable identity for the question, so the same one can
be recognized when it comes around again.

It covers what is asked and where it is drawn, but not the note
value or the order of the buttons.

**Returns**

| Type | Description |
| --- | --- |
| `str` | A 20-character hexadecimal string. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> a = Question(
...     "Name it.",
...     choices=["C", "D"],
...     answer="C",
... )
>>> b = Question(
...     "Name it.",
...     choices=["D", "C"],
...     answer="C",
... )  # the same question, buttons in another order
>>> a.item_key() == b.item_key()
True
>>> len(a.item_key())
20
```

## Question.to_dict

<div class="api-signature" markdown="1">

```python
def to_dict() -> dict
```

{% endraw %}{% include api-source.html name="Question.to_dict" line=866 %}{% raw %}

</div>

Return the question as plain data, so it can be stored and asked
again.

**Returns**

| Type | Description |
| --- | --- |
| `dict` | The fields of the question, with notes as dictionaries and tuples as lists. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> data = Question(
...     "Name it.",
...     choices=["C"],
...     answer="C",
...     staff=[[Note.parse("C4")]],
... ).to_dict()
>>> data["answer"], data["staff"]
('C', [[{'octave': 4, 'letter': 0, 'accidental': 0}]])
```

## Question.from_dict

<div class="api-signature" markdown="1">

```python
@classmethod
def from_dict(d: dict) -> Question
```

{% endraw %}{% include api-source.html name="Question.from_dict" line=897 %}{% raw %}

</div>

Rebuild a question from the data that `to_dict` made.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `d` | `dict` | The stored data. Questions saved by older versions, which may carry a `play` field, are accepted. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The question. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "Name it.",
...     choices=["C", "D"],
...     answer="C",
...     key=2,
...     accept=("D",),
... )
>>> Question.from_dict(q.to_dict()) == q
True
```
{% endraw %}
