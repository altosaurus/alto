---
title: user_records
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-user_records/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def user_records() -> list[ThemeRecord]
```

{% endraw %}{% include api-source.html name="user_records" line=576 %}{% raw %}

</div>

Read the themes the user has made, as they are saved.

**Returns**

| Type | Description |
| --- | --- |
| `list of ThemeRecord` | One record for each theme: its "id", its "name", and its "light" and "dark" colors. A saved list that cannot be read, or has something else in it, gives only the records that can be used. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> user_records()
[]
```
{% endraw %}
