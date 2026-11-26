---
title: read_fsrs_card
parent: alto.learning.grading
api_module: alto.learning.grading
package: alto.learning
permalink: /api/alto.learning.grading/function-read_fsrs_card/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_fsrs_card(
    key: str,
    *,
    previous: str | None,
    due: datetime,
) -> Card
```

{% endraw %}{% include api-source.html name="read_fsrs_card" line=300 %}{% raw %}

</div>

Restore a saved FSRS card or start one for the question.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The question's stable card key. |
| `previous` | `str or None` | The saved JSON, if the question has been reviewed. |
| `due` | `datetime` | Initial due time for a new card. |

**Returns**

| Type | Description |
| --- | --- |
| `Card` | The restored or newly scheduled card. |

**Examples**

```text
A new card is due at the time of its first review.
```
{% endraw %}
