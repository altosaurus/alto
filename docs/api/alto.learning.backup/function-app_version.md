---
title: app_version
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/function-app_version/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def app_version() -> str
```

{% endraw %}{% include api-source.html name="app_version" line=150 %}{% raw %}

</div>

Return the version of Alto that is running.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The installed version, or "unknown" if Alto was not installed as a package. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> app_version().count(".") >= 1
True
```
{% endraw %}
