---
title: set_item_icons
parent: alto.ui.icons
api_module: alto.ui.icons
package: alto.ui
permalink: /api/alto.ui.icons/function-set_item_icons/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_item_icons(
    view: QAbstractItemView,
    items: list[tuple[str, Callable[[QIcon], None]]],
) -> None
```

{% endraw %}{% include api-source.html name="set_item_icons" line=236 %}{% raw %}

</div>

Recolor the current rows of a navigation list or tree without
rebuilding it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `view` | `QAbstractItemView` | List or tree supplying the text color and icon size. |
| `items` | `list of tuple` | SVG drawing and icon setter for each row in the current model. |

**Examples**

```text
A category tree keeps its checked and expanded items when the theme
changes.
```
{% endraw %}
