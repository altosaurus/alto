---
title: read_backup
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/function-read_backup/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_backup(path: Path) -> Backup
```

{% endraw %}{% include api-source.html name="read_backup" line=350 %}{% raw %}

</div>

Read a backup file and check it all the way through, without
changing anything.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `path` | `Path` | The file. |

**Returns**

| Type | Description |
| --- | --- |
| `Backup` | The backup, ready to be applied. |

**Raises**

- *BackupError*: If the file cannot be read, is not an Alto backup, is damaged (a part does not match its checksum, or the database is not intact), or was made by a newer version of Alto.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import tempfile
>>> folder = Path(tempfile.mkdtemp())
>>> (folder / "x.altobackup").write_bytes(
...     b"not a zip"
... )
9
>>> read_backup(folder / "x.altobackup")
Traceback (most recent call last):
    ...
alto.learning.backup.BackupError: This is not an Alto backup.
```
{% endraw %}
