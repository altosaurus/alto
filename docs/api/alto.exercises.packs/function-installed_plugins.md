---
title: installed_plugins
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/function-installed_plugins/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def installed_plugins(folder: Path) -> tuple[list[InstalledPlugin], list[str]]
```

{% endraw %}{% include api-source.html name="installed_plugins" line=1895 %}{% raw %}

</div>

List the packs in the plugins folder, including damaged ones, so
each can be removed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `folder` | `Path` | The plugins directory. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of list of InstalledPlugin and list of str` | The packs in discovery order, and any discovery errors. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> installed_plugins(
...     Path("no-such-plugins-folder")
... )
([], [])
```
{% endraw %}
