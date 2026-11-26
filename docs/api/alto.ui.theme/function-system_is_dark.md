---
title: system_is_dark
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-system_is_dark/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def system_is_dark() -> bool
```

{% endraw %}{% include api-source.html name="system_is_dark" line=1086 %}{% raw %}

</div>

Say whether the desktop is set to dark, as long as the app is not
forcing a color scheme of its own.

A theme that follows the desktop does not force one, so this is what
it asks.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the color scheme in use is dark. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> system_is_dark() in {True, False}
True
```
{% endraw %}
