---
title: place_of_major
parent: alto.theory.fifths
api_module: alto.theory.fifths
package: alto.theory
permalink: /api/alto.theory.fifths/function-place_of_major/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def place_of_major(name: str) -> int
```

{% endraw %}{% include api-source.html name="place_of_major" line=118 %}{% raw %}

</div>

Return where a major key is on the circle, by either of its names.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | `str` | The key's name, such as "A", "B♭" or "C♭". |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The place, clockwise from C at 0. |

**Raises**

- *ValueError*: If no key has that name.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     place_of_major("A"),
...     place_of_major("C♭"),
...     place_of_major("G♭"),
... )
(3, 5, 6)
```
{% endraw %}
