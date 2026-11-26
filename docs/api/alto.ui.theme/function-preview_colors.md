---
title: preview_colors
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-preview_colors/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def preview_colors(theme: CustomTheme) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="preview_colors" line=917 %}{% raw %}

</div>

Pick the colors for the small picture of a theme in the settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `theme` | `CustomTheme` | The theme. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | The window, panel, outline, text, faint and chosen colors, and a tint for the chosen row. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     preview_colors(CUSTOM_THEMES[0])[
...         "window"
...     ],
...     sorted(
...         preview_colors(CUSTOM_THEMES[0])
...     )[:3],
... )
('#eceef1', ['accent', 'faint', 'ink'])
```
{% endraw %}
