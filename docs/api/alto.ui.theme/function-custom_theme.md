---
title: custom_theme
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-custom_theme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def custom_theme(key: str) -> CustomTheme | None
```

{% endraw %}{% include api-source.html name="custom_theme" line=845 %}{% raw %}

</div>

Find a theme with colors of its own, one of the built-in ones or one
the user made.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The theme's key. |

**Returns**

| Type | Description |
| --- | --- |
| `CustomTheme or None` | The theme, or None for "system", "light", "dark" or anything that is not one. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     custom_theme("studio_dark")
...     is CUSTOM_THEMES[1],
...     custom_theme("dark"),
... )
(True, None)
```
{% endraw %}
