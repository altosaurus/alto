---
title: log_path
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-log_path/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def log_path() -> Path
```

{% endraw %}{% include api-source.html name="log_path" line=653 %}{% raw %}

</div>

Give the file the Linux helper writes to, so that a failed update
can be looked into.

**Returns**

| Type | Description |
| --- | --- |
| `Path` | `update.log` in Alto's folder of the user's cache. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> log_path().name
'update.log'
```
{% endraw %}
