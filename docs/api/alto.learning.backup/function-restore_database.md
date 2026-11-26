---
title: restore_database
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/function-restore_database/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def restore_database(
    db: Database,
    *,
    backup: Backup,
) -> None
```

{% endraw %}{% include api-source.html name="restore_database" line=445 %}{% raw %}

</div>

Replace everything in the database with what a backup holds.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `db` | `Database` | The database to replace the contents of. |
| `backup` | `Backup` | A backup, as `read_backup` returns it. Keyword-only. |

**Raises**

- *BackupError*: If the database in the backup cannot be loaded. The database is not changed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import tempfile
>>> from alto.learning.database import Database
>>> source = Database()
>>> _ = source.add_profile("Ada")
>>> folder = Path(tempfile.mkdtemp())
>>> _ = write_backup(
...     source,
...     settings={},
...     path=folder / "a.altobackup",
... )
>>> clean = Database()
>>> restore_database(
...     clean,
...     backup=read_backup(
...         folder / "a.altobackup"
...     ),
... )
>>> [p.name for p in clean.profiles()]
['Ada']
```
{% endraw %}
