---
title: KeySignatures
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-keysignatures/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class KeySignatures(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="KeySignatures" line=1631 %}{% raw %}

</div>

Read a key signature drawn on a staff and name the key it belongs
to.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatures().generate(
...     random.Random(5)
... )
>>> q.answer in q.choices
True
```

## KeySignatures.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="KeySignatures.practice_signature" line=1651 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The kinds of question, clefs, scales and key signatures in force. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatures().settings_signature().startswith(
...     "["
... )
True
```

## KeySignatures.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeySignatures.instructions" line=1670 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Key Signature Identification"
...     in KeySignatures().instructions()
... )
True
```

## KeySignatures.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="KeySignatures.refresh" line=1703 %}{% raw %}

</div>

Give a stored signature question the caption on its staff that
older versions did not write.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The question as it was stored. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The same question, captioned '_ Major' (or '_ minor', '_ Dorian' and so on) if it shows a staff and had no caption. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> old = Question(
...     "Which minor key has this key signature?",
...     choices=["C"],
...     answer="C",
...     key=-3,
...     show_staff=True,
... )
>>> KeySignatures().refresh(old).caption
'_ minor'
```

## KeySignatures.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeySignatures.make_question" line=1765 %}{% raw %}

</div>

Make a key signature to read.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A signature on a staff; the answer is the tonic of the scale that has it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatures().generate(
...     random.Random(6)
... )
>>> q.show_staff and q.answer in q.choices
True
```
{% endraw %}
