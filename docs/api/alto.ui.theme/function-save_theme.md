---
title: save_theme
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-save_theme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="save_theme" line=1051 %}{% raw %}

</div>

Remember the theme the user chose.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | "system", "light", "dark" or the key of a theme with colors of its own. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_theme("light")
>>> saved_theme()
'light'
>>> save_theme("system")
```
{% endraw %}
