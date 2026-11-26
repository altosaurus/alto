---
title: load_choice_buttons
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_choice_buttons/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_choice_buttons() -> None
```

{% endraw %}{% include api-source.html name="load_choice_buttons" line=1328 %}{% raw %}

</div>

Restore the independent button preferences for each multiple-choice
exercise.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_choice_buttons()
>>> from alto.exercises.library import NoteNames
>>> NoteNames.button_settings().button_mode in {
...     "all",
...     "limited",
... }
True
```
{% endraw %}
