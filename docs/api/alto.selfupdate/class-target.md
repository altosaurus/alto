---
title: Target
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/class-target/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Target(
    system: str,
    folder: Path,
    prefix: Path | None,
)
```

{% endraw %}{% include api-source.html name="Target" line=117 %}{% raw %}

</div>

A packaged copy that can replace itself, and where it is.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `system` | `str` | "linux" or "windows". |
| `folder` | `Path` | The folder the program is in. |
| `prefix` | `Path or None` | On Linux, the folder that holds `opt/alto` and `bin/alto` (`~/.local` by default); None on Windows. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Target(
...     "windows",
...     folder=Path("C:/Alto"),
...     prefix=None,
... ).system
'windows'
```
{% endraw %}
