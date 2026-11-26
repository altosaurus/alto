---
title: major_key_tonic
parent: alto.theory.scales
api_module: alto.theory.scales
package: alto.theory
permalink: /api/alto.theory.scales/function-major_key_tonic/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def major_key_tonic(count: int) -> Note
```

{% endraw %}{% include api-source.html name="major_key_tonic" line=90 %}{% raw %}

</div>

Return the tonic of the major key with a given number of sharps or
flats.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `count` | `int` | Sharps (positive) or flats (negative) in the key signature, from -7 to 7. |

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The tonic, in octave 4. |

**Raises**

- *KeyError*: If `count` is outside -7..7.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> str(
...     major_key_tonic(2)
... )  # two sharps: D major
'D4'
>>> str(
...     major_key_tonic(-3)
... )  # three flats: E♭ major
'E♭4'
```
{% endraw %}
