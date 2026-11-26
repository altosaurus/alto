---
title: family_of
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-family_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def family_of(key: str) -> tuple[str, str]
```

{% endraw %}{% include api-source.html name="family_of" line=393 %}{% raw %}

</div>

Split a theme's key into its family and which version of it that is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The key of any theme. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (str, str)` | The family's key and "light", "dark" or "system". "system", "light" and "dark" belong to the family "default". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     family_of("sage_dark"),
...     family_of("sage"),
...     family_of("sage_auto"),
...     family_of("dark"),
...     family_of("system"),
... )
(('sage', 'dark'), ('sage', 'light'), ('sage', 'system'),
('default', 'dark'), ('default', 'system'))
```
{% endraw %}
