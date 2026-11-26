---
title: delete_user_theme
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-delete_user_theme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def delete_user_theme(family: str) -> None
```

{% endraw %}{% include api-source.html name="delete_user_theme" line=698 %}{% raw %}

</div>

Remove a theme the user made.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `family` | `str` | The theme's key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> colors = {part: "#112233" for part in PARTS}
>>> upsert_user_theme(
...     ThemeRecord(
...         id="my_a",
...         name="Mine",
...         light=colors,
...         dark=colors,
...     )
... )
>>> delete_user_theme("my_a")
>>> user_records()
[]
```
{% endraw %}
