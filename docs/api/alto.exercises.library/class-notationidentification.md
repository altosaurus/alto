---
title: NotationIdentification
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-notationidentification/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class NotationIdentification(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="NotationIdentification" line=4761 %}{% raw %}

</div>

Identify the highlighted part of a written phrase.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NotationIdentification().generate(
...     random.Random(2)
... )
>>> bool(
...     q.staff or q.notation_excerpt
... ) and q.answer in q.choices
True
```

## NotationIdentification.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="NotationIdentification.settings_signature" line=4786 %}{% raw %}

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

## NotationIdentification.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="NotationIdentification.practice_signature" line=4806 %}{% raw %}

</div>

Identify the terms eligible for review.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The selected terms, or the original empty signature when all terms are enabled. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NotationIdentification().settings_signature()
''
```

## NotationIdentification.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="NotationIdentification.instructions" line=4829 %}{% raw %}

</div>

Explain how to answer the notation question.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Help for mouse and keyboard users. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "number" in NotationIdentification().instructions()
True
```

## NotationIdentification.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="NotationIdentification.refresh" line=4924 %}{% raw %}

</div>

Replace unchecked distractors in older practice questions before
replay.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | Stored question matching the current settings signature. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The original notation with eligible answer buttons. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NotationIdentification()
>>> q = ex.generate(random.Random(1))
>>> ex.refresh(q) == q
True
```

## NotationIdentification.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="NotationIdentification.make_question" line=4953 %}{% raw %}

</div>

Choose a phrase and a single visible feature to highlight.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Source for the phrase, feature, and its position. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A short phrase with the selected marking and checked answer choices. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = NotationIdentification().generate(
...     random.Random(0)
... )
>>> q.notation_target[0] == q.answer
True
```

## NotationIdentification.card_groups

<div class="api-signature" markdown="1">

```python
def card_groups() -> dict[str, str]
```

{% endraw %}{% include api-source.html name="NotationIdentification.card_groups" line=5236 %}{% raw %}

</div>

Group the active question type’s playable examples by the symbol
being practiced.

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | Map from each eligible example’s item key to its selected term. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bool(NotationIdentification().card_groups())
True
```

## NotationIdentification.daily_candidates

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="NotationIdentification.daily_candidates" line=5258 %}{% raw %}

</div>

Choose one example for each selected notation term.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Randomizes term order, examples and distractors. |

**Yields**

- *Question*: A distinct playable card with the current answer controls.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> next(
...     NotationIdentification().daily_candidates(
...         random.Random(4)
...     )
... ).answer in settings.notation.terms
True
```

## NotationIdentification.review_question

<div class="api-signature" markdown="1">

```python
def review_question(
    question: Question,
    *,
    same_settings: bool,
) -> Question | None
```

{% endraw %}{% include api-source.html name="NotationIdentification.review_question" line=5329 %}{% raw %}

</div>

Recover an eligible saved example under the current term and
button selections.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | Saved question. |
| `same_settings` | `bool` | Whether the presentation settings still match. |

**Returns**

| Type | Description |
| --- | --- |
| `Question or None` | The current presentation of the card, or None if its term or example is outside the catalog. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ex = NotationIdentification()
>>> q = ex.generate(random.Random(4))
>>> ex.review_question(
...     q, same_settings=True
... ) == q
True
```
{% endraw %}
