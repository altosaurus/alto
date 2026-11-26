---
title: beat_meter
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/function-beat_meter/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def beat_meter(answer: str) -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="beat_meter" line=5406 %}{% raw %}

</div>

Look up the written time signature for either kind of answer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `answer` | `str` | A time signature or meter classification from the exercise. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of int` | Numerator and denominator for engraving the rhythm. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> beat_meter("Compound duple")
(6, 8)
```
{% endraw %}
