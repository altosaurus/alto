---
title: Sm2State
parent: alto.learning.grading
api_module: alto.learning.grading
package: alto.learning
permalink: /api/alto.learning.grading/class-sm2state/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Sm2State(
    repetitions: int = 0,
    interval: int = 0,
    ease: float = 2.5,
    phase: str = 'learning',
    step: int = 0,
    delay: int = 0,
)
```

{% endraw %}{% include api-source.html name="Sm2State" line=61 %}{% raw %}

</div>

SM-2 learning step, review history, and actual delay for the current
presentation.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sm2State.read(None).phase
'learning'
```

## Sm2State.read

<div class="api-signature" markdown="1">

```python
@classmethod
def read(previous: str | None) -> Sm2State
```

{% endraw %}{% include api-source.html name="Sm2State.read" line=80 %}{% raw %}

</div>

Read a button-graded or original automatic SM-2 schedule.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `previous` | `str or None` | Serialized schedule, if this card has been graded. |

**Returns**

| Type | Description |
| --- | --- |
| `Sm2State` | Card state with the existing interval and ease preserved. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sm2State.read("[2, 6, 2.5]").phase
'review'
```
{% endraw %}
