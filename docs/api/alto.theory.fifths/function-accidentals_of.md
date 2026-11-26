---
title: accidentals_of
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-accidentals_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def accidentals_of(signature: int) -> list[str]
```

{% endraw %}{% include api-source.html name="accidentals_of" line=304 %}{% raw %}

</div>

Return the sharps or flats of a key signature, in the order they are
written.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `signature` | `int` | The number of sharps (positive) or flats (negative). |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The notes that are altered: "F♯", "C♯" and so on, or "B♭", "E♭" and so on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> accidentals_of(3), accidentals_of(0)
(['F♯', 'C♯', 'G♯'], [])
```
{% endraw %}
