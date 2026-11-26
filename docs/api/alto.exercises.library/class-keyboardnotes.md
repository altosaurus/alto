---
title: KeyboardNotes
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-keyboardnotes/
---
{% raw %}
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

## KeyboardNotes.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="KeyboardNotes.card_prompt" line=3604 %}{% raw %}

</div>

Say what to name on a flashcard. Letter names give the octave if
it counts, and follow the key signature if one is shown.

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

## KeyboardNotes.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="KeyboardNotes.practice_signature" line=3643 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The keyboard range, black keys, octave and key signature settings, and the naming in force. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardNotes().settings_signature().startswith(
...     "["
... )
True
```

## KeyboardNotes.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeyboardNotes.instructions" line=3665 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML, with paragraphs added for the octave and key signature settings that are on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "highlighted" in KeyboardNotes().instructions()
True
```

## KeyboardNotes.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeyboardNotes.make_question" line=3727 %}{% raw %}

</div>

Make a keyboard with one key highlighted.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The keyboard, a grid of name buttons (and a row of octave buttons if octaves are asked), and the key's name as the answer, with the other spelling of a black key accepted. |

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
{% endraw %}
