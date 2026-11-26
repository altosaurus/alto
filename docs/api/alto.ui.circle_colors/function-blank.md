---
title: blank
parent: alto.ui.circle_colors
api_module: alto.ui.circle_colors
package: alto.ui
permalink: /api/alto.ui.circle_colors/function-blank/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def blank(key: str) -> CustomRecord
```

{% endraw %}{% include api-source.html name="blank" line=66 %}{% raw %}

</div>

Make the scheme a new one starts as: colors by key signature, from
cyan through blue to indigo, on dark wedges.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The key the new scheme gets. |

**Returns**

| Type | Description |
| --- | --- |
| `CustomRecord` | The scheme. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     blank("custom-3")["id"],
...     blank("custom-3")["mode"],
... )
('custom-3', 'signature')
```
{% endraw %}
