---
title: key_name
parent: alto.lessons.circle_of_fifths
api_module: alto.lessons.circle_of_fifths
package: alto.lessons
permalink: /api/alto.lessons.circle_of_fifths/function-key_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def key_name(
    ring: str,
    *,
    place: int,
) -> str
```

{% endraw %}{% include api-source.html name="key_name" line=37 %}{% raw %}

</div>

Return the first name of the key in a cell, written out.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ring` | `str` | "outer" for the major key, "inner" for the minor. |
| `place` | `int` | The place on the circle, clockwise from the top. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | "G major" or "E minor". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     key_name("outer", place=1),
...     key_name("inner", place=1),
... )
('G major', 'E minor')
```
{% endraw %}
