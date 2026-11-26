---
title: save_channel
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-save_channel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_channel(channel: str) -> None
```

{% endraw %}{% include api-source.html name="save_channel" line=372 %}{% raw %}

</div>

Remember what the update check follows.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `channel` | `str` | "releases" or "main". Anything else is saved as "releases". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_channel("nonsense")
>>> saved_channel()
'releases'
```
{% endraw %}
