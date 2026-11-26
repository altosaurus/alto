---
title: custom_style
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-custom_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def custom_style() -> KeyboardStyle
```

{% endraw %}{% include api-source.html name="custom_style" line=359 %}{% raw %}

</div>

Build the style from the custom colors.

Gradients and outlines are worked out from each part's color.

**Returns**

| Type | Description |
| --- | --- |
| `KeyboardStyle` | The custom style, with the key "custom". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> custom_style().key, custom_style().label
('custom', 'Custom')
```
{% endraw %}
