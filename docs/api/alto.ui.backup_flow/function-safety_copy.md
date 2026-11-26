---
title: safety_copy
parent: alto.ui.backup_flow
api_module: alto.ui.backup_flow
package: alto.ui
permalink: /api/alto.ui.backup_flow/function-safety_copy/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def safety_copy(db: Database) -> Path | None
```

{% endraw %}{% include api-source.html name="safety_copy" line=208 %}{% raw %}

</div>

Save a backup of what the database holds now, beside it, before it
is replaced.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `db` | `Database` | The database about to be replaced. |

**Returns**

| Type | Description |
| --- | --- |
| `Path or None` | The file written, or None for a throwaway in-memory database, which has no folder to keep a copy in. |

**Raises**

- *BackupError*: If the copy cannot be written.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> safety_copy(Database()) is None
True
```
{% endraw %}
