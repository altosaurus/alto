---
title: relative_minor
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-relative_minor/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def relative_minor(name: str) -> str
```

{% endraw %}{% include api-source.html name="relative_minor" line=152 %}{% raw %}

</div>

Return the relative minor of a major key.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | `str` | The major key's name. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The first name of its relative minor, such as "F♯m" for A. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     relative_minor("C"),
...     relative_minor("E♭"),
...     relative_minor("C♯"),
... )
('Am', 'Cm', 'B♭m')
```
{% endraw %}
