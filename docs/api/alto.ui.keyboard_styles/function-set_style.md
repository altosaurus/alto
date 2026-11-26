---
title: set_style
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-set_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_style(key: str) -> None
```

{% endraw %}{% include api-source.html name="set_style" line=464 %}{% raw %}

</div>

Choose and save a style, and redraw every keyboard already on
screen.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | A key of `BY_KEY`, or "custom". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_style("modern")
>>> current().label
'Modern piano'
>>> set_style(DEFAULT)
```
{% endraw %}
