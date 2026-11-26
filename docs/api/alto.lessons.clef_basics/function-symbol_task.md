---
title: symbol_task
parent: alto.lessons.clef_basics
api_module: alto.lessons.clef_basics
package: alto.lessons
permalink: /api/alto.lessons.clef_basics/function-symbol_task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def symbol_task(rng: random.Random) -> Task
```

{% endraw %}{% include api-source.html name="symbol_task" line=60 %}{% raw %}

</div>

Ask which of the three symbols a clef is made with.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Chooses the clef. |

**Returns**

| Type | Description |
| --- | --- |
| `Task` | A clef drawn on a staff, and a button for each symbol. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = symbol_task(random.Random(2))
>>> task.correct == CLEF_SYMBOL_NAMES[
...     SYMBOLS[task.clef]
... ]
True
```
{% endraw %}
