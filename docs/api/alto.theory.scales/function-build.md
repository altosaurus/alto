---
title: build
parent: alto.theory.scales
api_module: alto.theory.scales
package: alto.theory
permalink: /api/alto.theory.scales/function-build/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def build(
    tonic: Note,
    *,
    intervals: list[Interval],
) -> list[Note]
```

{% endraw %}{% include api-source.html name="build" line=239 %}{% raw %}

</div>

Build the notes of a scale or chord above a tonic.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `tonic` | `Note` | The first note. |
| `intervals` | `list of Interval` | The intervals above the tonic, including the unison, such as a value of `SCALES` or `CHORDS`. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of Note` | The tonic transposed by each interval, in order. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [
...     str(n)
...     for n in build(
...         Note.parse("G4"),
...         intervals=SCALES["Major (Ionian)"],
...     )
... ]
['G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F♯5']
```
{% endraw %}
