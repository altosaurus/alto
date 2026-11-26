---
title: ScaleIdentification
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-scaleidentification/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ScaleIdentification(Exercise)
```

{% endraw %}{% include api-source.html name="ScaleIdentification" line=2280 %}{% raw %}

</div>

Identify the tonic and type of a scale drawn on a staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleIdentification().generate(
...     random.Random(7)
... )
>>> len(q.staff), q.answer in q.choices
(8, True)
```

## ScaleIdentification.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="ScaleIdentification.settings_signature" line=2298 %}{% raw %}

</div>

Identify the clefs, scale types and staff and scale signatures
in force.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The serialized question settings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleIdentification().settings_signature().startswith(
...     "["
... )
True
```

## ScaleIdentification.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ScaleIdentification.instructions" line=2331 %}{% raw %}

</div>

Explain how to identify the scale, including a staff with a
different signature.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML help text. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Scale Identification"
...     in ScaleIdentification().instructions()
... )
True
```

## ScaleIdentification.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ScaleIdentification.generate" line=2366 %}{% raw %}

</div>

Draw a one-octave scale and offer scale names without revealing
the answer on the staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | Eight staff notes and a choice of tonic and scale type. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleIdentification().generate(
...     random.Random(8)
... )
>>> q.staff[0][0].name == q.staff[-1][
...     0
... ].name and not q.caption
True
```
{% endraw %}
