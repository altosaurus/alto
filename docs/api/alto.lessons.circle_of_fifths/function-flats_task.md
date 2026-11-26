---
title: flats_task
parent: alto.lessons.circle_of_fifths
api_module: alto.lessons.circle_of_fifths
package: alto.lessons
permalink: /api/alto.lessons.circle_of_fifths/function-flats_task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def flats_task(rng: random.Random) -> Task
```

{% endraw %}{% include api-source.html name="flats_task" line=213 %}{% raw %}

</div>

Ask for the major key with a given number of flats, answered on the
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
>>> task = flats_task(random.Random(3))
>>> ring, at = next(iter(task.cells))
>>> (
...     ring,
...     -SIGNATURES[at]
...     == int(
...         task.prompt.split("<b>")[1].split()[
...             0
...         ]
...     ),
... )
('outer', True)
```
{% endraw %}
