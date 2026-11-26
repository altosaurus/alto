---
title: OrderOfKeysSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-orderofkeyssettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
OrderOfKeysSettings(
    *,
    starting_accidentals: set[int] = field(default_factory=lambda: {0}),
)
```

{% endraw %}{% include api-source.html name="OrderOfKeysSettings" line=1454 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

Choose the starting signs for writing a key signature.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `starting_accidentals` | `set of int` | Allowed counts of given signs. Negative counts represent flats and positive counts represent sharps. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> OrderOfKeysSettings(
...     keys={-2, 4}
... ).available_starts()
range(-2, 5)
```

## OrderOfKeysSettings.available_starts

<div class="api-signature" markdown="1">

```python
def available_starts() -> range
```

{% endraw %}{% include api-source.html name="OrderOfKeysSettings.available_starts" line=1475 %}{% raw %}

</div>

Return starting counts that fit at least one selected signature.

**Returns**

| Type | Description |
| --- | --- |
| `range` | Counts from the flattest eligible start through the sharpest, always including zero. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> list(
...     OrderOfKeysSettings(
...         keys={-2}
...     ).available_starts()
... )
[-2, -1, 0]
```
{% endraw %}
