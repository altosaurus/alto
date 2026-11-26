---
title: Scene
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/class-scene/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Scene(
    time: float,
    old: Sequence[Sprite],
    new: Sequence[Sprite],
    direction: int,
)
```

{% endraw %}{% include api-source.html name="Scene" line=116 %}{% raw %}

</div>

What a transition is given at each moment: the time, the two sets of
sprites and the direction.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `time` | `float` | The time since the transition began, in milliseconds. |
| `old` | `sequence of Sprite` | The cards that are leaving. |
| `new` | `sequence of Sprite` | The cards that are arriving. |
| `direction` | `int` | 1 when going toward the lessons, -1 when coming back. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Scene(
...     time=0.0, old=[], new=[], direction=1
... ).direction
1
```
{% endraw %}
