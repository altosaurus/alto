---
title: exercise_icon
parent: alto.ui.home
api_module: alto.ui.home
package: alto.ui
permalink: /api/alto.ui.home/function-exercise_icon/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def exercise_icon(name: str) -> str
```

{% endraw %}{% include api-source.html name="exercise_icon" line=517 %}{% raw %}

</div>

Find the icon for an exercise: the one its plugin supplies, or
Alto's own.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | `str` | The exercise's class name. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | SVG shapes with COLOR where the theme's ink goes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> exercise_icon(
...     "NoteNames"
... ) == icons.EXERCISE_NOTE_NAMES
True
>>> exercise_icon(
...     "pack.nothing.here"
... ) == icons.EXERCISE_NOTE_NAMES
True
```
{% endraw %}
