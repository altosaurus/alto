---
title: theme_palette
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-theme_palette/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def theme_palette(theme: CustomTheme) -> QPalette
```

{% endraw %}{% include api-source.html name="theme_palette" line=956 %}{% raw %}

</div>

Build the Qt palette of a theme with colors of its own.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `theme` | `CustomTheme` | The theme. |

**Returns**

| Type | Description |
| --- | --- |
| `QPalette` | The palette: the window, lists and buttons, text, the chosen row and links in the theme's colors, with quiet text for what is switched off. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> colors = theme_palette(CUSTOM_THEMES[0])
>>> (
...     colors.color(
...         QPalette.ColorRole.Window
...     ).name(),
...     colors.color(
...         QPalette.ColorRole.Highlight
...     ).name(),
... )
('#eceef1', '#2f7fc1')
```
{% endraw %}
