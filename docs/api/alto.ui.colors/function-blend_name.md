---
title: blend_name
parent: alto.ui.colors
api_module: alto.ui.colors
package: alto.ui
permalink: /api/alto.ui.colors/function-blend_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def blend_name(
    a: QColor,
    *,
    b: QColor,
    t: float,
) -> str
```

{% endraw %}{% include api-source.html name="blend_name" line=69 %}{% raw %}

</div>

Return the hex name of a blended color, for use in a stylesheet.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `a` | `QColor` | The color at 0. |
| `b` | `QColor` | The color at 1. Keyword-only. |
| `t` | `float` | How far from `a` to `b`. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The color as '#rrggbb'. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> blend_name(
...     QColor("#000000"),
...     b=QColor("#ffffff"),
...     t=1.0,
... )
'#ffffff'
```
{% endraw %}
