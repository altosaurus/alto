---
title: BeatIdentification
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-beatidentification/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class BeatIdentification(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="BeatIdentification" line=5431 %}{% raw %}

</div>

Identify the time signature or classify the meter of a rhythm.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = BeatIdentification().generate(random.Random(2))
>>> q.answer in q.choices and bool(q.rhythm)
True
```

## BeatIdentification.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="BeatIdentification.practice_signature" line=5447 %}{% raw %}

</div>

Keep separate review settings for the two rhythm components.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The original empty signature for time signature practice, or the selected component for classification practice. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatIdentification().practice_signature()
''
```

## BeatIdentification.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="BeatIdentification.instructions" line=5471 %}{% raw %}

</div>

Explain how to answer from the two written measures.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The task and its keyboard shortcut directions. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "keys" in BeatIdentification().instructions()
True
```

## BeatIdentification.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="BeatIdentification.make_question" line=5505 %}{% raw %}

</div>

Generate two complete measures in a randomly chosen meter.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Chooses the time signature and how each beat is written. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The rhythm and the answers for the selected component. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = BeatIdentification().make_question(random.Random(0))
>>> q.prompt
'What is the time signature?'
```
{% endraw %}
