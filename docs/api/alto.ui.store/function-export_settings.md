---
title: export_settings
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-export_settings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def export_settings() -> dict[str, object]
```

{% endraw %}{% include api-source.html name="export_settings" line=452 %}{% raw %}

</div>

Return every saved preference, by key, for a backup.

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to object` | Each key Alto has saved and its value. Qt byte arrays come back as `bytes` and lists as lists. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue("demo/name", "Ada")
>>> export_settings()["demo/name"]
'Ada'
>>> settings_.remove("demo")
```
{% endraw %}
