---
title: PracticeComplete
parent: alto.learning.learner
api_module: alto.learning.learner
package: alto.learning
permalink: /api/alto.learning.learner/class-practicecomplete/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PracticeComplete(retry_at: float | None = None)
```

{% endraw %}{% include api-source.html name="PracticeComplete" line=51 %}{% raw %}

</div>

Bases: `Exception`

The current exercise has no scheduled cards available.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> issubclass(PracticeComplete, Exception)
True
```

**Constructor**

Carry the next missed card's due time to the exercise screen.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `retry_at` | `float or None` | Scheduled timestamp, or None when practice is finished for now. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PracticeComplete().retry_at is None
True
```
{% endraw %}
