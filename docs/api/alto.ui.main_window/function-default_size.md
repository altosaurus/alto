---
title: default_size
parent: alto.ui.main_window
api_module: alto.ui.main_window
package: alto.ui
permalink: /api/alto.ui.main_window/function-default_size/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def default_size() -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="default_size" line=150 %}{% raw %}

</div>

Return the size a new window opens at.

It is big enough for a lesson step, with its circle, to show without
scrolling, but never more than most of the screen.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (int, int)` | The width and height in pixels. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> width, height = default_size()
>>> 0 < width <= DEFAULT_WIDTH and 0 < height <= DEFAULT_HEIGHT
True
```
{% endraw %}
