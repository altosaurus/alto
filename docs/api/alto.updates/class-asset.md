---
title: Asset
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/class-asset/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Asset(
    name: str,
    url: str,
    size: int = 0,
)
```

{% endraw %}{% include api-source.html name="Asset" line=578 %}{% raw %}

</div>

A file of a release: the installer, the tarball, the checksums or
their signature.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `name` | `str` | Its name, such as "alto-0.1.0-linux-x86_64.tar.gz". |
| `url` | `str` | The address it is downloaded from. |
| `size` | `int` | Its size in bytes, as GitHub states it; 0 if it does not. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Asset(
...     "SHA256SUMS",
...     url="https://example.org/s",
...     size=300,
... ).size
300
```
{% endraw %}
