---
title: new_family_id
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-new_family_id/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def new_family_id() -> str
```

{% endraw %}{% include api-source.html name="new_family_id" line=624 %}{% raw %}

</div>

Make the key for a new theme of the user's.

**Returns**

| Type | Description |
| --- | --- |
| `str` | A key that starts with "my_" and is not one that is in use. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new_family_id().startswith("my_")
True
```
{% endraw %}
