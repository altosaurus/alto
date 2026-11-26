---
title: svg_icon
parent: alto.ui.icons
api_module: alto.ui.icons
package: alto.ui
permalink: /api/alto.ui.icons/function-svg_icon/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def svg_icon(
    inner: str,
    *,
    color: QColor,
    size: int = 24,
    scale: float = 2.0,
) -> QIcon
```

{% endraw %}{% include api-source.html name="svg_icon" line=286 %}{% raw %}

</div>

Render 24 by 24 SVG shapes into a crisp icon.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `inner` | `str` | The SVG shapes, using COLOR wherever the color goes. |
| `color` | `QColor` | The color to draw in. Keyword-only. |
| `size` | `int, default 24` | The icon's size in logical pixels. Keyword-only. |
| `scale` | `float, default 2.0` | How many device pixels to render per logical pixel, so it stays sharp on high-resolution screens. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QIcon` | The icon. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> icon = svg_icon(
...     PLAY, color=QColor("#336699"), size=16
... )
>>> icon.isNull()
False
```
{% endraw %}
