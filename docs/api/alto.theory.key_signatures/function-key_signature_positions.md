---
title: key_signature_positions
parent: alto.theory.key_signatures
api_module: alto.theory.key_signatures
package: alto.theory
permalink: /api/alto.theory.key_signatures/function-key_signature_positions/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def key_signature_positions(
    clef: str,
    *,
    sign: int,
) -> list[str]
```

{% endraw %}{% include api-source.html name="key_signature_positions" line=60 %}{% raw %}

</div>

Return the notes the sharps or flats of a key signature are written
on, in a clef.

Each accidental is a fourth up or a fifth down from the one before
(sharps: F C G D A E B, flats: B E A D G C F), and the
pattern is chosen so that all seven stay on the staff, or one step
above or below it. This gives the usual signatures for
the treble, bass, alto and tenor clefs, and works out the rest.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | A key of `BOTTOM_LINE`. |
| `sign` | `int` | 1 for sharps, -1 for flats. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | Seven note names with octaves, in the order the accidentals appear. |

**Raises**

- *ValueError*: If no placement keeps all seven accidentals on the staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_signature_positions("treble", sign=1)
['F5', 'C5', 'G5', 'D5', 'A4', 'E5', 'B4']
>>> key_signature_positions("bass", sign=-1)
['B2', 'E3', 'A2', 'D3', 'G2', 'C3', 'F2']
```
{% endraw %}
