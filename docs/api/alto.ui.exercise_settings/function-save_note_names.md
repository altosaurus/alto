---
title: save_note_names
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_note_names/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_note_names() -> None
```

{% endraw %}{% include api-source.html name="save_note_names" line=124 %}{% raw %}

</div>

Save the note identification settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg_ = settings.note_names
>>> cfg_.naming = "solfege"
>>> save_note_names()
>>> str(store().value("noteNames/naming"))
'solfege'
>>> cfg_.naming = "letters"
>>> save_note_names()
```
{% endraw %}
