---
title: ThemeRecord
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/class-themerecord/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ThemeRecord(TypedDict)
```

{% endraw %}{% include api-source.html name="ThemeRecord" line=496 %}{% raw %}

</div>

A theme the user made, as it is saved: its key, its name, and the
colors of its light and dark versions.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ThemeRecord(
...     id="my_1",
...     name="Mine",
...     light={},
...     dark={},
... )["name"]
'Mine'
```
{% endraw %}
