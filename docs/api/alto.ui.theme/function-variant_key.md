---
title: variant_key
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-variant_key/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def variant_key(
    family: str,
    *,
    version: str,
) -> str
```

{% endraw %}{% include api-source.html name="variant_key" line=432 %}{% raw %}

</div>

Give the key of one version of a family.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `family` | `str` | The family's key. |
| `version` | `str` | "light", "dark" or "system". Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     variant_key("sage", version="dark"),
...     variant_key("sage", version="system"),
...     variant_key("default", version="dark"),
... )
('sage_dark', 'sage_auto', 'dark')
```
{% endraw %}
