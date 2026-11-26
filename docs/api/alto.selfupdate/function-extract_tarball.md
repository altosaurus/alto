---
title: extract_tarball
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-extract_tarball/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def extract_tarball(
    archive: Path,
    *,
    destination: Path,
) -> Path
```

{% endraw %}{% include api-source.html name="extract_tarball" line=359 %}{% raw %}

</div>

Unpack the Linux download, refusing anything that would land outside
the folder.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `archive` | `Path` | The `.tar.gz`. |
| `destination` | `Path` | The folder to unpack it in. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Path` | The one folder the download unpacks to, which holds `install.sh` and the program. |

**Raises**

- *UpdateError*: If it cannot be unpacked safely, or is not what an update needs.
{% endraw %}
