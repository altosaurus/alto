---
title: note_from
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/function-note_from/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def note_from(v: dict | None) -> Note | None
```

{% endraw %}{% include api-source.html name="note_from" line=978 %}{% raw %}

</div>

Rebuild a note from stored data.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `v` | `dict or None` | A note as the dictionary `to_dict` stores, or None. |

**Returns**

| Type | Description |
| --- | --- |
| `Note or None` | The note, or None if `v` was None. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> note_from(
...     {
...         "octave": 4,
...         "letter": 0,
...         "accidental": 0,
...     }
... )
Note(octave=4, letter=0, accidental=0)
>>> note_from(None) is None
True
```
{% endraw %}
