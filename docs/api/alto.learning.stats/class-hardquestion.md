---
title: HardQuestion
parent: alto.learning.stats
api_module: alto.learning.stats
package: alto.learning
permalink: /api/alto.learning.stats/class-hardquestion/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
HardQuestion(
    exercise: str,
    *,
    text: str,
    strain: float,
    seen: int,
    wrong: int,
    item_key: str = '',
    payload: str | None = None,
)
```

{% endraw %}{% include api-source.html name="HardQuestion" line=193 %}{% raw %}

</div>

A question that needs practice, for the list on the statistics
screen.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `exercise` | `str` | The exercise's class name. |
| `text` | `str` | A short line saying what the question was.  Keyword-only. |
| `strain` | `float` | How much practice it needs; higher is more. Keyword-only. |
| `seen` | `int` | How many times it was answered. Keyword-only. |
| `wrong` | `int` | How many wrong answers it has had. Keyword-only. |
| `item_key` | `str` | The stored identity used to look up this question's practice history. Keyword-only. |
| `payload` | `str or None` | The saved question as JSON for the preview. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HardQuestion(
...     "NoteNames",
...     text="Treble: G4",
...     strain=4.5,
...     seen=6,
...     wrong=5,
... ).wrong
5
```
{% endraw %}
