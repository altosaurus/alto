---
title: write_backup
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/function-write_backup/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def write_backup(
    db: Database,
    *,
    settings: Mapping[str, object],
    path: Path,
    now: float | None = None,
) -> BackupInfo
```

{% endraw %}{% include api-source.html name="write_backup" line=259 %}{% raw %}

</div>

Write a backup of the database and the saved preferences to a file.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `db` | `Database` | The database to back up. It is not changed. |
| `settings` | `mapping of str to object` | The saved preferences, by key. Keyword-only. |
| `path` | `Path` | The file to write; it is replaced if it exists. Keyword-only. |
| `now` | `float or None, default None` | The time to record, as a timestamp; the clock is used if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `BackupInfo` | What the backup says about itself. |

**Raises**

- *BackupError*: If the file cannot be written. Nothing is left at `path` in that case.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import tempfile
>>> from alto.learning.database import Database
>>> folder = Path(tempfile.mkdtemp())
>>> write_backup(
...     Database(),
...     settings={},
...     path=folder / "empty.altobackup",
...     now=5.0,
... ).created
5.0
```
{% endraw %}
