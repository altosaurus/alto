---
title: InstallKind
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/class-installkind/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class InstallKind(Enum)
```

{% endraw %}{% include api-source.html name="InstallKind" line=270 %}{% raw %}

</div>

How the running copy of Alto got where it is, which decides how it
can be updated.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `SCRIPT` | `InstallKind` | Installed with `scripts/alto-install.sh`: it can replace itself, from a release or from the main branch. |
| `PACKAGE` | `InstallKind` | A packaged build (a tarball or the Windows installer): it can only be told that a newer release exists. |
| `OTHER` | `InstallKind` | Installed from a git address some other way, so there is no `uv tool` to update it with. |
| `SOURCE` | `InstallKind` | Run from a source folder, which is updated with git. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> InstallKind.SCRIPT.name
'SCRIPT'
```
{% endraw %}
