---
title: load_style
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-load_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_style() -> None
```

{% endraw %}{% include api-source.html name="load_style" line=436 %}{% raw %}

</div>

Apply the saved style (Classic if none is saved or it is unknown),
and the saved custom colors.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue("ui/keyboard", "modern")
>>> load_style()
>>> current().key
'modern'
>>> set_style(DEFAULT)
```
{% endraw %}
