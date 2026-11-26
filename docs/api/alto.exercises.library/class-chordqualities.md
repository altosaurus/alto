---
title: ChordQualities
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-chordqualities/
---
{% raw %}
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

## ChordQualities.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="ChordQualities.card_prompt" line=3090 %}{% raw %}

</div>

Say what to name on a flashcard.

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
>>> ChordQualities().card_prompt(
...     Question("", choices=[], answer="Major")
... )
'Identify the Chord Quality.'
```

## ChordQualities.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ChordQualities.instructions" line=3114 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "root position" in ChordQualities().instructions()
True
```

## ChordQualities.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ChordQualities.make_question" line=3136 %}{% raw %}

</div>

Make a chord in root position whose quality is to be named.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The chord drawn as one stack of notes, with its type (such as 'minor 7th') as the answer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ChordQualities().generate(
...     random.Random(10)
... )
>>> q.answer in CHORDS
True
```
{% endraw %}
