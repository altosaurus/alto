---
title: BackupError
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/class-backuperror/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class BackupError(Exception)
```

{% endraw %}{% include api-source.html name="BackupError" line=62 %}{% raw %}

</div>

A backup file could not be written or read: it is damaged, is not a
backup, or was made by a newer Alto.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> str(
...     BackupError(
...         "This is not an Alto backup."
...     )
... )
'This is not an Alto backup.'
```
{% endraw %}
