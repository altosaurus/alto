---
title: identify_task
parent: alto.lessons.clef_basics
api_module: alto.lessons.clef_basics
package: alto.lessons
permalink: /api/alto.lessons.clef_basics/function-identify_task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def identify_task(rng: random.Random) -> Task
```

{% endraw %}{% include api-source.html name="identify_task" line=103 %}{% raw %}

</div>

Ask which clef is drawn on a staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Chooses the clef. |

**Returns**

| Type | Description |
| --- | --- |
| `Task` | A clef drawn on a staff, and a button for each of the four everyday clefs. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = identify_task(random.Random(3))
>>> task.correct in task.choices and task.clef != ""
True
```
{% endraw %}
