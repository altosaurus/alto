---
title: RythmicEquations
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-rythmicequations/
---
{% raw %}
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

## RythmicEquations.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="RythmicEquations.instructions" line=5986 %}{% raw %}

</div>

Explain how to complete the equation with a button or its
shortcut.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Instructions for the exercise. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "keys" in RythmicEquations().instructions()
True
```

## RythmicEquations.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="RythmicEquations.card_prompt" line=6007 %}{% raw %}

</div>

Ask for the missing symbol or number on an exported card.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The equation on the card. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The instruction shown above the equation. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RythmicEquations().card_prompt(
...     Question("", choices=[], answer="")
... )
'Which note or rest balances the equation?'
```

## RythmicEquations.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="RythmicEquations.practice_signature" line=6034 %}{% raw %}

</div>

Keep review questions tied to the options that generated them.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The selected operators and symbols, or an empty string for the original defaults. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RythmicEquations().practice_signature()
''
```

## RythmicEquations.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="RythmicEquations.make_question" line=6108 %}{% raw %}

</div>

Write a rhythm equation and hide a symbol or number.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Chooses the note value, operation, and blank position. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The equation and the note values available as answers. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RythmicEquations().make_question(
...     random.Random(0)
... ).prompt.count("_")
1
```
{% endraw %}
