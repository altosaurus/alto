---
title: register
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/function-register/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def register() -> type[Exercise]
```

{% endraw %}{% include api-source.html name="register" line=1687 %}{% raw %}

</div>

Add an exercise to `REGISTRY`, next to the others of its category.

The categories come in the order they first appear, so the home
screen and the exercise list can show each category
once, with all its exercises under it. Used as a class decorator.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cls` | `type of Exercise` | The exercise class. |

**Returns**

| Type | Description |
| --- | --- |
| `type of Exercise` | The same class, so the decorator can be applied to a class definition. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> @register
... class Demo(Exercise):
...     name = "Demo"
...     category = (
...         "A category no other exercise has"
...     )
...
...     def generate(self, rng):
...         return Question(
...             "?", choices=["A"], answer="A"
...         )
>>> REGISTRY[-1] is Demo
True
>>> REGISTRY.remove(Demo)
```
{% endraw %}
