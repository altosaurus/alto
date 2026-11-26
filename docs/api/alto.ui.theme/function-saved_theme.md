---
title: saved_theme
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-saved_theme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def saved_theme() -> str
```

{% endraw %}{% include api-source.html name="saved_theme" line=1029 %}{% raw %}

</div>

Return the theme the user chose.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The key of the theme: "system", "light", "dark" or one of the themes with colors of its own; "system" if nothing valid is saved. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_theme("dark")
>>> saved_theme()
'dark'
>>> save_theme("system")
```
{% endraw %}
