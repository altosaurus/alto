---
title: installed_pack_info
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/function-installed_pack_info/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def installed_pack_info(path: Path) -> dict
```

{% endraw %}{% include api-source.html name="installed_pack_info" line=1818 %}{% raw %}

</div>

Read a pack's manifest for display or duplicate detection without
loading its media.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `path` | `Path` | An installed ZIP or an editable pack.json. |

**Returns**

| Type | Description |
| --- | --- |
| `dict` | The manifest, or an empty dictionary for an invalid manifest or archive. |

**Examples**

```text
A damaged pack can still be listed for removal by filename.
```
{% endraw %}
