---
title: ItemRecord
parent: alto.learning.database
api_module: alto.learning.database
package: alto.learning
permalink: /api/alto.learning.database/class-itemrecord/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ItemRecord(
    strain: float,
    *,
    seen: int,
    first_try_right: int,
    wrong_attempts: int,
    total_first_ms: int,
    last_seen: float,
    signature: str,
    payload: str,
    item_key: str = '',
)
```

{% endraw %}{% include api-source.html name="ItemRecord" line=316 %}{% raw %}

</div>

What a profile's history says about one question.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `strain` | `float` | How much practice the question needs; higher means it comes back sooner. |
| `seen` | `int` | How many times the question was shown and answered. Keyword-only. |
| `first_try_right` | `int` | How many of those showings were answered right on the first try. Keyword-only. |
| `wrong_attempts` | `int` | How many wrong answers there have been in all. Keyword-only. |
| `total_first_ms` | `int` | Time to the first answer, summed over the showings, in milliseconds. Keyword-only. |
| `last_seen` | `float` | When the question was last answered, as a timestamp. Keyword-only. |
| `signature` | `str` | The exercise settings it was asked under; it is only asked again while these are unchanged. Keyword-only. |
| `payload` | `str` | The question itself as JSON, so it can be asked again. Keyword-only. |
| `item_key` | `str, default ""` | The question's identity. Empty when the record is built to be saved, filled in when it is read back. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> record = ItemRecord(
...     2.0,
...     seen=3,
...     first_try_right=1,
...     wrong_attempts=2,
...     total_first_ms=9000,
...     last_seen=100.0,
...     signature="s",
...     payload="{}",
... )
>>> record.seen
3
```
{% endraw %}
