---
title: user_themes
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-user_themes/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def user_themes() -> tuple[CustomTheme, ...]
```

{% endraw %}{% include api-source.html name="user_themes" line=784 %}{% raw %}

</div>

Give the themes the user has made, light and dark versions of each.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of CustomTheme` | The light theme and then the dark theme of each record. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> user_themes()
()
```
{% endraw %}
