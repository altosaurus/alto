---
title: all_tonics
parent: alto.theory.scales
api_module: alto.theory.scales
package: alto.theory
permalink: /api/alto.theory.scales/function-all_tonics/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def all_tonics(max_accidentals: int = 1) -> list[Note]
```

{% endraw %}{% include api-source.html name="all_tonics" line=348 %}{% raw %}

</div>

Return every spelled tonic in octave 4, within a limit on
accidentals.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `max_accidentals` | `int, default 1` | The most sharps or flats a tonic may have, so 1 allows C♭ through B♯ but not double sharps. |

**Returns**

| Type | Description |
| --- | --- |
| `list of Note` | Each letter with each accidental from `-max_accidentals` to `max_accidentals`, letters in the order C to B. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(all_tonics())
21
>>> [str(n) for n in all_tonics(0)]
['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']
```
{% endraw %}
