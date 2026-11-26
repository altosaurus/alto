---
title: colors_of
parent: alto.ui.theme_cards
api_module: alto.ui.theme_cards
package: alto.ui
permalink: /api/alto.ui.theme_cards/function-colors_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def colors_of(key: str) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="colors_of" line=86 %}{% raw %}

</div>

Give the colors of a theme's picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | A theme's key: "light", "dark", or a theme with colors of its own, light or dark. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | The window, panel, outline, text, faint and chosen colors, and a tint for the chosen row. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     colors_of("dark")["window"],
...     colors_of("studio")["window"],
... )
('#2b2b2b', '#eceef1')
```
{% endraw %}
