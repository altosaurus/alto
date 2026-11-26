---
title: describe
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/function-describe/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def describe(question: Question) -> str
```

{% endraw %}{% include api-source.html name="describe" line=532 %}{% raw %}

</div>

Return a short line saying what a question was, for the list of
questions that need practice.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | The question to describe. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | What was shown (notes, a key signature or a keyboard key) and, where that does not already say it, the answer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.base import Question
>>> describe(
...     Question(
...         "What type of chord is this?",
...         choices=["major", "minor"],
...         answer="minor",
...     )
... )
'What type of chord is this? → minor'
```
{% endraw %}
