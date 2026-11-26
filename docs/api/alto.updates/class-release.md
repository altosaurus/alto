---
title: Release
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/class-release/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Release(
    version: str,
    tag: str,
    url: str,
    assets: tuple[Asset, ...] = field(default=()),
)
```

{% endraw %}{% include api-source.html name="Release" line=608 %}{% raw %}

</div>

A release of Alto, as published on GitHub.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `version` | `str` | Its version, such as "0.1.0". |
| `tag` | `str` | The tag it is made from, such as "v0.1.0". |
| `url` | `str` | The page where it and its downloads are. |
| `assets` | `tuple of Asset` | Its files. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Release(
...     "0.1.0",
...     tag="v0.1.0",
...     url="https://example.org/r",
... ).version
'0.1.0'
```
{% endraw %}
