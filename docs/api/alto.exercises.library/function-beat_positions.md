---
title: beat_positions
parent: alto.exercises.library
api_module: alto.exercises.library
package: alto.exercises
permalink: /api/alto.exercises.library/function-beat_positions/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def beat_positions(meter: tuple[int, int]) -> frozenset[int]
```

{% endraw %}{% include api-source.html name="beat_positions" line=5841 %}{% raw %}

</div>

Get the main beat starts in two measures, measured in eighth notes.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `meter` | `tuple of int` | One of the supported time signatures. |

**Returns**

| Type | Description |
| --- | --- |
| `frozenset of int` | Zero-based positions from the start of the first measure. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sorted(beat_positions((6, 8)))
[0, 3, 6, 9]
```
{% endraw %}
