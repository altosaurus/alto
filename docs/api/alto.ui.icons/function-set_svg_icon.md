---
title: set_svg_icon
parent: alto.ui.icons
api_module: alto.ui.icons
package: alto.ui
permalink: /api/alto.ui.icons/function-set_svg_icon/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_svg_icon(
    target: QAbstractButton | QAction | QMenu,
    inner: str,
    *,
    role: QPalette.ColorRole = QPalette.ColorRole.WindowText,
    size: int = 24,
) -> None
```

{% endraw %}{% include api-source.html name="set_svg_icon" line=200 %}{% raw %}

</div>

Tint an SVG icon with the control's current foreground or accent
color.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `target` | `QAbstractButton or QAction or QMenu` | Control that displays the icon. |
| `inner` | `str` | SVG shapes using COLOR for the ink. |
| `role` | `QPalette.ColorRole, default WindowText` | Color to take from the application palette. |
| `size` | `int, default 24` | Logical size in pixels. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtWidgets import QPushButton
>>> button = QPushButton()
>>> set_svg_icon(button, HELP)
>>> button.icon().isNull()
False
```
{% endraw %}
