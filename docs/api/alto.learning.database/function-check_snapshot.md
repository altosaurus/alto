---
title: check_snapshot
parent: alto.learning.database
api_module: alto.learning.database
package: alto.learning
permalink: /api/alto.learning.database/function-check_snapshot/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def check_snapshot(data: bytes) -> tuple[int, int, int]
```

{% endraw %}{% include api-source.html name="check_snapshot" line=211 %}{% raw %}

</div>

Check that bytes are an intact Alto database that this version can
read, and say what is in it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `data` | `bytes` | A snapshot, as `Database.snapshot` returns it. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (int, int, int)` | The schema version, the number of profiles and the number of answers. |

**Raises**

- *ValueError*: If the data is not a SQLite database, is damaged, is not an Alto database, or has a newer schema than this version knows.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> check_snapshot(Database().snapshot()) == (
...     SCHEMA_VERSION,
...     0,
...     0,
... )
True
>>> check_snapshot(b"not a database")
Traceback (most recent call last):
    ...
ValueError: This is not an Alto database.
```
{% endraw %}
