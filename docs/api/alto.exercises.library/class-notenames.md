---
title: NoteNames
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-notenames/
---
{% raw %}
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

| Parameter | Type | Description |
| --- | --- | --- |
| `accidentals` | `bool, default False` | Ask notes with explicit sharps, flats and naturals, whatever the settings say. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames(accidentals=True).accidentals
True
```

## NoteNames.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="NoteNames.card_prompt" line=267 %}{% raw %}

</div>

Say what to name on a flashcard, and in which form: letters,
solfège or a scale degree, with the octave if it counts.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The question on the card. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The instruction. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames().card_prompt(
...     Question("", choices=[], answer="C")
... )
'Identify the note.'
```

## NoteNames.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="NoteNames.practice_signature" line=291 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The clefs, ranges, key signatures, note values and naming in force, and whether accidentals are asked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames().settings_signature() != NoteNames(
...     accidentals=True
... ).settings_signature()
True
```

## NoteNames.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="NoteNames.instructions" line=314 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Press the button with its name"
...     in NoteNames().instructions()
... )
True
```

## NoteNames.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="NoteNames.make_question" line=369 %}{% raw %}

</div>

Make a note to name, on one of the chosen clefs, in a chosen
key.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The note drawn on a staff, with one button for each name that could be the answer. |

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

## NoteNames.card_count

<div class="api-signature" markdown="1">

```python
def card_count() -> int
```

{% endraw %}{% include api-source.html name="NoteNames.card_count" line=422 %}{% raw %}

</div>

Count written pitches across the selected ranges, clefs and
signatures.

**Returns**

| Type | Description |
| --- | --- |
| `int` | Each staff position contributes one spelling, or three when accidentals are enabled. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNames().card_count() > 0
True
```

## NoteNames.daily_candidates

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="NoteNames.daily_candidates" line=451 %}{% raw %}

</div>

Visit each selectable written note once, in shuffled order.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Source of the daily order and answer choices. |

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

## NoteNames.review_question

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

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | Saved note and answer. |
| `same_settings` | `bool` | Whether its original settings are active. |

**Returns**

| Type | Description |
| --- | --- |
| `Question or None` | The note with the current answer bank, or None outside the selected material. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NoteNames()
>>> q = ex.generate(random.Random(1))
>>> ex.review_question(
...     q, same_settings=True
... ) == q
True
```
{% endraw %}
