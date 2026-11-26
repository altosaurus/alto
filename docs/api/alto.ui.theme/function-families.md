---
title: families
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-families/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def families() -> tuple[tuple[str, str, str], ...]
```

{% endraw %}{% include api-source.html name="families" line=822 %}{% raw %}

</div>

List every theme there is to choose, the user's own first.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of tuple of (str, str, str)` | The key of each theme's family, its name and a line about it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> families() == FAMILIES
True
```
{% endraw %}
