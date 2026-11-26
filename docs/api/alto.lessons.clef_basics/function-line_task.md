---
title: line_task
parent: alto.lessons.clef_basics
api_module: alto.lessons.clef_basics
package: alto.lessons
permalink: /api/alto.lessons.clef_basics/function-line_task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def line_task(rng: random.Random) -> Task
```

{% endraw %}{% include api-source.html name="line_task" line=146 %}{% raw %}

</div>

Ask which line of a blank staff a named clef is written on.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Chooses the clef. |

**Returns**

| Type | Description |
| --- | --- |
| `Task` | A blank staff, and a button for each line. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = line_task(random.Random(4))
>>> task.correct in LINES and task.clef == ""
True
```
{% endraw %}
