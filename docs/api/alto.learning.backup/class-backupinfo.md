---
title: BackupInfo
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/class-backupinfo/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
BackupInfo(
    created: float,
    app_version: str,
    schema_version: int,
    profiles: int,
    attempts: int,
)
```

{% endraw %}{% include api-source.html name="BackupInfo" line=79 %}{% raw %}

</div>

What a backup says about itself.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `created` | `float` | When it was made, as a timestamp. |
| `app_version` | `str` | The version of Alto that made it. |
| `schema_version` | `int` | The version of the database layout it holds. |
| `profiles` | `int` | How many profiles it holds. |
| `attempts` | `int` | How many answers it holds. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BackupInfo(
...     100.0,
...     app_version="0.1.0",
...     schema_version=1,
...     profiles=2,
...     attempts=30,
... ).profiles
2
```
{% endraw %}
