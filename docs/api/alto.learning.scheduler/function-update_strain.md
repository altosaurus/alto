---
title: update_strain
parent: alto.learning.scheduler
api_module: alto.learning.scheduler
package: alto.learning
permalink: /api/alto.learning.scheduler/function-update_strain/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def update_strain(
    strain: float,
    *,
    correct: bool,
    attempt_no: int,
    seconds: float,
    par_seconds: float,
) -> float
```

{% endraw %}{% include api-source.html name="update_strain" line=156 %}{% raw %}

</div>

Return the question's strain after one more answer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `strain` | `float` | The strain before this answer. |
| `correct` | `bool` | Whether the answer was right. Keyword-only. |
| `attempt_no` | `int` | 1 for the first answer to this showing of the question, 2 for the second and so on. Keyword-only. |
| `seconds` | `float` | How long the answer took. Only the first attempt's speed matters. Keyword-only. |
| `par_seconds` | `float` | How long a good first answer takes for this exercise. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The new strain, kept between 0 and `STRAIN_MAX`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> update_strain(
...     1.5,
...     correct=False,
...     attempt_no=1,
...     seconds=5.0,
...     par_seconds=5.0,
... )
3.0
>>> round(
...     update_strain(
...         1.5,
...         correct=True,
...         attempt_no=1,
...         seconds=1.0,
...         par_seconds=5.0,
...     ),
...     2,
... )  # right, and quick
0.4
>>> update_strain(
...     5.9,
...     correct=False,
...     attempt_no=1,
...     seconds=5.0,
...     par_seconds=5.0,
... )  # capped
6.0
```
{% endraw %}
