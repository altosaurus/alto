---
title: saved_step
parent: alto.ui.lesson
api_module: alto.ui.lesson
package: alto.ui
permalink: /api/alto.ui.lesson/function-saved_step/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def saved_step(lesson: Lesson) -> int
```

{% endraw %}{% include api-source.html name="saved_step" line=80 %}{% raw %}

</div>

Return the step a lesson was left at, from the saved settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `lesson` | `Lesson` | The lesson. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The step number from 0, or 0 if none is saved or it no longer exists. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> saved_step(LESSONS[0]) in range(
...     len(LESSONS[0].steps)
... )
True
```
{% endraw %}
