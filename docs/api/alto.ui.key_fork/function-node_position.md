---
title: node_position
parent: alto.ui.key_fork
api_module: alto.ui.key_fork
package: alto.ui
permalink: /api/alto.ui.key_fork/function-node_position/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def node_position(value: int) -> QPointF
```

{% endraw %}{% include api-source.html name="node_position" line=86 %}{% raw %}

</div>

Return where a signature sits on the fork.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `int` | The signature: that many sharps if positive (top tine), flats if negative (bottom tine), 0 for the stem's end. |

**Returns**

| Type | Description |
| --- | --- |
| `QPointF` | The center of its number, in the widget's coordinates. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> node_position(0).x() < node_position(
...     1
... ).x() < node_position(2).x()
True
>>> node_position(3).y() < node_position(
...     0
... ).y() < node_position(-3).y()
True
```
{% endraw %}
