---
title: custom_colors
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-custom_colors/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def custom_colors() -> dict[str, str | None]
```

{% endraw %}{% include api-source.html name="custom_colors" line=341 %}{% raw %}

</div>

Return the color of each part of the custom keyboard.

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str or None` | Part name ("naturals", "sharps", "case", "felt" or "caps") to its color, or None where an optional part is left out. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sorted(custom_colors())
['caps', 'case', 'felt', 'naturals', 'sharps']
```
{% endraw %}
