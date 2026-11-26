---
title: pack_manifests
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/function-pack_manifests/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def pack_manifests(folder: Path) -> tuple[list[Path], list[str]]
```

{% endraw %}{% include api-source.html name="pack_manifests" line=1776 %}{% raw %}

</div>

Find each installed ZIP or folder manifest, including packs that
failed validation.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `folder` | `Path` | The plugins directory. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of list of Path and list of str` | ZIP files and pack.json files in discovery order, and any discovery errors. |

**Examples**

```text
An author can install either viola.zip or viola/pack.json.
```
{% endraw %}
