---
title: NoteReferencePanel
parent: alto.ui.reference
api_module: alto.ui.reference
package: alto.ui
permalink: /api/alto.ui.reference/class-notereferencepanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NoteReferencePanel(exercise: Exercise)
```

{% endraw %}{% include api-source.html name="NoteReferencePanel" line=892 %}{% raw %}

</div>

Bases: `QWidget`

Hints for reading notes or intervals and a link to the associated
lesson.

**Constructor**

Show the hints for the current note exercise.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `exercise` | `Exercise` | The note exercise whose reference was opened. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteReferencePanel(
...     KeyboardNotes()
... ).lesson_button.text()
'New to this? Take the full lesson  →'
```
{% endraw %}
