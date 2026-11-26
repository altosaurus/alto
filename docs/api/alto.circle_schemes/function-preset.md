---
title: preset
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-preset/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def preset(key: str) -> Scheme
```

{% endraw %}{% include api-source.html name="preset" line=709 %}{% raw %}

</div>

Return a preset by its key.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | A key of `PRESETS`. |

**Returns**

| Type | Description |
| --- | --- |
| `Scheme` | The preset. |

**Raises**

- *KeyError*: If there is no such preset.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preset("midnight").name
'Midnight'
>>> len(PRESETS)
14
```
{% endraw %}
