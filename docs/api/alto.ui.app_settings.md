---
title: alto.ui.app_settings
parent: api
package: alto.ui
permalink: /api/alto.ui.app_settings/
---
{% raw %}
The application-wide settings dialog.

It holds the color theme, the notation font, the keyboard style, the
transitions, the instrument and what updates follow.

Changes apply as soon as they are made. Each style is a card that
previews it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.windowTitle()
'Settings'
>>> dialog.pages.count()  # Appearance, Sound and Updates
3
```

## PreviewCard

<div class="api-signature" markdown="1">

```python
PreviewCard(
    preview: QWidget,
    *,
    key: str,
    title: str,
    blurb: str,
    height: int,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="PreviewCard" line=194 %}{% raw %}

</div>

Bases: `QPushButton`

A selectable tile that previews a style: a picture drawn in it, with
its name and a few words about it underneath.

**Attributes**

- `style_key` (*str*): The key of the style the card stands for.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = PreviewCard(
...     QLabel("♪"),
...     key="demo",
...     title="Demo",
...     blurb="A short note.",
...     height=120,
... )
>>> (
...     card.style_key,
...     card.isCheckable(),
...     card.height(),
... )
('demo', True, 120)
```

**Constructor**

Build the card around its preview.

**Parameters**

- `preview` (*QWidget*): The picture of the style. Clicks pass through it to the card.
- `key` (*str*): The key of the style. Keyword-only.
- `title` (*str*): The style's name, shown in bold. Keyword-only.
- `blurb` (*str*): A few words about the style, shown in small gray type. Keyword-only.
- `height` (*int*): The card's height before zooming; every card is 232 wide. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> label = QLabel("♪")
>>> card = PreviewCard(
...     label,
...     key="demo",
...     title="Demo",
...     blurb="",
...     height=120,
... )
>>> label.testAttribute(
...     Qt.WidgetAttribute.WA_TransparentForMouseEvents
... )
True
```

## StyleCard

<div class="api-signature" markdown="1">

```python
StyleCard(
    style: notation.NotationStyle,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="StyleCard" line=291 %}{% raw %}

</div>

Bases: `PreviewCard`

A selectable tile that previews a notation style: a short phrase on
a staff, drawn in that style.

**Attributes**

- `style_key` (*str*): The key of the style the card stands for.
- `staff` (*StaffWidget*): The preview.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> StyleCard(
...     notation.BY_KEY["bravura"]
... ).width()
232
```

## KeyboardCard

<div class="api-signature" markdown="1">

```python
KeyboardCard(
    style: keyboard_styles.KeyboardStyle,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyboardCard" line=369 %}{% raw %}

</div>

Bases: `PreviewCard`

A selectable tile that previews a keyboard style: a short stretch of
keys drawn in that style.

**Attributes**

- `style_key` (*str*): The key of the style the card stands for.
- `keys` (*KeyboardWidget*): The preview.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = KeyboardCard(
...     keyboard_styles.BY_KEY["modern"]
... )
>>> card.style_key
'modern'
```

**Constructor**

Build the card for a keyboard style.

**Parameters**

- `style` (*KeyboardStyle*): The style to preview; its label and a few words about it are shown under the keys.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # noinspection PyUnresolvedReferences
>>> KeyboardCard(
...     keyboard_styles.BY_KEY["classic"]
... ).keys.style_override.key
'classic'
```

### KeyboardCard.show_style

<div class="api-signature" markdown="1">

```python
def show_style(style: keyboard_styles.KeyboardStyle) -> None
```

{% endraw %}{% include api-source.html name="KeyboardCard.show_style" line=448 %}{% raw %}

</div>

Redraw the preview in a style.

The custom card follows the colors being edited.

**Parameters**

- `style` (*KeyboardStyle*): The style to preview.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = KeyboardCard(
...     keyboard_styles.BY_KEY["classic"]
... )
>>> card.show_style(
...     keyboard_styles.BY_KEY["modern"]
... )
>>> # noinspection PyUnresolvedReferences
>>> card.keys.style_override.key
'modern'
```

## KeyboardBuilder

<div class="api-signature" markdown="1">

```python
KeyboardBuilder(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="KeyboardBuilder" line=475 %}{% raw %}

</div>

Bases: `QFrame`

Rows for coloring each part of a keyboard.

Each has a swatch that opens the color picker, and chips for colors
named after materials. Changing anything selects
the Custom style.

**Attributes**

- `changed` (*Signal*): Emitted after a part is recolored.
- `swatches` (*dict of str to QPushButton*): The swatch of each part ("naturals", "sharps", "case", "felt" and "caps").

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> builder = KeyboardBuilder()
>>> sorted(builder.swatches)
['caps', 'case', 'felt', 'naturals', 'sharps']
```

**Constructor**

Build the rows and show each part's current color.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the builder.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardBuilder().swatches[
...     "naturals"
... ].width()
46
```

### KeyboardBuilder.refresh

<div class="api-signature" markdown="1">

```python
def refresh() -> None
```

{% endraw %}{% include api-source.html name="KeyboardBuilder.refresh" line=621 %}{% raw %}

</div>

Show each part's current color on its swatch.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> builder = KeyboardBuilder()
>>> builder.refresh()
>>> builder.swatches[
...     "naturals"
... # a color is set, so the swatch shows it, not "none"
... ].text()
''
```

## AppSettingsDialog

<div class="api-signature" markdown="1">

```python
AppSettingsDialog(
    parent: QWidget | None = None,
    *,
    learner: Learner | None = None,
)
```

{% endraw %}{% include api-source.html name="AppSettingsDialog" line=732 %}{% raw %}

</div>

Bases: `QDialog`

Application-wide settings. Changes apply immediately, and the main
window can be used while the dialog is open.

Pages are built when first selected, so hidden previews do not slow
down opening Settings or changing themes.

**Attributes**

- `theme_changed` (*bool*): True once the theme has been changed, so the window can be rebuilt in it.
- `categories` (*QListWidget*): The list of pages on the left: Appearance sections, Sound and Updates.
- `pages` (*QStackedWidget*): The page for the chosen category.
- `instruments` (*InstrumentPicker*): The instrument chooser, available after the Sound page is first selected.
- `theme_list` (*QListWidget*): The themes, on the Theme section, with the one in use in bold.
- `theme_items` (*dict of str to QListWidgetItem*): The rows of that list, by the key of the theme's family.
- `theme_pages` (*QStackedWidget*): The card of the theme chosen in the list, or the editor.
- `theme_editor` (*ThemeEditor*): The form that makes a theme of the user's own, or changes one.
- `new_theme_item` (*QListWidgetItem*): The row of the list that makes a new theme.
- `theme_cards` (*dict of str to ThemeCard*): The cards built so far, by the key of the theme's family. A card is built when its row is first chosen, because every widget makes a change of theme slower; use `card` to get one.
- `theme_scrolls` (*dict of str to QScrollArea*): The scroll area each built card is in, which is what the stack shows; use `scroll` to get one.
- `theme_thumbs` (*dict of str to ThemeThumb*): The clickable pictures of every built card, by the key of the theme each chooses; use `thumb` to get one.
- `transition_list` (*QListWidget*): The choice of transition, available after the Transitions section is first selected.
- `transition_items` (*dict of str to QListWidgetItem*): The rows of that list, by the transition's key.
- `transition_preview` (*TransitionPreview*): Plays the transition that is chosen, beside the choices.
- `scheduler_list` (*QListWidget*): The algorithms on the Practice page, with the current profile's choice selected.
- `scheduler_description` (*QLabel*): Explanation of the selected algorithm beside the list.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.theme_changed
False
```

**Constructor**

Build the dialog with the Appearance page showing.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the dialog.
- `learner` (*Learner or None*): Profile whose practice preferences can be edited.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.categories.currentRow()
0
```

### AppSettingsDialog.card

<div class="api-signature" markdown="1">

```python
def card(family: str) -> ThemeCard
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.card" line=1402 %}{% raw %}

</div>

Give the card of a theme, building it the first time it is asked
for.

Every card is a few dozen widgets, and Qt styles every widget
again when the theme changes, so only the cards that have
been looked at exist.

**Parameters**

- `family` (*str*): The key of the theme's family.

**Returns**

- *ThemeCard*: Its card.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> "sage" in dialog.theme_cards
False
>>> (
...     dialog.card("sage")
...     is dialog.card("sage"),
...     "sage" in dialog.theme_cards,
... )
(True, True)
```

### AppSettingsDialog.card_page

<div class="api-signature" markdown="1">

```python
def card_page(family: str) -> QScrollArea
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.card_page" line=1451 %}{% raw %}

</div>

Give the scroll area that holds a theme's card, which is the
page the stack shows for it.

**Parameters**

- `family` (*str*): The key of the theme's family.

**Returns**

- *QScrollArea*: The area, with the card built if it was not yet.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.card_page(
...     "sage"
... ).widget() is dialog.card("sage")
True
```

### AppSettingsDialog.thumb

<div class="api-signature" markdown="1">

```python
def thumb(key: str) -> ThemeThumb
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.thumb" line=1477 %}{% raw %}

</div>

Give the clickable picture that chooses a theme, with the card
it is on built if it was not yet.

**Parameters**

- `key` (*str*): The key of the theme, such as "light" or "sage_dark".

**Returns**

- *ThemeThumb*: Its picture.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.thumb("sage_dark").isChecked()
False
```

### AppSettingsDialog.choose_theme

<div class="api-signature" markdown="1">

```python
def choose_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.choose_theme" line=2238 %}{% raw %}

</div>

Switch the color theme, remember it, and note that the window
should be rebuilt in it.

**Parameters**

- `key` (*str*): "system", "light" or "dark", or the key of a theme with colors of its own.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.choose_theme("light")
>>> dialog.theme_changed, saved_theme()
(True, 'light')
>>> dialog.choose_theme("system")
```
{% endraw %}
