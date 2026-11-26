---
title: fifth_task
parent: alto.lessons.circle_of_fifths
api_module: alto.lessons.circle_of_fifths
package: alto.lessons
permalink: /api/alto.lessons.circle_of_fifths/function-fifth_task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def fifth_task(rng: random.Random) -> Task
```

{% endraw %}{% include api-source.html name="fifth_task" line=110 %}{% raw %}

</div>

Ask for the letter a fifth above a random letter, answered with
buttons.

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
>>> task = fifth_task(random.Random(1))
>>> task.correct in LETTERS and len(
...     task.choices
... ) == 4 and task.correct in task.choices
True
```
{% endraw %}
