---
title: note_name
parent: alto.ui.exercise_view
api_module: alto.ui.exercise_view
package: alto.ui
permalink: /api/alto.ui.exercise_view/function-note_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def note_name(
    note: Note,
    *,
    key: int | None = None,
    minor: bool = False,
) -> str
```

{% endraw %}{% include api-source.html name="note_name" line=320 %}{% raw %}

</div>

Return a note's name as it is written, with its octave: F♯4.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note` | The note. |
| `key` | `int or None, default None` | The major key signature for scale degrees. Without a key context, degrees fall back to letter names. Keyword-only. |
| `minor` | `bool, default False` | Use natural minor scale degrees. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The name in the naming the app is set to, then the octave number. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> note_name(Note.parse("F#4"))
'F♯4'
```
{% endraw %}
