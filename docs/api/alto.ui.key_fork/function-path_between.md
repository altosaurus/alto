---
title: path_between
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/function-path_between/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def path_between(
    a: int,
    *,
    b: int,
) -> list[QPointF]
```

{% endraw %}{% include api-source.html name="path_between" line=170 %}{% raw %}

</div>

Return the way along the fork from one signature to another.

The circle goes back along the tine it is on, around the U and out
along the other, never across the gap between the tines.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `a` | `int` | The signature to start from. |
| `b` | `int` | The signature to end at. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of QPointF` | The points to pass through, from `a` to `b`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> path_between(2, b=2) == [node_position(2)]
True
>>> path_between(1, b=-1)[0] == node_position(
...     1
... ) and path_between(1, b=-1)[
...     -1
... ] == node_position(-1)
True
>>> any(
...     abs(p.x() - APEX_X) < 1e-9
...     for p in path_between(1, b=-1)
... )  # it goes around the U, through its apex
True
```
{% endraw %}
