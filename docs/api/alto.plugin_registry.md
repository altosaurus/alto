---
title: alto.plugin_registry
parent: api
package: alto
permalink: /api/alto.plugin_registry/
---
{% raw %}
Install registered instrument packs from the latest release in their
public GitHub repositories.

## install_registered

```python
def install_registered(
    code: str,
    *,
    folder: Path,
    selected: InstalledPlugin | None = None,
) -> str | None
```

Install by registration code, or update a selected ZIP from its
registered repository.

**Parameters**

- `code` (*str*): The published code, including any leading zeros. Updates recover the code from the installation or its registered pack ID.
- `folder` (*Path*): The plugins directory.
- `selected` (*InstalledPlugin or None*): The installed ZIP to update. Editable directories stay under the author's control.

**Returns**

- *str or None*: The installed pack name and release tag, or None if the installed ZIP already matches the latest asset.

**Raises**

- *ValueError*: If registration, release selection, integrity checks, or pack validation fails.
{% endraw %}
