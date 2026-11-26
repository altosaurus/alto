---
title: short
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-short/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def short(commit: str) -> str
```

{% endraw %}{% include api-source.html name="short" line=129 %}{% raw %}

</div>

Shorten a commit id to the seven characters people use for it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `commit` | `str` | The full commit id. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Its first seven characters. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> short(
...     "b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe"
... )
'b6e2091'
```
{% endraw %}
