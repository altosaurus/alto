---
title: IntervalNames
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-intervalnames/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class IntervalNames(Exercise)
```

{% endraw %}{% include api-source.html name="IntervalNames" line=776 %}{% raw %}

</div>

Name the interval between two written notes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = IntervalNames().generate(
...     random.Random(3)
... )
>>> (
...     [len(chord) for chord in q.staff],
...     q.answer in q.choices,
... )
([2], True)
```

## IntervalNames.card_prompt

<div class="api-signature" markdown="1">

```python
def card_prompt(question: Question) -> str
```

{% endraw %}{% include api-source.html name="IntervalNames.card_prompt" line=798 %}{% raw %}

</div>

Say whether to name the interval's number, its quality, both, or
its inversion.

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
>>> IntervalNames().card_prompt(
...     Question("", choices=[], answer="3")
... )
'Identify the numeric interval.'
>>> IntervalNames().card_prompt(
...     Question("", choices=[], answer="M3")
... )
'Identify the interval and quality.'
```

## IntervalNames.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="IntervalNames.instructions" line=836 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "quality followed by a number"
...     in IntervalNames().instructions()
... )
True
```

## IntervalNames.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="IntervalNames.settings_signature" line=877 %}{% raw %}

</div>

Identify the settings used to generate and grade the interval.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The stored-question review signature. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Harmonic" in IntervalNames().settings_signature()
True
```

## IntervalNames.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="IntervalNames.refresh" line=933 %}{% raw %}

</div>

Arrange written interval answers by quality, with interval
numbers in columns.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | A new or saved interval question. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The same answer choices in reading order. Perfect and major share a row. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = Question(
...     "",
...     choices=["d3", "m3", "P4", "M3", "A3"],
...     answer="m3",
... )
>>> IntervalNames().refresh(q).choices
['A3', 'M3', 'P4', 'm3', 'd3']
```

## IntervalNames.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="IntervalNames.generate" line=977 %}{% raw %}

</div>

Make two notes whose interval is to be named.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The lower and higher note on a staff, and the interval (such as 'M3' or 'P5') as the answer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = IntervalNames().generate(
...     random.Random(4)
... )
>>> q.answer[0] in "PMmAd" and q.answer[
...     1:
... ].isdigit()
True
```
{% endraw %}
