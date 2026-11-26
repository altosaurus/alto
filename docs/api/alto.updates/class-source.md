---
title: Source
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/class-source/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Source(
    url: str,
    commit: str,
    ref: str = 'HEAD',
)
```

{% endraw %}{% include api-source.html name="Source" line=101 %}{% raw %}

</div>

Where an installed copy of Alto came from.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `url` | `str` | The git address it was installed from. |
| `commit` | `str` | The commit it was built from. |
| `ref` | `str` | The branch or tag it follows; "HEAD", the address's default branch, unless the install named one. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Source(
...     "https://github.com/altosaurus/alto.git",
...     commit="b6e2091",
... ).ref
'HEAD'
```
{% endraw %}
