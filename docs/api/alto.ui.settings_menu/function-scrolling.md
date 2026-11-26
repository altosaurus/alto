---
title: scrolling
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-scrolling/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def scrolling(body: QWidget) -> QScrollArea
```

{% endraw %}{% include api-source.html name="scrolling" line=3012 %}{% raw %}

</div>

Put a page's body in a scroll area, so a long page scrolls inside
the pane and never makes the window taller.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `body` | `QWidget` | What the page shows. |

**Returns**

| Type | Description |
| --- | --- |
| `QScrollArea` | The scroll area that holds it, with no frame and no sideways scrolling. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = QWidget()
>>> scrolling(page).widget() is page
True
```
{% endraw %}
