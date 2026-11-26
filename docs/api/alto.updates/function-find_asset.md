---
title: find_asset
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-find_asset/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def find_asset(
    release: Release,
    *,
    name: str,
    base: str = DOWNLOAD_BASE,
) -> Asset | None
```

{% endraw %}{% include api-source.html name="find_asset" line=998 %}{% raw %}

</div>

Find a file of a release by its name, if it is at the address where
a release keeps its files.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `release` | `Release` | The release. |
| `name` | `str` | The file's name. Keyword-only. |
| `base` | `str, default DOWNLOAD_BASE` | What the address must start with. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Asset or None` | The file, or None if the release has none by that name or it is somewhere else. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> files = (
...     Asset("a", url=DOWNLOAD_BASE + "v1/a"),
...     Asset("b", url="https://example.org/b"),
... )
>>> found = find_asset(
...     Release(
...         "1", tag="v1", url="", assets=files
...     ),
...     name="a",
... )
>>> found.name if found else None
'a'
>>> find_asset(
...     Release(
...         "1", tag="v1", url="", assets=files
...     ),
...     name="b",
... ) is None
True
```
{% endraw %}
