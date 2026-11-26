---
title: upsert_user_theme
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-upsert_user_theme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def upsert_user_theme(record: ThemeRecord) -> None
```

{% endraw %}{% include api-source.html name="upsert_user_theme" line=645 %}{% raw %}

</div>

Save a theme the user made, replacing the one with the same key if
there is one.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `record` | `ThemeRecord` | The theme. |

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
>>> upsert_user_theme(
...     ThemeRecord(
...         id="my_a",
...         name="Renamed",
...         light=colors,
...         dark=colors,
...     )
... )
>>> [
...     (r["id"], r["name"])
...     for r in user_records()
... ]
[('my_a', 'Renamed')]
>>> store().remove("ui/userThemes")
```
{% endraw %}
