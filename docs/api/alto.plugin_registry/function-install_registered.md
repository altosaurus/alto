---
title: install_registered
parent: alto.plugin_registry
api_module: alto.plugin_registry
package: alto
permalink: /api/alto.plugin_registry/function-install_registered/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def install_registered(
    code: str,
    *,
    folder: Path,
    selected: InstalledPlugin | None = None,
) -> str | None
```

{% endraw %}{% include api-source.html name="install_registered" line=131 %}{% raw %}

</div>

Install by registration code, or update a selected ZIP from its
registered repository.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `code` | `str` | The published code, including any leading zeros. Updates recover the code from the installation or its registered pack ID. |
| `folder` | `Path` | The plugins directory. |
| `selected` | `InstalledPlugin or None` | The installed ZIP to update. Editable directories stay under the author's control. |

**Returns**

| Type | Description |
| --- | --- |
| `str or None` | The installed pack name and release tag, or None if the installed ZIP already matches the latest asset. |

**Raises**

- *ValueError*: If registration, release selection, integrity checks, or pack validation fails.
{% endraw %}
