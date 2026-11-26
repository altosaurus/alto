---
title: import_backup
parent: alto.ui.backup_flow
api_module: alto.ui.backup_flow
package: alto.ui
permalink: /api/alto.ui.backup_flow/function-import_backup/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def import_backup(
    parent: QWidget,
    *,
    db: Database,
) -> bool
```

{% endraw %}{% include api-source.html name="import_backup" line=242 %}{% raw %}

</div>

Ask for a backup file and, once the user has agreed, replace
everything with what it holds.

The file is read and checked completely first, so a damaged or
foreign file changes nothing. After the user agrees, a
backup of the current data is saved beside the database, then the
database and the saved preferences are replaced. The
caller has to reload what is on screen afterwards.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | The window the dialogs belong to. |
| `db` | `Database` | The database to replace the contents of. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the backup was applied; False if the user canceled or the file was refused (which is explained). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import_backup(
...     QWidget(), db=Database()
... )  # doctest: +SKIP
True
```
{% endraw %}
