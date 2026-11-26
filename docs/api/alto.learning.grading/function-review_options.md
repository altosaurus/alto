---
title: review_options
parent: alto.learning.grading
api_module: alto.learning.grading
package: alto.learning
permalink: /api/alto.learning.grading/function-review_options/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def review_options(
    key: str,
    *,
    mode: str,
    previous: str | None,
    due: float,
    now: float,
) -> dict[Rating, tuple[int, str]]
```

{% endraw %}{% include api-source.html name="review_options" line=409 %}{% raw %}

</div>

Calculate a consistent set of answer-button intervals from one
scheduling state.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | Card identity. |
| `mode` | `str` | SM-2 or FSRS. |
| `previous` | `str or None` | Schedule before this answer. |
| `due` | `float` | Due timestamp of the previous schedule. |
| `now` | `float` | Time of the answer. |

**Returns**

| Type | Description |
| --- | --- |
| `dict` | Delay in seconds and serialized successor state for each grade. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> review_options(
...     "abc",
...     mode="SM-2",
...     previous=None,
...     due=0,
...     now=0,
... )[Rating.Again][0]
60
```
{% endraw %}
