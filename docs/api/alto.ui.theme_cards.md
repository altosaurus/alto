---
title: alto.ui.theme_cards
parent: api
package: alto.ui
order: 63
permalink: /api/alto.ui.theme_cards/
---
{% raw %}
The card of a theme in the settings.

A card is one theme: its name, three pictures of the window one above another that can be clicked (light, dark, and System,
which is cut through on a slant to show it is light or dark as the desktop is) and the squares of its colors.

**Examples**

```pycon
>>> card = ThemeCard("sage")
>>> sorted(card.thumbs)
['sage', 'sage_auto', 'sage_dark']
```

## colors_of

```python
def colors_of(key: str) -> dict[str, str]
```

Give the colors of a theme's picture.

**Parameters**

- `key` (*str*): A theme's key: "light", "dark", or a theme with colors of its own, light or dark.

**Returns**

- *dict of str to str*: The window, panel, outline, text, faint and chosen colors, and a tint for the chosen row.

**Examples**

```pycon
>>> colors_of("dark")["window"], colors_of("studio")["window"]
('#2b2b2b', '#eceef1')
```

## ThemeThumb

```python
ThemeThumb(
    key: str,
    *,
    colors: dict[str, str],
    other: dict[str, str] | None = None,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

Bases: `QPushButton`

A small picture of the window in a theme, to click to choose the theme.

**Attributes**

- `theme_key` (*str*): The key of the theme it chooses.
- `colors` (*dict of str to str*): The colors it is drawn in.
- `other` (*dict of str to str or None*): The colors of the dark half, for a picture that is cut through on a slant; None for a plain one.
- `scale_by` (*float*): How many times bigger than the smallest size it is drawn.

**Examples**

```pycon
>>> ThemeThumb("dark", colors=DARK).theme_key
'dark'
```

**Constructor**

Build the picture.

**Parameters**

- `key` (*str*): The theme it chooses.
- `colors` (*dict of str to str*): The colors of the picture, or of its light half.
- `other` (*dict of str to str or None, default None*): The colors of its dark half, for a picture cut through on a slant. Keyword-only.
- `scale` (*float, default 1.0*): How many times bigger than the smallest size to draw it. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> ThemeThumb("system", colors=LIGHT, other=DARK).width(), ThemeThumb("light", colors=LIGHT, scale=2.0).width()
(116, 232)
```

### ThemeThumb.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw the window, cut through on a slant if it has two halves, with an outline that is heavier when it is chosen.

**Parameters**

- `_` (*QPaintEvent*): The paint request.

**Examples**

```pycon
>>> ThemeThumb("light", colors=LIGHT).grab().isNull()
False
```

## ThemeCard

```python
ThemeCard(
    family: str,
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

Bases: `QFrame`

The card of one theme: its name, three clickable pictures one above another, and with each the squares of its colors.

The pictures are Light, Dark and System. The System one is cut through on a slant, light on one side and dark on the other,
because that version is light or dark as the desktop is.

**Attributes**

- `family` (*str*): The key of the theme's family: "default" for System, Light and Dark.
- `thumbs` (*dict of str to ThemeThumb*): The three pictures, by the key of the theme each chooses.
- `change_button` (*QPushButton or None*): Opens the editor; only a theme the user made has one.
- `chosen` (*Signal*): Emitted with the key of the theme when one of the pictures is clicked.
- `edit_requested` (*Signal*): Emitted with the key of the theme when its Change colors button is pressed; only a theme the user made has one.

**Examples**

```pycon
>>> card = ThemeCard("default")
>>> list(card.thumbs)
['light', 'dark', 'system']
```

**Constructor**

Build the card of a family.

**Parameters**

- `family` (*str*): The key of the family: "default", "studio" or one of the generated themes.
- `scale` (*float, default 1.0*): How many times bigger than the smallest size to draw the pictures. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> ThemeCard("studio").family
'studio'
```

### ThemeCard.show_current

```python
def show_current(key: str) -> None
```

Mark the picture of the theme that is in use, and outline the card that has it.

**Parameters**

- `key` (*str*): The key of the theme in use.

**Examples**

```pycon
>>> card = ThemeCard("sage")
>>> card.show_current("sage_dark")
>>> [k for k, picture in card.thumbs.items() if picture.isChecked()]
['sage_dark']
```
{% endraw %}
