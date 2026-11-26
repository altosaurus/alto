---
title: scheme_of
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-scheme_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def scheme_of(key: str) -> Qt.ColorScheme | None
```

{% endraw %}{% include api-source.html name="scheme_of" line=880 %}{% raw %}

</div>

Say which color scheme a theme uses: light, dark, or the desktop's
own.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The theme's key. |

**Returns**

| Type | Description |
| --- | --- |
| `Qt.ColorScheme or None` | The scheme; None if there is no theme with that key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     scheme_of("dark")
...     == Qt.ColorScheme.Dark,
...     scheme_of("sage_auto")
...     == Qt.ColorScheme.Unknown,
...     scheme_of("nonsense"),
... )
(True, True, None)
```
{% endraw %}
