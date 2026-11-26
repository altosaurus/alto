---
title: BeatConstruction
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-beatconstruction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class BeatConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="BeatConstruction" line=5866 %}{% raw %}

</div>

Mark where the main beats begin in two written measures.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = BeatConstruction().generate(random.Random(2))
>>> q.answer in BEAT_METERS and not q.choices
True
```

## BeatConstruction.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="BeatConstruction.settings_signature" line=5882 %}{% raw %}

</div>

Identify the note types used in a saved construction question.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Empty for the original selection, otherwise its signature. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatConstruction().settings_signature()
''
```

## BeatConstruction.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="BeatConstruction.instructions" line=5903 %}{% raw %}

</div>

Explain how to place and submit the beats.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Counting guidance and keyboard controls. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "arrow keys" in BeatConstruction().instructions()
True
```

## BeatConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="BeatConstruction.generate" line=5930 %}{% raw %}

</div>

Choose a time signature and write two measures to mark.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Chooses the meter and the written rhythm. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The rhythm and its time signature, without answer choices. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BeatConstruction().generate(random.Random(1)).prompt
'Place the beats in both measures.'
```
{% endraw %}
