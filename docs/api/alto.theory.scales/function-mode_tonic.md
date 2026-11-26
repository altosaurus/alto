---
title: mode_tonic
parent: alto.theory.scales
api_module: alto.theory.scales
package: alto.theory
permalink: /api/alto.theory.scales/function-mode_tonic/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def mode_tonic(
    count: int,
    *,
    mode: str,
) -> Note
```

{% endraw %}{% include api-source.html name="mode_tonic" line=131 %}{% raw %}

</div>

Return the note a scale in a given mode starts on, for a given key
signature.

The notes of a mode are those of a major scale started from another
degree. D Dorian, for example, has the key
signature of C major, started from its second note.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `count` | `int` | Sharps (positive) or flats (negative) in the key signature, from -7 to 7. |
| `mode` | `str` | A key of `MODE_DEGREE`, such as "Dorian" or "Natural minor (Aeolian)". Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The tonic of that mode, in octave 4 or 5. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> str(
...     mode_tonic(0, mode="Dorian")
... )  # no sharps or flats: D Dorian
'D4'
>>> str(
...     mode_tonic(
...         2, mode="Natural minor (Aeolian)"
...     )
... )  # two sharps: B minor
'B4'
```
{% endraw %}
