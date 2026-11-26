---
title: KeySignatureConstruction
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/class-keysignatureconstruction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class KeySignatureConstruction(Exercise)
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction" line=1899 %}{% raw %}

</div>

Build the key signature of a named key on a blank staff, with the
fork.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatureConstruction().generate(
...     random.Random(5)
... )
>>> q.build_key, q.staff, q.choices
(True, [], [])
```

## KeySignatureConstruction.settings_signature

<div class="api-signature" markdown="1">

```python
def settings_signature() -> str
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction.settings_signature" line=1919 %}{% raw %}

</div>

Return what identifies the settings that shape these questions.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The clefs, scales and key signatures in force. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatureConstruction().settings_signature().startswith(
...     "["
... )
True
```

## KeySignatureConstruction.instructions

<div class="api-signature" markdown="1">

```python
def instructions() -> str
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction.instructions" line=1937 %}{% raw %}

</div>

Return the help text for the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     "Key Signature Construction"
...     in KeySignatureConstruction().instructions()
... )
True
```

## KeySignatureConstruction.generate

<div class="api-signature" markdown="1">

```python
def generate(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="KeySignatureConstruction.generate" line=1972 %}{% raw %}

</div>

Name a key whose signature is to be built.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | A blank staff captioned with the key, such as 'D Major'; the answer is its sharps or flats. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> q = KeySignatureConstruction().generate(
...     random.Random(1)
... )
>>> q.caption.split()[0] in {
...     "C",
...     "D",
...     "E",
...     "F",
...     "G",
...     "A",
...     "B",
... } or "♯" in q.caption or "♭" in q.caption
True
>>> q.answer == format_key_signature(q.key)
True
```
{% endraw %}
