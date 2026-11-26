---
title: save_user_records
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-save_user_records/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_user_records(records: list[ThemeRecord]) -> None
```

{% endraw %}{% include api-source.html name="save_user_records" line=606 %}{% raw %}

</div>

Save the themes the user has made.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `records` | `list of ThemeRecord` | The records, as `user_records` gives them. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_user_records([])
>>> user_records()
[]
```
{% endraw %}
