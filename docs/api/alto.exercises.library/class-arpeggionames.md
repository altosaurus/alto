---
title: ArpeggioNames
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-arpeggionames/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ArpeggioNames(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="ArpeggioNames" line=3197 %}{% raw %}

</div>

Name the type and the inversion of a broken chord.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ArpeggioNames().generate(
...     random.Random(11)
... )
>>> q.octaves is not None and len(q.staff) >= 4
True
```

## ArpeggioNames.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="ArpeggioNames.practice_signature" line=3215 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The clefs, chord types, inversions and key signatures in force. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioNames().settings_signature().startswith(
...     "["
... )
True
```

## ArpeggioNames.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ArpeggioNames.instructions" line=3234 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "inversion" in ArpeggioNames().instructions()
True
```

## ArpeggioNames.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ArpeggioNames.make_question" line=3264 %}{% raw %}

</div>

Make an arpeggio on one of the chosen clefs, in a chosen
position.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The arpeggio's notes one after another on a staff; the answer is the chord type and inversion, such as 'major · 1st inversion'. |

**Raises**

- *RuntimeError*: If no arpeggio fits the chosen clefs, chord types and inversions.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ArpeggioNames().generate(
...     random.Random(12)
... )
>>> " · " in q.answer
True
```
{% endraw %}
