---
title: route
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/function-route/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def route(value: int) -> list[QPointF]
```

{% endraw %}{% include api-source.html name="route" line=120 %}{% raw %}

</div>

Return the way along the fork from the end of the stem to a
signature.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `int` | The signature, as for `node_position`. |

**Returns**

| Type | Description |
| --- | --- |
| `list of QPointF` | The points to pass through: the stem's end, around the bend of the U to the tine and then each number up to the one asked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     len(route(0)),
...     len(route(2))
...     > len(route(1))
...     > len(route(0)),
... )
(1, True)
>>> route(-1)[-1] == node_position(-1)
True
>>> round(route(3)[1].x()) == round(
...     APEX_X
... )  # it leaves the stem at the apex of the U
True
```
{% endraw %}
