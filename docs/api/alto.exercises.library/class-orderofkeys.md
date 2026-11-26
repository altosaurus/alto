---
title: OrderOfKeys
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-orderofkeys/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class OrderOfKeys(Exercise)
```

{% endraw %}{% include api-source.html name="OrderOfKeys" line=2030 %}{% raw %}

</div>

Write the accidentals of a named key signature in order.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeys().generate(
...     random.Random(1)
... ).place_signature
True
```

## OrderOfKeys.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="OrderOfKeys.settings_signature" line=2048 %}{% raw %}

</div>

Identify the selections used to generate a practice question.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The original empty signature at the defaults, so earlier questions remain available for review. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeys().settings_signature()
''
```

## OrderOfKeys.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="OrderOfKeys.instructions" line=2077 %}{% raw %}

</div>

Explain how to enter and submit a signature.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The exercise help text. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Undo" in OrderOfKeys().instructions()
True
```

## OrderOfKeys.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="OrderOfKeys.generate" line=2103 %}{% raw %}

</div>

Choose a key from the selected scales and signatures and spell
it in a selected clef.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Source for the key, mode, and clef. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The named key and the ordered signs with their exact staff octaves. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = OrderOfKeys().generate(random.Random(2))
>>> q.show_staff and not q.choices
True
```
{% endraw %}
