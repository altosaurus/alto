---
title: ClefBasics
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-clefbasics/
---
{% raw %}
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

## ClefBasics.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="ClefBasics.settings_signature" line=4601 %}{% raw %}

</div>

Use button preferences for reviews only when the learner answers
with buttons.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The signature for the active question type. |

**Examples**

```text
Changing Button count leaves staff-placement reviews available.
```

## ClefBasics.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="ClefBasics.practice_signature" line=4621 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The clefs asked for. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasics().settings_signature().startswith(
...     "["
... )
True
```

## ClefBasics.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ClefBasics.instructions" line=4639 %}{% raw %}

</div>

Return the help text for the exercise, for the kind of question
that is being asked.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Clef Basics" in ClefBasics().instructions()
True
```

## ClefBasics.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ClefBasics.make_question" line=4689 %}{% raw %}

</div>

Name a clef to place, or draw a clef to name.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | For construction, a blank staff and the name of the clef, which is the question written under the staff. For identification, a staff with the clef drawn on it, and a button for each clef that can be asked for. |

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
{% endraw %}
