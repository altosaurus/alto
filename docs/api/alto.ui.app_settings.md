---
title: alto.ui.app_settings
parent: api
package: alto.ui
order: 19
permalink: /api/alto.ui.app_settings/
---
{% raw %}
The application-wide settings dialog.

It holds the colour theme, the notation font, the keyboard style, the transitions, the instrument and what updates follow.

Changes apply as soon as they are made. Each style is a card that previews it.

**Examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> dialog.windowTitle()
'Settings'
>>> dialog.pages.count()  # Appearance, Sound and Updates
3
```

## StyleCard

```python
StyleCard(
    style: notation.NotationStyle,
    *,
    parent: QWidget | None = None,
)
```

Bases: `QPushButton`

A selectable tile that previews a notation style: a short phrase on a staff, drawn in that style.

**Attributes**

- `style_key` (*str*): The key of the style the card stands for.
- `staff` (*StaffWidget*): The preview.

**Examples**

```pycon
>>> card = StyleCard(notation.BY_KEY["leland"])
>>> card.style_key, card.isCheckable()
('leland', True)
```

**Constructor**

Build the card for a notation style.

**Parameters**

- `style` (*NotationStyle*): The style to preview; its label and a few words about it are shown under the staff.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```pycon
>>> StyleCard(notation.BY_KEY["bravura"]).width()
232
```

## KeyboardCard

```python
KeyboardCard(
    style: keyboard_styles.KeyboardStyle,
    *,
    parent: QWidget | None = None,
)
```

Bases: `QPushButton`

A selectable tile that previews a keyboard style: a short stretch of keys drawn in that style.

**Attributes**

- `style_key` (*str*): The key of the style the card stands for.
- `keys` (*KeyboardWidget*): The preview.

**Examples**

```pycon
>>> card = KeyboardCard(keyboard_styles.BY_KEY["modern"])
>>> card.style_key
'modern'
```

**Constructor**

Build the card for a keyboard style.

**Parameters**

- `style` (*KeyboardStyle*): The style to preview; its label and a few words about it are shown under the keys.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```pycon
>>> # noinspection PyUnresolvedReferences
>>> KeyboardCard(keyboard_styles.BY_KEY["classic"]).keys.style_override.key
'classic'
```

### KeyboardCard.show_style

```python
def show_style(style: keyboard_styles.KeyboardStyle) -> None
```

Redraw the preview in a style.

The custom card follows the colours being edited.

**Parameters**

- `style` (*KeyboardStyle*): The style to preview.

**Examples**

```pycon
>>> card = KeyboardCard(keyboard_styles.BY_KEY["classic"])
>>> card.show_style(keyboard_styles.BY_KEY["modern"])
>>> # noinspection PyUnresolvedReferences
>>> card.keys.style_override.key
'modern'
```

## KeyboardBuilder

```python
KeyboardBuilder(parent: QWidget | None = None)
```

Bases: `QFrame`

Rows for colouring each part of a keyboard.

Each has a swatch that opens the colour picker, and chips for colours named after materials. Changing anything selects
the Custom style.

**Attributes**

- `changed` (*Signal*): Emitted after a part is recoloured.
- `swatches` (*dict of str to QPushButton*): The swatch of each part ("naturals", "sharps", "case", "felt" and "caps").

**Examples**

```pycon
>>> builder = KeyboardBuilder()
>>> sorted(builder.swatches)
['caps', 'case', 'felt', 'naturals', 'sharps']
```

**Constructor**

Build the rows and show each part's current colour.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the builder.

**Constructor examples**

```pycon
>>> KeyboardBuilder().swatches["naturals"].width()
46
```

### KeyboardBuilder.refresh

```python
def refresh() -> None
```

Show each part's current colour on its swatch.

**Examples**

```pycon
>>> builder = KeyboardBuilder()
>>> builder.refresh()
>>> builder.swatches["naturals"].text()  # a colour is set, so the swatch shows it, not "none"
''
```

## AppSettingsDialog

```python
AppSettingsDialog(parent: QWidget | None = None)
```

Bases: `QDialog`

Application-wide settings. Changes apply immediately, and the main window can be used while the dialog is open.

**Attributes**

- `theme_changed` (*bool*): True once the theme has been changed, so the window can be rebuilt in it.
- `categories` (*QListWidget*): The list of pages on the left: Appearance and Sound.
- `pages` (*QStackedWidget*): The page for the chosen category.
- `instruments` (*InstrumentPicker*): The instrument chooser on the Sound page.
- `theme_list` (*QListWidget*): The themes, on the Theme section, with the one in use in bold.
- `theme_items` (*dict of str to QListWidgetItem*): The rows of that list, by the key of the theme's family.
- `theme_pages` (*QStackedWidget*): The card of the theme chosen in the list, or the editor.
- `theme_editor` (*ThemeEditor*): The form that makes a theme of the user's own, or changes one.
- `new_theme_item` (*QListWidgetItem*): The row of the list that makes a new theme.
- `theme_cards` (*dict of str to ThemeCard*): The cards built so far, by the key of the theme's family. A card is built when its row is first chosen, because every widget makes a change of theme slower; use `card` to get one.
- `theme_scrolls` (*dict of str to QScrollArea*): The scroll area each built card is in, which is what the stack shows; use `scroll` to get one.
- `theme_thumbs` (*dict of str to ThemeThumb*): The clickable pictures of every built card, by the key of the theme each chooses; use `thumb` to get one.
- `transition_list` (*QListWidget*): The choice of transition between the exercises and the lessons, on the Transitions section.
- `transition_items` (*dict of str to QListWidgetItem*): The rows of that list, by the transition's key.
- `transition_preview` (*TransitionPreview*): Plays the transition that is chosen, beside the choices.

**Examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> dialog.theme_changed
False
```

**Constructor**

Build the dialog with the Appearance page showing.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the dialog.

**Constructor examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> dialog.categories.currentRow()
0
```

### AppSettingsDialog.changeEvent

```python
def changeEvent(event: QEvent) -> None
```

Restyle the segmented control when the palette changes, so it follows the theme.

**Parameters**

- `event` (*QEvent*): The change.

**Examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> dialog.changeEvent(QEvent(QEvent.Type.PaletteChange))
```

### AppSettingsDialog.card

```python
def card(family: str) -> ThemeCard
```

Give the card of a theme, building it the first time it is asked for.

Every card is a few dozen widgets, and Qt styles every widget again when the theme changes, so only the cards that have
been looked at exist.

**Parameters**

- `family` (*str*): The key of the theme's family.

**Returns**

- *ThemeCard*: Its card.

**Examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> "sage" in dialog.theme_cards
False
>>> dialog.card("sage") is dialog.card("sage"), "sage" in dialog.theme_cards
(True, True)
```

### AppSettingsDialog.card_page

```python
def card_page(family: str) -> QScrollArea
```

Give the scroll area that holds a theme's card, which is the page the stack shows for it.

**Parameters**

- `family` (*str*): The key of the theme's family.

**Returns**

- *QScrollArea*: The area, with the card built if it was not yet.

**Examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> dialog.card_page("sage").widget() is dialog.card("sage")
True
```

### AppSettingsDialog.thumb

```python
def thumb(key: str) -> ThemeThumb
```

Give the clickable picture that chooses a theme, with the card it is on built if it was not yet.

**Parameters**

- `key` (*str*): The key of the theme, such as "light" or "sage_dark".

**Returns**

- *ThemeThumb*: Its picture.

**Examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> dialog.thumb("sage_dark").isChecked()
False
```

### AppSettingsDialog.choose_theme

```python
def choose_theme(key: str) -> None
```

Switch the colour theme, remember it, and note that the window should be rebuilt in it.

**Parameters**

- `key` (*str*): "system", "light" or "dark", or the key of a theme with colours of its own.

**Examples**

```pycon
>>> dialog = AppSettingsDialog()
>>> dialog.choose_theme("light")
>>> dialog.theme_changed, saved_theme()
(True, 'light')
>>> dialog.choose_theme("system")
```
{% endraw %}
