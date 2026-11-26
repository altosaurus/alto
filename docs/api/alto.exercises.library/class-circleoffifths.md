---
title: CircleOfFifths
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-circleoffifths/
---
{% raw %}
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

## CircleOfFifths.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="CircleOfFifths.practice_signature" line=2790 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The kinds of question in force. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleOfFifths().settings_signature().startswith(
...     "["
... )
True
```

## CircleOfFifths.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="CircleOfFifths.instructions" line=2808 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML, with a paragraph for each kind of question that is switched on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "circle of fifths" in CircleOfFifths().instructions()
True
```

## CircleOfFifths.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="CircleOfFifths.make_question" line=2873 %}{% raw %}

</div>

Pick a kind of question that is switched on, and ask it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A question on the circle: `circle_kind` says which kind. |

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
{% endraw %}
