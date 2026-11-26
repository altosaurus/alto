---
title: navigation_heading_style
parent: alto.ui.style
api_module: alto.ui.style
package: alto.ui
permalink: /api/alto.ui.style/function-navigation_heading_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def navigation_heading_style(palette: QPalette) -> tuple[QFont, QColor]
```

{% endraw %}{% include api-source.html name="navigation_heading_style" line=22 %}{% raw %}

</div>

Style category headings in the navigation pane and tile filters.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `palette` | `QPalette` | The pane's current palette. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of QFont and QColor` | The small, spaced capitals and muted foreground used for section headings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> navigation_heading_style(QPalette())[
...     0
... ].bold()
True
```
{% endraw %}
