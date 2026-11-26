---
title: apply_theme
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-apply_theme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def apply_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="apply_theme" line=1161 %}{% raw %}

</div>

Switch the application's color scheme and rebuild the stylesheet
from the new palette.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | "system" to follow the desktop, "light" or "dark", or the key of a theme with colors of its own. Anything else follows the system. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> apply_theme("system")
>>> # noinspection PyUnresolvedReferences
>>> app.styleSheet() != ""
True
>>> apply_theme("studio")
>>> QApplication.palette().color(
...     QPalette.ColorRole.Window
... ).name()
'#eceef1'
>>> apply_theme("system")
>>> QApplication.palette().color(
...     QPalette.ColorRole.Window
... ).name() != "#eceef1"
True
```
{% endraw %}
