---
title: lesson_icon
parent: alto.ui.home
api_module: alto.ui.home
package: alto.ui
permalink: /api/alto.ui.home/function-lesson_icon/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def lesson_icon(lesson: Lesson) -> str
```

{% endraw %}{% include api-source.html name="lesson_icon" line=550 %}{% raw %}

</div>

Use the lesson's own icon when present, falling back to its primary
exercise's icon.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `lesson` | `Lesson` | The lesson. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | SVG shapes with COLOR where the theme's ink goes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> lesson_icon(LESSONS[0]) == exercise_icon(
...     LESSONS[0].exercise
... )
True
```
{% endraw %}
