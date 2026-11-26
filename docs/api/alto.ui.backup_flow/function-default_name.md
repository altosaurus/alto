---
title: default_name
parent: alto.ui.backup_flow
api_module: alto.ui.backup_flow
package: alto.ui
permalink: /api/alto.ui.backup_flow/function-default_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def default_name(
    *,
    now: float | None = None,
) -> str
```

{% endraw %}{% include api-source.html name="default_name" line=49 %}{% raw %}

</div>

Suggest a file name for a backup made now.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `now` | `float or None, default None` | The time as a timestamp; the clock is used if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | For example `alto-backup-2026-11-13.altobackup`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> default_name(
...     now=datetime(
...         2026, 11, 13, 12
...     ).timestamp()
... )
'alto-backup-2026-11-13.altobackup'
```
{% endraw %}
