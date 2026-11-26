---
title: arpeggio
parent: alto.theory.scales
api_module: alto.theory.scales
package: alto.theory
permalink: /api/alto.theory.scales/function-arpeggio/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def arpeggio(
    root: Note,
    *,
    intervals: list[Interval],
    inversion: int = 0,
) -> list[Note]
```

{% endraw %}{% include api-source.html name="arpeggio" line=185 %}{% raw %}

</div>

Return a chord broken and rising from its lowest note, then that
note again an octave higher.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `root` | `Note` | The root of the chord. |
| `intervals` | `list of Interval` | The intervals above the root that make the chord, such as `CHORDS["major"]`. Keyword-only. |
| `inversion` | `int, default 0` | How many of the lowest chord tones are moved up an octave first: 0 is root position, 1 puts the third at the bottom, 2 the fifth. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of Note` | The chord tones from the lowest up, ending on the lowest note an octave higher. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [
...     str(n)
...     for n in arpeggio(
...         Note.parse("C4"),
...         intervals=CHORDS["major"],
...     )
... ]
['C4', 'E4', 'G4', 'C5']
>>> [
...     str(n)
...     for n in arpeggio(
...         Note.parse("C4"),
...         intervals=CHORDS["major"],
...         inversion=1,
...     )
... ]
['E4', 'G4', 'C5', 'E5']
```
{% endraw %}
