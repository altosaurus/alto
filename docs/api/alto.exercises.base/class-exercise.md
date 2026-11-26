---
title: Exercise
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/class-exercise/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class Exercise(ABC)
```

{% endraw %}{% include api-source.html name="Exercise" line=1072 %}{% raw %}

</div>

What every exercise provides: its name, how it makes questions and
how long a good answer takes.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `name` | `str` | The title shown on the home screen and in the exercise list. |
| `category` | `str` | The heading it is listed under. |
| `description` | `str` | One line saying what the exercise is for. |
| `par_seconds` | `float, default 5.0` | How long a good first answer takes; much quicker earns credit and much slower counts against the question. |
| `icon` | `str, default ""` | SVG shapes for the exercise's tile, in a 24 by 24 box with COLOR where the theme's ink goes. Plugins supply one; empty uses Alto's own icon for the exercise. |
| `has_sound` | `bool, default True` | False for an exercise that makes no sound at all, whatever the sound button says. |
| `interval_voices` | `bool, default False` | True when two notes on the staff are an interval: they keep the question's note value, with the stems apart, and are played one after the other when they are melodic. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(Exercise):
...     name = "Demo"
...
...     def generate(self, rng):
...         return Question(
...             "Pick A.",
...             choices=["A", "B"],
...             answer="A",
...         )
>>> Demo().generate(random.Random(0)).answer
'A'
```

## Exercise.sound_instrument

<div class="api-signature" markdown="1">

```python
def sound_instrument(key: str | None) -> str | None
```

{% endraw %}{% include api-source.html name="Exercise.sound_instrument" line=1131 %}{% raw %}

</div>

Choose the instrument that plays this exercise's notes.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str or None` | The key of the instrument the question's picture asks for, or None when it asks for none. |

**Returns**

| Type | Description |
| --- | --- |
| `str or None` | The key to play with, or None for the learner's own choice of sound. Exercises return the picture's instrument unless a setting says otherwise. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> NoteNames().sound_instrument(
...     "pack.viola.bowed-viola"
... )
'pack.viola.bowed-viola'
```

## Exercise.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="Exercise.settings_signature" line=1158 %}{% raw %}

</div>

Return what identifies the settings that shape the questions.

A stored question is only asked again while this is unchanged.
Exercises with settings override it.

**Returns**

| Type | Description |
| --- | --- |
| `str` | An identifier; empty for an exercise with no settings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(Exercise):
...     def generate(self, rng):
...         return Question(
...             "?", choices=["A"], answer="A"
...         )
>>> Demo().settings_signature()
''
```

## Exercise.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="Exercise.card_prompt" line=1182 %}{% raw %}

</div>

Say what to do on a flashcard made from a question, where
nothing on screen explains the task.

Exercises whose on-screen prompt depends on the screen (buttons
to press, a staff to click) override this.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The question on the card. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The instruction, shown above the card's picture. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(Exercise):
...     name = "Demo"
...
...     def generate(self, rng):
...         return Question(
...             "Pick A.",
...             choices=["A"],
...             answer="A",
...         )
>>> Demo().card_prompt(
...     Question("", choices=["A"], answer="A")
... )
'Demo'
>>> Demo().card_prompt(
...     Question(
...         "Click the fermata.",
...         choices=[],
...         answer="fermata",
...         notation_target=("fermata", 0),
...     )
... )
'Locate the fermata.'
```

## Exercise.card_groups

<div class="api-signature" markdown="1">

```python
def card_groups() -> dict[str, str] | None
```

{% endraw %}{% include api-source.html name="Exercise.card_groups" line=1235 %}{% raw %}

</div>

Map playable examples to the skills that share a calendar review
date.

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str or None` | Example item keys mapped to skill names, or None when every example has its own schedule. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     KeyboardNotes,
... )
>>> KeyboardNotes().card_groups() is None
True
```

## Exercise.card_count

<div class="api-signature" markdown="1">

```python
def card_count() -> int | None
```

{% endraw %}{% include api-source.html name="Exercise.card_count" line=1256 %}{% raw %}

</div>

Count distinct cards possible with the current settings when the
exercise has an exact catalog.

**Returns**

| Type | Description |
| --- | --- |
| `int or None` | Catalog size, or None for an exercise that prepares a bounded daily sample. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     KeyboardNotes,
... )
>>> KeyboardNotes().card_count() is None
True
```

## Exercise.daily_candidates

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="Exercise.daily_candidates" line=1278 %}{% raw %}

</div>

Yield distinct questions until 100 consecutive draws find no new
playable item.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The generator for this day's sample. |

**Yields**

- *Question*: A playable question. Finite exercises can override this to visit every eligible item.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     KeyboardNotes,
... )
>>> isinstance(
...     next(
...         KeyboardNotes().daily_candidates(
...             random.Random(1)
...         )
...     ),
...     Question,
... )
True
```

## Exercise.review_question

<div class="api-signature" markdown="1">

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

{% endraw %}{% include api-source.html name="Exercise.review_question" line=1321 %}{% raw %}

</div>

Adapt a stored question for review under the active settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | Previously introduced card. |
| `same_settings` | `bool` | Whether the saved presentation matches the active settings. |

**Returns**

| Type | Description |
| --- | --- |
| `Question or None` | A playable question when the exercise recognizes this presentation. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     KeyboardNotes,
... )
>>> ex = KeyboardNotes()
>>> q = ex.generate(random.Random(1))
>>> ex.review_question(
...     q, same_settings=True
... ) == q
True
```

## Exercise.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="Exercise.refresh" line=1357 %}{% raw %}

</div>

Bring a stored question up to date with how the exercise draws
its questions now.

A question that is asked again comes from the copy stored when
it was first asked, which an older version may
have drawn differently. The default leaves it as it is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The question as it was stored. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The question as the exercise would draw it today. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(Exercise):
...     def generate(self, rng):
...         return Question(
...             "?", choices=["A"], answer="A"
...         )
>>> q = Question("?", choices=["A"], answer="A")
>>> Demo().refresh(q) is q
True
```

## Exercise.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="Exercise.instructions" line=1389 %}{% raw %}

</div>

Return the help text shown from the exercise's help button.

Exercises override it to describe themselves.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML; by default the one-line description. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(Exercise):
...     description = "Spot the note."
...
...     def generate(self, rng):
...         return Question(
...             "?", choices=["A"], answer="A"
...         )
>>> Demo().instructions()
'Spot the note.'
```

## Exercise.generate

<div class="api-signature" markdown="1">

```python
@abstractmethod
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="Exercise.generate" line=1415 %}{% raw %}

</div>

Make one new question.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator to use, so tests can ask for a repeatable question. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The question. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> q = NoteNames().generate(random.Random(1))
>>> q.answer in q.choices
True
```
{% endraw %}
