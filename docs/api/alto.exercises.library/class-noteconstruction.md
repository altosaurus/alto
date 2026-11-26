---
title: NoteConstruction
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-noteconstruction/
---
{% raw %}
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

## NoteConstruction.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="NoteConstruction.card_prompt" line=3918 %}{% raw %}

</div>

Say which note to place, whichever way the on-screen prompt
words it.

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

## NoteConstruction.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="NoteConstruction.settings_signature" line=3957 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The clefs, accidentals and key signature settings, and the naming in force. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstruction().settings_signature().startswith(
...     "["
... )
True
```

## NoteConstruction.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="NoteConstruction.instructions" line=4006 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML, with paragraphs added for the key signature and accidental settings that are on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Click the staff" in NoteConstruction().instructions()
True
```

## NoteConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="NoteConstruction.generate" line=4076 %}{% raw %}

</div>

Make a note name to be placed on the staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A prompt such as 'Place F♯4 on the staff.'; the answer is the note's name, and `construct` is the note to place. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NoteConstruction().generate(
...     random.Random(16)
... )
>>> q.answer in q.prompt
True
```

## NoteConstruction.card_count

<div class="api-signature" markdown="1">

```python
def card_count() -> int
```

{% endraw %}{% include api-source.html name="NoteConstruction.card_count" line=4261 %}{% raw %}

</div>

Count distinct construction cards without rendering them.

**Returns**

| Type | Description |
| --- | --- |
| `int` | Number of eligible written placements under the current settings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteConstruction().card_count() > 0
True
```

## NoteConstruction.daily_candidates

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="NoteConstruction.daily_candidates" line=4280 %}{% raw %}

</div>

Visit all eligible placements in a randomized order.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Source for the order of the signatures and placements. |

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

## NoteConstruction.review_question

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

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | Stored construction card. |
| `same_settings` | `bool` | Whether its original settings are still active. |

**Returns**

| Type | Description |
| --- | --- |
| `Question or None` | The playable card if its placement and prompt remain eligible. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NoteConstruction()
>>> q = ex.generate(random.Random(3))
>>> ex.review_question(
...     q, same_settings=True
... ) == q
True
```
{% endraw %}
