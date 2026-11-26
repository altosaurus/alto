---
title: summary
parent: alto.lessons.circle_of_fifths
api_module: alto.lessons.circle_of_fifths
package: alto.lessons
permalink: /api/alto.lessons.circle_of_fifths/function-summary/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def summary(
    ring: str,
    *,
    place: int,
) -> str
```

{% endraw %}{% include api-source.html name="summary" line=68 %}{% raw %}

</div>

Say a key and its key signature in one line.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ring` | `str` | "outer" or "inner". |
| `place` | `int` | The place on the circle. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML such as "<b>A major</b>: 3 sharps (F♯, C♯, G♯)". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     summary("outer", place=0),
...     summary("inner", place=11),
... )
('<b>C major</b>: no sharps or flats', '<b>D minor</b>: 1 flat
(B♭)')
```
{% endraw %}
