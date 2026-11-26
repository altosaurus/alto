---
title: key_accidental
parent: alto.theory.pitch
api_module: alto.theory.pitch
package: alto.theory
permalink: /api/alto.theory.pitch/function-key_accidental/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def key_accidental(
    letter: int,
    *,
    count: int,
) -> int
```

{% endraw %}{% include api-source.html name="key_accidental" line=674 %}{% raw %}

</div>

Return the accidental a key signature applies to a letter.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `letter` | `int` | An index into `LETTERS` (0 is C, 6 is B). |
| `count` | `int` | The key signature: that many sharps if positive, that many flats if negative. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | 1 if the signature sharpens the letter, -1 if it flattens it, 0 if it leaves it natural. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_accidental(3, count=1)  # F in G major
1
>>> key_accidental(6, count=-1)  # B in F major
-1
>>> key_accidental(0, count=1)  # C in G major
0
```
{% endraw %}
