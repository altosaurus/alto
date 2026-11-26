---
title: current
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-current/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def current() -> KeyboardStyle
```

{% endraw %}{% include api-source.html name="current" line=418 %}{% raw %}

</div>

Return the keyboard style in use.

**Returns**

| Type | Description |
| --- | --- |
| `KeyboardStyle` | The style chosen in the settings (Classic until another is chosen). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> current().key in BY_KEY or current().key == CUSTOM
True
```
{% endraw %}
