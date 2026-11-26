---
title: key_signature
parent: alto.theory.scales
api_module: alto.theory.scales
package: alto.theory
permalink: /api/alto.theory.scales/function-key_signature/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def key_signature(
    tonic_name: str,
    *,
    scale: str = 'Major (Ionian)',
) -> int
```

{% endraw %}{% include api-source.html name="key_signature" line=274 %}{% raw %}

</div>

Return the key signature of a scale as a signed count of
accidentals.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `tonic_name` | `str` | The tonic in plain text without an octave, such as 'G', 'Eb' or 'F#'. |
| `scale` | `str, default "Major (Ionian)"` | A key of `SCALES`. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The sum of the accidentals of the scale's notes: positive for sharps, negative for flats. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_signature("G")  # G major has one sharp
1
>>> key_signature(
...     "Eb"
... )  # E♭ major has three flats
-3
>>> key_signature(
...     "A", scale="Natural minor (Aeolian)"
... )  # A minor has none
0
```
{% endraw %}
