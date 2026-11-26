---
title: question_circle
parent: alto.ui.circle
api_module: alto.ui.circle
package: alto.ui
permalink: /api/alto.ui.circle/function-question_circle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def question_circle(question: Question) -> FifthsCircle
```

{% endraw %}{% include api-source.html name="question_circle" line=1381 %}{% raw %}

</div>

Build a fixed-size circle for a question preview or export.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The exercise question to display. |

**Returns**

| Type | Description |
| --- | --- |
| `FifthsCircle` | A circle showing the question before revealing its answer. |

**Examples**

```text
The Anki export reveals the answer after saving the front image.
```
{% endraw %}
