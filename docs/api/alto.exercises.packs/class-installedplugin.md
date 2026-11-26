---
title: InstalledPlugin
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/class-installedplugin/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
InstalledPlugin(
    title: str,
    path: Path,
    manifest: Path,
    snapshot: stat_result,
)
```

{% endraw %}{% include api-source.html name="InstalledPlugin" line=1857 %}{% raw %}

</div>

One pack in the plugins folder, as listed for removal.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `title` | `str` | The pack's name, or its file name without the .zip extension when the manifest cannot be read. |
| `path` | `Path` | The ZIP file or editable pack folder that removal moves to the trash. |
| `manifest` | `Path` | The ZIP or the folder's pack.json. |
| `snapshot` | `stat_result` | The state of ``path`` when it was listed, used to notice a change before removal. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> import os
>>> plugin = InstalledPlugin(
...     title="Viola",
...     path=Path("viola.zip"),
...     manifest=Path("viola.zip"),
...     snapshot=os.stat("."),
... )
>>> plugin.title
'Viola'
```
{% endraw %}
