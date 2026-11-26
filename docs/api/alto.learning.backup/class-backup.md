---
title: Backup
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/class-backup/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Backup(
    info: BackupInfo,
    settings: dict[str, object],
    database: bytes,
)
```

{% endraw %}{% include api-source.html name="Backup" line=116 %}{% raw %}

</div>

A backup that has been read and checked, ready to be applied.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `info` | `BackupInfo` | What the backup says about itself. |
| `settings` | `dict of str to object` | The saved preferences, by key. |
| `database` | `bytes` | The database, as `Database.snapshot` returns it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Backup(
...     BackupInfo(
...         1.0,
...         app_version="0.1.0",
...         schema_version=1,
...         profiles=0,
...         attempts=0,
...     ),
...     settings={},
...     database=b"",
... ).settings
{}
```
{% endraw %}
