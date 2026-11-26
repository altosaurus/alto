---
title: Transition
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/class-transition/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Transition(
    key: str,
    label: str,
    about: str,
    frame: Callable[[Scene], None] | None = field(default=None, compare=False),
    length: Callable[[Scene], float] = field(default=lambda scene: 0.0, compare=False),
)
```

{% endraw %}{% include api-source.html name="Transition" line=590 %}{% raw %}

</div>

One way of moving between the exercises and the lessons.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `key` | `str` | What it is saved as. |
| `label` | `str` | What the settings call it. |
| `about` | `str` | A sentence saying what it looks like. |
| `frame` | `callable or None` | Sets how every sprite looks in a scene; None for no transition at all. |
| `length` | `callable` | Says how long it lasts, in milliseconds, from a scene that has the cards but no time. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> TRANSITIONS[0].frame is None
True
```
{% endraw %}
