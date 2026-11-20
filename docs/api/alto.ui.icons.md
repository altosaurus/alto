---
title: alto.ui.icons
parent: api
package: alto.ui
permalink: /api/alto.ui.icons/
---
{% raw %}
Small monochrome icons drawn from SVG, tinted with the current theme's text color.

Each icon is the inside of a 24 by 24 SVG, written with the word COLOR where the theme color goes. `svg_icon` turns one
into a `QIcon`.

**Examples**

```pycon
>>> svg_icon(HELP, color=QColor("black")).isNull()
False
```

## set_palette_icon

```python
def set_palette_icon(
    target: QAbstractButton | QAction | QMenu,
    render: Callable[[QPalette], QIcon],
) -> None
```

Assign a native Qt icon and refresh it whenever the application palette changes.

**Parameters**

- `target` (*QAbstractButton or QAction or QMenu*): Button, menu, or action to update.
- `render` (*Callable*): Draws the icon in the supplied palette.

**Examples**

```pycon
>>> from PySide6.QtWidgets import QPushButton
>>> button = QPushButton()
>>> set_palette_icon(button, lambda palette: svg_icon(HELP, color=palette.text().color()))
>>> button.icon().isNull()
False
```

## set_svg_icon

```python
def set_svg_icon(
    target: QAbstractButton | QAction | QMenu,
    inner: str,
    *,
    role: QPalette.ColorRole = QPalette.ColorRole.WindowText,
    size: int = 24,
) -> None
```

Tint an SVG icon with the control's current foreground or accent color.

**Parameters**

- `target` (*QAbstractButton or QAction or QMenu*): Control that displays the icon.
- `inner` (*str*): SVG shapes using COLOR for the ink.
- `role` (*QPalette.ColorRole, default WindowText*): Color to take from the application palette.
- `size` (*int, default 24*): Logical size in pixels.

**Examples**

```pycon
>>> from PySide6.QtWidgets import QPushButton
>>> button = QPushButton()
>>> set_svg_icon(button, HELP)
>>> button.icon().isNull()
False
```

## set_item_icons

```python
def set_item_icons(
    view: QAbstractItemView,
    items: list[tuple[str, Callable[[QIcon], None]]],
) -> None
```

Recolor the current rows of a navigation list or tree without rebuilding it.

**Parameters**

- `view` (*QAbstractItemView*): List or tree supplying the text color and icon size.
- `items` (*list of tuple*): SVG drawing and icon setter for each row in the current model.

**Examples**

```pycon
A category tree keeps its checked and expanded items when the theme changes.
```

## svg_icon

```python
def svg_icon(
    inner: str,
    *,
    color: QColor,
    size: int = 24,
    scale: float = 2.0,
) -> QIcon
```

Render 24 by 24 SVG shapes into a crisp icon.

**Parameters**

- `inner` (*str*): The SVG shapes, using COLOR wherever the color goes.
- `color` (*QColor*): The color to draw in. Keyword-only.
- `size` (*int, default 24*): The icon's size in logical pixels. Keyword-only.
- `scale` (*float, default 2.0*): How many device pixels to render per logical pixel, so it stays sharp on high-resolution screens. Keyword-only.

**Returns**

- *QIcon*: The icon.

**Examples**

```pycon
>>> icon = svg_icon(PLAY, color=QColor("#336699"), size=16)
>>> icon.isNull()
False
```
{% endraw %}
