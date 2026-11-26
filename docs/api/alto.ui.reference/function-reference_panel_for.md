---
title: reference_panel_for
parent: alto.ui.reference
api_module: alto.ui.reference
package: alto.ui
permalink: /api/alto.ui.reference/function-reference_panel_for/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def reference_panel_for(exercise: Exercise) -> ReferencePanel | ClefReferencePanel | ScaleReferencePanel | NoteReferencePanel | PluginReferencePanel | None
```

{% endraw %}{% include api-source.html name="reference_panel_for" line=1017 %}{% raw %}

</div>

Return the reference pane for an exercise.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `exercise` | `Exercise` | The exercise. |

**Returns**

| Type | Description |
| --- | --- |
| `ReferencePanel or ClefReferencePanel or ScaleReferencePanel or` |  |
| `NoteReferencePanel or None` | The panel, or None for an exercise with nothing to look up. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> (
...     isinstance(
...         reference_panel_for(NoteNames()),
...         NoteReferencePanel,
...     ),
...     reference_panel_for(CircleOfFifths())
...     is not None,
... )
(True, True)
>>> type(
...     reference_panel_for(ClefBasics())
... ).__name__
'ClefReferencePanel'
```
{% endraw %}
