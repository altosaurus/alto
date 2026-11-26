---
title: app_style
parent: alto.ui.style
api_module: alto.ui.style
package: alto.ui
permalink: /api/alto.ui.style/function-app_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def app_style(
    palette: QPalette,
    *,
    paper_palette: QPalette | None = None,
) -> str
```

{% endraw %}{% include api-source.html name="app_style" line=92 %}{% raw %}

</div>

Build the stylesheet for a palette.

Push buttons use rounded hairline borders. In dark mode, exercise
tiles have near-black outlines and
other standard buttons have graphite-gray outlines.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `palette` | `QPalette` | The palette to take colors from, so the style follows the light or dark theme. |
| `paper_palette` | `QPalette or None, default None` | The theme's light variant for playback on white staff paper. Dark desktop themes use Qt light colors with the desktop accent when no light variant is supplied. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Qt style sheet text. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtWidgets import QApplication
>>> sheet = app_style(QApplication.palette())
>>> "QPushButton" in sheet and "border-radius" in sheet
True
```
{% endraw %}
