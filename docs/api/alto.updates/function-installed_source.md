---
title: installed_source
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-installed_source/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def installed_source() -> Source | None
```

{% endraw %}{% include api-source.html name="installed_source" line=217 %}{% raw %}

</div>

Say where the Alto that is running was installed from.

**Returns**

| Type | Description |
| --- | --- |
| `Source or None` | Its git address and commit, or None if it was not installed from a git address. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> source = installed_source()
>>> source is None or len(
...     source.commit
... ) == COMMIT_LENGTH
True
```
{% endraw %}
