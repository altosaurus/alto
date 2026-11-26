---
title: KeyboardIntervals
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-keyboardintervals/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class KeyboardIntervals(Exercise)
```

{% endraw %}{% include api-source.html name="KeyboardIntervals" line=1376 %}{% raw %}

</div>

Identify the ascending interval between two highlighted piano keys.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `INTERVALS` | `tuple of str` | Conventional names for every distance on the piano, including compound intervals and combined tritone answers. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeyboardIntervals().generate(
...     random.Random(5)
... )
>>> (
...     len(q.keyboard_notes),
...     q.answer in q.choices,
...     q.staff,
... )
(2, True, [])
```

## KeyboardIntervals.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.card_prompt" line=1405 %}{% raw %}

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
>>> KeyboardIntervals().card_prompt(
...     Question("", choices=[], answer="P5")
... )
'Identify the interval.'
```

## KeyboardIntervals.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.settings_signature" line=1429 %}{% raw %}

</div>

Identify the keyboard range and selected intervals for
stored-question reviews.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The settings that determine which questions can be asked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> bool(
...     KeyboardIntervals().settings_signature()
... )
True
```

## KeyboardIntervals.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.instructions" line=1448 %}{% raw %}

</div>

Explain how to identify an interval from two highlighted keys.

**Returns**

| Type | Description |
| --- | --- |
| `str` | HTML explaining interval names and enharmonic ambiguity on the keyboard. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "A4 / d5" in KeyboardIntervals().instructions()
True
```

## KeyboardIntervals.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeyboardIntervals.generate" line=1482 %}{% raw %}

</div>

Highlight two distinct keys at a selected interval within the
chosen range.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | Two highlighted keys and either a limited number of choices or a fixed bank for every selected interval. A prompt is returned if none are selected. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeyboardIntervals().generate(
...     random.Random(7)
... )
>>> 1 <= q.keyboard_notes[
...     1
... ].midi - q.keyboard_notes[0].midi <= 12
True
```
{% endraw %}
