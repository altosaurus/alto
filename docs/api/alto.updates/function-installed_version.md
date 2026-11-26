---
title: installed_version
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-installed_version/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def installed_version() -> str
```

{% endraw %}{% include api-source.html name="installed_version" line=718 %}{% raw %}

</div>

Give the version of Alto that is running.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The installed version, or "unknown" if Alto was not installed as a package. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> installed_version().count(".") >= 1
True
```
{% endraw %}
