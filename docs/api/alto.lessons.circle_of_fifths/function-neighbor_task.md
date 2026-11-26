---
title: neighbor_task
parent: alto.lessons.circle_of_fifths
api_module: alto.lessons.circle_of_fifths
package: alto.lessons
permalink: /api/alto.lessons.circle_of_fifths/function-neighbor_task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def neighbor_task(rng: random.Random) -> Task
```

{% endraw %}{% include api-source.html name="neighbor_task" line=314 %}{% raw %}

</div>

Ask for the key a fifth above or below a random key, answered on the
circle.

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
>>> task = neighbor_task(random.Random(5))
>>> ring, at = next(iter(task.cells))
>>> ring, at in range(12)
('outer', True)
```
{% endraw %}
