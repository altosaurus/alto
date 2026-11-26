---
title: vertical_scroll_area
parent: alto.ui.widgets
api_module: alto.ui.widgets
package: alto.ui
permalink: /api/alto.ui.widgets/function-vertical_scroll_area/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def vertical_scroll_area(body: QWidget) -> QScrollArea
```

{% endraw %}{% include api-source.html name="vertical_scroll_area" line=48 %}{% raw %}

</div>

Put a resizable widget in a frameless vertical scroll area.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `body` | `QWidget` | Contents of the viewport. |

**Returns**

| Type | Description |
| --- | --- |
| `QScrollArea` | The scroll area containing the body. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> body = QWidget()
>>> scroll = vertical_scroll_area(body)
>>> scroll.widget() is body
True
```
{% endraw %}
