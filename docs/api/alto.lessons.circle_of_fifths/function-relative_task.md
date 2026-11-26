---
title: relative_task
parent: alto.lessons.circle_of_fifths
api_module: alto.lessons.circle_of_fifths
package: alto.lessons
permalink: /api/alto.lessons.circle_of_fifths/function-relative_task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def relative_task(rng: random.Random) -> Task
```

{% endraw %}{% include api-source.html name="relative_task" line=266 %}{% raw %}

</div>

Ask for the relative minor of a major key, answered on the circle.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | The random number generator. |

**Returns**

| Type | Description |
| --- | --- |
| `Task` | The question. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = relative_task(random.Random(4))
>>> task.cells <= {
...     ("inner", at) for at in range(12)
... }
True
```
{% endraw %}
