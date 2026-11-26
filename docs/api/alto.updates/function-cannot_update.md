---
title: cannot_update
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-cannot_update/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def cannot_update(kind: InstallKind) -> str | None
```

{% endraw %}{% include api-source.html name="cannot_update" line=375 %}{% raw %}

</div>

Say why a kind of copy cannot update itself at all, if it cannot.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `kind` | `InstallKind` | The kind of copy. |

**Returns**

| Type | Description |
| --- | --- |
| `str or None` | A sentence for a copy run from a source folder or installed some other way; None for one that can be told about updates. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     cannot_update(InstallKind.SOURCE)
...     == SOURCE_FOLDER,
...     cannot_update(InstallKind.OTHER)
...     == NOT_BY_SCRIPT,
... )
(True, True)
>>> cannot_update(
...     InstallKind.SCRIPT
... ) is None and cannot_update(
...     InstallKind.PACKAGE
... ) is None
True
```
{% endraw %}
