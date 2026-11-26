---
title: new_work_folder
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-new_work_folder/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def new_work_folder() -> Path
```

{% endraw %}{% include api-source.html name="new_work_folder" line=872 %}{% raw %}

</div>

Make a new temporary folder for an update, whose name says what it
is for.

**Returns**

| Type | Description |
| --- | --- |
| `Path` | The empty folder. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> folder = new_work_folder()
>>> folder.is_dir() and folder.name.startswith(
...     LEFTOVER_PREFIX
... )
True
>>> folder.rmdir()
```
{% endraw %}
