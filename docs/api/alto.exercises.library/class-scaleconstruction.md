---
title: ScaleConstruction
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-scaleconstruction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ScaleConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="ScaleConstruction" line=2460 %}{% raw %}

</div>

Place the notes of a named scale on a blank staff, one after
another.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleConstruction().generate(
...     random.Random(5)
... )
>>> (
...     len(q.construct_scale or []),
...     q.choices,
...     q.key,
... )
(8, [], 0)
```

## ScaleConstruction.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="ScaleConstruction.settings_signature" line=2483 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The clefs, scales and key signatures in force. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleConstruction().settings_signature().startswith(
...     "["
... )
True
```

## ScaleConstruction.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="ScaleConstruction.instructions" line=2509 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Scale Construction" in ScaleConstruction().instructions()
True
```

## ScaleConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="ScaleConstruction.generate" line=2600 %}{% raw %}

</div>

Name a scale to be placed on the staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A blank staff captioned with the scale, such as 'D Major'. The eight notes in the selected direction are stored in `construct_scale`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = ScaleConstruction().generate(
...     random.Random(1)
... )
>>> scale = q.construct_scale or []
>>> scale[0].name == scale[
...     -1
... ].name and q.accidentals
True
>>> q.check_scale(scale)
True
```
{% endraw %}
