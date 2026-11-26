---
title: display_minor
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-display_minor/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def display_minor(place: int) -> str
```

{% endraw %}{% include api-source.html name="display_minor" line=281 %}{% raw %}

</div>

Return the minor key of a place as it is written to ask about it:
"F♯ minor", or "G♯ minor / A♭ minor".

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
>>> display_minor(3), display_minor(5)
('F♯ minor', 'G♯ minor / A♭ minor')
```
{% endraw %}
