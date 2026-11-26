---
title: settings_panel_for
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/function-settings_panel_for/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def settings_panel_for(
    exercise: Exercise,
    *,
    learner: Learner | None = None,
) -> ExerciseSettingsPanel
```

{% endraw %}{% include api-source.html name="settings_panel_for" line=3841 %}{% raw %}

</div>

Return the settings panel for an exercise.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `exercise` | `Exercise` | The exercise. |
| `learner` | `Learner or None` | Profile whose calendar limits can be overridden. |

**Returns**

| Type | Description |
| --- | --- |
| `ExerciseSettingsPanel` | A panel with the exercise options and the shared Next Question setting. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     IntervalNames,
...     NoteNames,
... )
>>> type(
...     settings_panel_for(NoteNames())
... ).__name__
'NoteNameSettingsPanel'
>>> type(
...     settings_panel_for(IntervalNames())
... ).__name__
'IntervalSettingsPanel'
```
{% endraw %}
