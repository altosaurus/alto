---
title: set_palette_icon
parent: alto.ui.icons
api_module: alto.ui.icons
package: alto.ui
permalink: /api/alto.ui.icons/function-set_palette_icon/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_palette_icon(
    target: QAbstractButton | QAction | QMenu,
    render: Callable[[QPalette], QIcon],
) -> None
```

{% endraw %}{% include api-source.html name="set_palette_icon" line=150 %}{% raw %}

</div>

Assign a native Qt icon and refresh it whenever the application
palette changes.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `target` | `QAbstractButton or QAction or QMenu` | Button, menu, or action to update. |
| `render` | `Callable` | Draws the icon in the supplied palette. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtWidgets import QPushButton
>>> button = QPushButton()
>>> set_palette_icon(
...     button,
...     lambda palette: svg_icon(
...         HELP, color=palette.text().color()
...     ),
... )
>>> button.icon().isNull()
False
```
{% endraw %}
