---
title: KeyChoice
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-keychoice/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class KeyChoice
```

{% endraw %}{% include api-source.html name="KeyChoice" line=381 %}{% raw %}

</div>

Settings with a set of chosen key signatures.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `keys` | `set of int` | The chosen key signatures, as sharps (positive) or flats (negative). The dataclass that uses this mixin declares the field and its default. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardSettings(keys={3, -2}).active_keys()
[-2, 3]
```

## KeyChoice.active_keys

<div class="api-signature" markdown="1">

```python
def active_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="KeyChoice.active_keys" line=400 %}{% raw %}

</div>

Return the key signatures to draw from, lowest first.

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | Sharps (positive) or flats (negative); no sharps or flats if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ConstructionSettings(
...     keys={2, -1}
... ).active_keys()
[-1, 2]
>>> KeySignatureSettings(
...     keys=set()
... ).active_keys()
[0]
```
{% endraw %}
