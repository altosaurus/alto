---
title: describe
parent: alto.ui.backup_flow
api_module: alto.ui.backup_flow
package: alto.ui
permalink: /api/alto.ui.backup_flow/function-describe/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def describe(info: BackupInfo) -> str
```

{% endraw %}{% include api-source.html name="describe" line=108 %}{% raw %}

</div>

Say what a backup holds and when it was made, for the question asked
before importing it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `info` | `BackupInfo` | What the backup says about itself. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | A sentence or two. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> text = describe(
...     BackupInfo(
...         datetime(
...             2026, 11, 13, 9, 30
...         ).timestamp(),
...         app_version="0.1.0",
...         schema_version=1,
...         profiles=2,
...         attempts=1500,
...     )
... )
>>> text
'Made on 13 November 2026, 09:30 by Alto 0.1.0. It holds 2 profiles
and 1,500 answers.'
```
{% endraw %}
