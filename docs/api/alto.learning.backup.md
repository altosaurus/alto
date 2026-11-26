---
title: alto.learning.backup
parent: api
package: alto.learning
api_components: [{"title": "Backup", "url": "/api/alto.learning.backup/class-backup/"}, {"title": "BackupError", "url": "/api/alto.learning.backup/class-backuperror/"}, {"title": "BackupInfo", "url": "/api/alto.learning.backup/class-backupinfo/"}, {"title": "app_version", "url": "/api/alto.learning.backup/function-app_version/"}, {"title": "decode_value", "url": "/api/alto.learning.backup/function-decode_value/"}, {"title": "encode_value", "url": "/api/alto.learning.backup/function-encode_value/"}, {"title": "read_backup", "url": "/api/alto.learning.backup/function-read_backup/"}, {"title": "restore_database", "url": "/api/alto.learning.backup/function-restore_database/"}, {"title": "write_backup", "url": "/api/alto.learning.backup/function-write_backup/"}]
permalink: /api/alto.learning.backup/
---
{% raw %}
Backup files: everything Alto keeps, in one file that can be read back
into a clean install. Pure Python (no Qt).

## Classes

- [`BackupError`](class-backuperror/) — A backup file could not be written or read: it is damaged, is not a backup, or was made by a newer Alto.
- [`BackupInfo`](class-backupinfo/) — What a backup says about itself.
- [`Backup`](class-backup/) — A backup that has been read and checked, ready to be applied.

## Functions

- [`app_version`](function-app_version/) — Return the version of Alto that is running.
- [`encode_value`](function-encode_value/) — Turn a saved preference into something JSON can hold.
- [`decode_value`](function-decode_value/) — Undo `encode_value`.
- [`write_backup`](function-write_backup/) — Write a backup of the database and the saved preferences to a file.
- [`read_backup`](function-read_backup/) — Read a backup file and check it all the way through, without changing anything.
- [`restore_database`](function-restore_database/) — Replace everything in the database with what a backup holds.

<details markdown="1">
<summary>Module notes and examples</summary>

A backup is a zip file holding three things: the whole database
(profiles, every answer, what is known about each question),
the saved preferences (theme, fonts, instrument, every exercise's
settings, the last profile used) and a manifest that says
which version of Alto made it and carries a checksum of each part.
Reading a backup back checks the checksums and the database
before anything is changed, so a damaged or foreign file is refused
instead of half applied.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import tempfile
>>> from alto.learning.database import Database
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> folder = Path(tempfile.mkdtemp())
>>> info = write_backup(
...     db,
...     settings={"ui/theme": "dark"},
...     path=folder / "ada.altobackup",
... )
>>> info.profiles, info.attempts
(1, 0)
>>> backup = read_backup(
...     folder / "ada.altobackup"
... )
>>> backup.settings
{'ui/theme': 'dark'}
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"backuperror": "class-backuperror/", "backupinfo": "class-backupinfo/", "backup": "class-backup/", "app_version": "function-app_version/", "encode_value": "function-encode_value/", "decode_value": "function-decode_value/", "write_backup": "function-write_backup/", "read_backup": "function-read_backup/", "restore_database": "function-restore_database/"}</script>
{% include api-fragments.html %}
