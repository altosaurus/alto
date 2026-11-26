---
title: display_major
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-display_major/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def display_major(place: int) -> str
```

{% endraw %}{% include api-source.html name="display_major" line=258 %}{% raw %}

</div>

Return the major key of a place as it is written to ask about it: "A
major", or "B major / C♭ major".

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `place` | `int` | The place on the circle. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The name, with both names when the wedge has two. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> display_major(3), display_major(5)
('A major', 'B major / C♭ major')
```
{% endraw %}
