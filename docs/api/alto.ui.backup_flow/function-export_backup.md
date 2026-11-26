---
title: export_backup
parent: alto.ui.backup_flow
api_module: alto.ui.backup_flow
package: alto.ui
permalink: /api/alto.ui.backup_flow/function-export_backup/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def export_backup(
    parent: QWidget,
    *,
    db: Database,
) -> Path | None
```

{% endraw %}{% include api-source.html name="export_backup" line=151 %}{% raw %}

</div>

Ask where to save a backup, and write it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | The window the dialogs belong to. |
| `db` | `Database` | The database to back up. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Path or None` | The file that was written, or None if the user canceled or the backup could not be written (which is explained). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> export_backup(
...     QWidget(), db=Database()
... )  # doctest: +SKIP
PosixPath('/home/ada/alto-backup-2026-11-13.altobackup')
```
{% endraw %}
