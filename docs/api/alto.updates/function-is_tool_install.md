---
title: is_tool_install
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-is_tool_install/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def is_tool_install(
    *,
    prefix: Path | None = None,
) -> bool
```

{% endraw %}{% include api-source.html name="is_tool_install" line=243 %}{% raw %}

</div>

Say whether Alto is running from an environment that `uv tool` made,
which is what the install script makes.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `prefix` | `Path or None, default None` | The environment to look at; the one that is running if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the environment has the receipt that `uv tool install` leaves in it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> is_tool_install(prefix=Path("/nowhere"))
False
```
{% endraw %}
