---
title: save_step
parent: alto.ui.lesson
api_module: alto.ui.lesson
package: alto.ui
permalink: /api/alto.ui.lesson/function-save_step/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_step(
    lesson: Lesson,
    *,
    step: int,
) -> None
```

{% endraw %}{% include api-source.html name="save_step" line=106 %}{% raw %}

</div>

Remember the step a lesson is at.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `lesson` | `Lesson` | The lesson. |
| `step` | `int` | The step number from 0. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_step(LESSONS[0], step=0)
>>> saved_step(LESSONS[0])
0
```
{% endraw %}
