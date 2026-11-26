---
title: numeral_chords
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-numeral_chords/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def numeral_chords(place: int) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="numeral_chords" line=217 %}{% raw %}

</div>

Return the six chords of a major key that are on the circle, spelled
as that key spells them.

A wedge with two names, such as D♭ and C♯, is the same chord, but
the key decides which name is right: C♯ is the V of F♯.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `place` | `int` | The key's own place on the circle. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | The chord's name for each numeral, in the order of `NUMERALS`: "G", "Am" and so on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> numeral_chords(0)
{'I': 'C', 'ii': 'Dm', 'iii': 'Em', 'IV': 'F', 'V': 'G', 'vi': 'Am'}
>>> (
...     numeral_chords(6)["V"],
...     numeral_chords(7)["IV"],
... )  # in F♯ major the V is C♯; in D♭ major the IV is G♭
('C♯', 'G♭')
```
{% endraw %}
