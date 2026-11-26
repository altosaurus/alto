---
title: signature_of
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-signature_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def signature_of(place: int) -> int
```

{% endraw %}{% include api-source.html name="signature_of" line=324 %}{% raw %}

</div>

Return how far a place is from C, with flats as negative: the key
signature of the major key there.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `place` | `int` | The place clockwise from the top, 0 to 11. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | From -5 (five flats) to 6 (six sharps). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [
...     signature_of(at)
...     for at in (0, 1, 6, 7, 11)
... ]
[0, 1, 6, -5, -1]
```
{% endraw %}
