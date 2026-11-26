---
title: set_style
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/function-set_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_style(key: str) -> None
```

{% endraw %}{% include api-source.html name="set_style" line=274 %}{% raw %}

</div>

Choose and save a style, and redraw every staff already on screen.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | A key of `BY_KEY`; an unknown key gives the default. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_style("leland")
>>> current().label
'Leland'
>>> set_style(DEFAULT)
```
{% endraw %}
