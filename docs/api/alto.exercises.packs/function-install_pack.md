---
title: install_pack
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/function-install_pack/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def install_pack(
    source: Path,
    *,
    folder: Path,
    expected_id: str | None = None,
    replacing: InstalledPlugin | None = None,
) -> str
```

{% endraw %}{% include api-source.html name="install_pack" line=1946 %}{% raw %}

</div>

Validate a copy of the selected ZIP and install it for the next
startup.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `source` | `Path` | The downloaded instrument pack ZIP. |
| `folder` | `Path` | The plugins directory used at startup. |
| `expected_id` | `str or None` | The manifest ID assigned to a registered download. |
| `replacing` | `InstalledPlugin or None` | The previously selected ZIP to replace after validation. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The installed pack's display name. |

**Raises**

- *ValueError*: If the ZIP is invalid or conflicts with an existing installation.
- *OSError*: If the installation cannot be read or written.

**Examples**

```text
Installing a downloaded viola.zip adds both of its exercises on the
next launch.
```
{% endraw %}
