---
title: is_frozen
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-is_frozen/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def is_frozen() -> bool
```

{% endraw %}{% include api-source.html name="is_frozen" line=301 %}{% raw %}

</div>

Say whether Alto is running as a packaged build, made with
PyInstaller, rather than from Python.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True for a packaged build. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> is_frozen()
False
```
{% endraw %}
