---
title: alto.ui.style
parent: api
package: alto.ui
order: 61
permalink: /api/alto.ui.style/
---
{% raw %}
Application-wide stylesheet: rounded corners on buttons, panes, lists and scroll bars.

Colors come from the palette so it follows the system light/dark theme.

**Examples**

```pycon
>>> RADIUS
10
```

## app_style

```python
def app_style(
    palette: QPalette,
    *,
    paper_palette: QPalette | None = None,
) -> str
```

Build the stylesheet for a palette.

Push buttons use rounded hairline borders. In dark mode, exercise tiles have near-black outlines and
other standard buttons have graphite-gray outlines.

**Parameters**

- `palette` (*QPalette*): The palette to take colors from, so the style follows the light or dark theme.
- `paper_palette` (*QPalette or None, default None*): The theme's light variant for playback on white staff paper. Dark desktop themes use Qt light colors with the desktop accent when no light variant is supplied.

**Returns**

- *str*: Qt style sheet text.

**Examples**

```pycon
>>> from PySide6.QtWidgets import QApplication
>>> sheet = app_style(QApplication.palette())
>>> "QPushButton" in sheet and "border-radius" in sheet
True
```
{% endraw %}
