---
title: saved_channel
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-saved_channel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def saved_channel() -> str
```

{% endraw %}{% include api-source.html name="saved_channel" line=340 %}{% raw %}

</div>

Return what the update check follows, as chosen in Settings.

**Returns**

| Type | Description |
| --- | --- |
| `str` | "releases" for the newest release, or "main" for the newest commit on the main branch; "releases" if nothing valid is saved. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> saved_channel()
'releases'
>>> save_channel("main")
>>> saved_channel()
'main'
>>> save_channel("releases")
```
{% endraw %}
