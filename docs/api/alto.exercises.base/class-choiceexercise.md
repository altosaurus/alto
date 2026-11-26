---
title: ChoiceExercise
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/class-choiceexercise/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ChoiceExercise(Exercise)
```

{% endraw %}{% include api-source.html name="ChoiceExercise" line=1456 %}{% raw %}

</div>

A button-answer exercise with its own standard Buttons submenu.

Supply the eligible choices in `make_question`. Set `default_limit`
to start in Limited mode.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     ChordQualities,
... )
>>> ChordQualities.button_settings().button_mode
'limited'
```

## ChoiceExercise.button_settings

<div class="api-signature" markdown="1">

```python
@classmethod
@cache
def button_settings() -> ButtonSettings
```

{% endraw %}{% include api-source.html name="ChoiceExercise.button_settings" line=1476 %}{% raw %}

</div>

Return the preferences shared by instances of this particular
exercise.

**Returns**

| Type | Description |
| --- | --- |
| `ButtonSettings` | The exercise's answer layout. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> NoteNames.button_settings().button_mode
'all'
```

## ChoiceExercise.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="ChoiceExercise.settings_signature" line=1497 %}{% raw %}

</div>

Include custom answer layouts when deciding which questions can
be replayed.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The original practice signature at the historical default, or a layout-specific signature. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     ChordQualities,
... )
>>> ChordQualities().settings_signature()
''
```

## ChoiceExercise.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="ChoiceExercise.practice_signature" line=1525 %}{% raw %}

</div>

Identify the exercise settings other than the answer layout.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The signature for questions using the default layout. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     ChordQualities,
... )
>>> ChordQualities().practice_signature()
''
```

## ChoiceExercise.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ChoiceExercise.generate" line=1544 %}{% raw %}

</div>

Generate the musical task and apply the selected button count.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Source for the exercise and the distractor sample. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A question with its answer buttons ready for practice. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     ChordQualities,
... )
>>> len(
...     ChordQualities()
...     .generate(random.Random(0))
...     .choices
... )
5
```

## ChoiceExercise.limit_buttons

<div class="api-signature" markdown="1">

```python
def limit_buttons(
    question: Question,
    *,
    rng: random.Random,
) -> Question
```

{% endraw %}{% include api-source.html name="ChoiceExercise.limit_buttons" line=1572 %}{% raw %}

</div>

Limit each answer group while keeping all the buttons needed to
complete the question.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The task and its eligible answer choices. |
| `rng` | `random.Random` | Source for sampling distractors. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The question with its chosen layout. |

**Examples**

```text
A note and octave question keeps the correct name and octave in
their respective groups.
```

## ChoiceExercise.make_question

<div class="api-signature" markdown="1">

```python
@abstractmethod
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ChoiceExercise.make_question" line=1661 %}{% raw %}

</div>

Generate the task and eligible answer choices before the button
limit is applied.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The exercise's random source. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The musical task. |

**Examples**

```text
Note Identification supplies the note names appropriate to the
active clef and key settings.
```
{% endraw %}
