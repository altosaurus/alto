---
title: symbol_icon
parent: alto.ui.pictures
api_module: alto.ui.pictures
package: alto.ui
permalink: /api/alto.ui.pictures/function-symbol_icon/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def symbol_icon(
    symbol: str,
    *,
    color: QColor,
    height: int = 56,
) -> QIcon
```

{% endraw %}{% include api-source.html name="symbol_icon" line=103 %}{% raw %}

</div>

Draw a clef symbol on its own, without a staff, as an icon.

The G, C and F clefs are drawn the same size as they are on a staff,
so the three look alike beside one another, and centered.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `symbol` | `str` | "G", "C" or "F". |
| `color` | `QColor` | The color to draw it in. Keyword-only. |
| `height` | `int, default 56` | The icon's height in pixels, which is also as wide as it is. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QIcon` | The icon, in the notation font chosen in the settings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> symbol_icon(
...     "F", color=QColor("black")
... ).isNull()
False
```
{% endraw %}
