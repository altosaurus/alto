---
title: blend
parent: alto.ui.colors
api_module: alto.ui.colors
package: alto.ui
permalink: /api/alto.ui.colors/function-blend/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def blend(
    a: QColor,
    *,
    b: QColor,
    t: float,
) -> QColor
```

{% endraw %}{% include api-source.html name="blend" line=22 %}{% raw %}

</div>

Return the color a given fraction of the way from one color to
another.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `a` | `QColor` | The color at 0. |
| `b` | `QColor` | The color at 1. Keyword-only. |
| `t` | `float` | How far from `a` to `b`: 0 is `a`, 1 is `b`, 0.5 is halfway. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QColor` | The blended color. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> blend(
...     QColor("#000000"),
...     b=QColor("#ffffff"),
...     t=0.0,
... ).name()
'#000000'
>>> blend(
...     QColor("#ff0000"),
...     b=QColor("#0000ff"),
...     t=1.0,
... ).name()
'#0000ff'
```
{% endraw %}
