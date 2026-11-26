---
title: IntervalConstruction
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-intervalconstruction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class IntervalConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="IntervalConstruction" line=1281 %}{% raw %}

</div>

Place a second written note at the requested interval from a given
note.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = IntervalConstruction().generate(
...     random.Random(2)
... )
>>> q.construct is not None and q.check_placed(
...     q.construct
... )
True
```

## IntervalConstruction.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="IntervalConstruction.instructions" line=1305 %}{% raw %}

</div>

Explain staff placement and spelling for interval construction.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Instructions for mouse and keyboard input. |

**Examples**

```text
The reference describes the difference between melodic and
harmonic placement.
```

## IntervalConstruction.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="IntervalConstruction.settings_signature" line=1330 %}{% raw %}

</div>

Identify the construction settings used to generate a stored
card.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Stable signature of the exercise options. |

**Examples**

```text
A change in staff ranges changes which stored questions are
eligible.
```

## IntervalConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="IntervalConstruction.generate" line=1349 %}{% raw %}

</div>

Generate a staff, an interval prompt, and its eligible
placements.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Generator for the presentation. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | Written interval to construct. |

**Examples**

```text
A harmonic question asks for a note above its starting note.
```
{% endraw %}
