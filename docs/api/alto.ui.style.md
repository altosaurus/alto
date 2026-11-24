---
title: alto.ui.style
parent: api
package: alto.ui
permalink: /api/alto.ui.style/
---
{% raw %}
Application-wide stylesheet: rounded corners on buttons, panes, lists
and scroll bars.

Colors come from the palette so it follows the system light/dark theme.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RADIUS
10
```

## navigation_heading_style

```python
def navigation_heading_style(palette: QPalette) -> tuple[QFont, QColor]
```

Style category headings in the navigation pane and tile filters.

**Parameters**

- `palette` (*QPalette*): The pane's current palette.

**Returns**

- *tuple of QFont and QColor*: The small, spaced capitals and muted foreground used for section headings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> navigation_heading_style(QPalette())[
...     0
... ].bold()
True
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

Push buttons use rounded hairline borders. In dark mode, exercise
tiles have near-black outlines and
other standard buttons have graphite-gray outlines.

**Parameters**

- `palette` (*QPalette*): The palette to take colors from, so the style follows the light or dark theme.
- `paper_palette` (*QPalette or None, default None*): The theme's light variant for playback on white staff paper. Dark desktop themes use Qt light colors with the desktop accent when no light variant is supplied.

**Returns**

- *str*: Qt style sheet text.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtWidgets import QApplication
>>> sheet = app_style(QApplication.palette())
>>> "QPushButton" in sheet and "border-radius" in sheet
True
```
{% endraw %}
