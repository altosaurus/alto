---
title: AppSettingsDialog
parent: alto.ui.app_settings
api_module: alto.ui.app_settings
package: alto.ui
permalink: /api/alto.ui.app_settings/class-appsettingsdialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
AppSettingsDialog(
    parent: QWidget | None = None,
    *,
    learner: Learner | None = None,
)
```

{% endraw %}{% include api-source.html name="AppSettingsDialog" line=906 %}{% raw %}

</div>

Bases: `QDialog`

Application-wide settings. Changes apply immediately, and the main
window can be used while the dialog is open.

Pages are built when first selected, so hidden previews do not slow
down opening Settings or changing themes.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `theme_changed` | `bool` | True once the theme has been changed, so the window can be rebuilt in it. |
| `categories` | `QListWidget` | The list of pages on the left: Appearance sections, Sound and Updates. |
| `pages` | `QStackedWidget` | The page for the chosen category. |
| `instruments` | `InstrumentPicker` | The chooser, available after the Instruments page is selected. |
| `theme_list` | `QListWidget` | The themes, on the Theme section, with the one in use in bold. |
| `theme_items` | `dict of str to QListWidgetItem` | The rows of that list, by the key of the theme's family. |
| `theme_pages` | `QStackedWidget` | The card of the theme chosen in the list, or the editor. |
| `theme_editor` | `ThemeEditor` | The form that makes a theme of the user's own, or changes one. |
| `new_theme_item` | `QListWidgetItem` | The row of the list that makes a new theme. |
| `theme_cards` | `dict of str to ThemeCard` | The cards built so far, by the key of the theme's family. A card is built when its row is first chosen, because every widget makes a change of theme slower; use `card` to get one. |
| `theme_scrolls` | `dict of str to QScrollArea` | The scroll area each built card is in, which is what the stack shows; use `scroll` to get one. |
| `theme_thumbs` | `dict of str to ThemeThumb` | The clickable pictures of every built card, by the key of the theme each chooses; use `thumb` to get one. |
| `transition_list` | `QListWidget` | The choice of transition, available after the Transitions section is first selected. |
| `transition_items` | `dict of str to QListWidgetItem` | The rows of that list, by the transition's key. |
| `transition_preview` | `TransitionPreview` | Plays the transition that is chosen, beside the choices. |
| `scheduler_list` | `QListWidget` | The algorithms on the Practice page, with the current profile's choice selected. |
| `scheduler_description` | `QLabel` | Explanation of the selected algorithm beside the list. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.theme_changed
False
```

**Constructor**

Build the dialog with the Appearance page showing.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the dialog. |
| `learner` | `Learner or None` | Profile whose practice preferences can be edited. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.categories.currentRow()
0
```

## AppSettingsDialog.card

<div class="api-signature" markdown="1">

```python
def card(family: str) -> ThemeCard
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.card" line=1620 %}{% raw %}

</div>

Give the card of a theme, building it the first time it is asked
for.

Every card is a few dozen widgets, and Qt styles every widget
again when the theme changes, so only the cards that have
been looked at exist.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `family` | `str` | The key of the theme's family. |

**Returns**

| Type | Description |
| --- | --- |
| `ThemeCard` | Its card. |

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

## AppSettingsDialog.card_page

<div class="api-signature" markdown="1">

```python
def card_page(family: str) -> QScrollArea
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.card_page" line=1669 %}{% raw %}

</div>

Give the scroll area that holds a theme's card, which is the
page the stack shows for it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `family` | `str` | The key of the theme's family. |

**Returns**

| Type | Description |
| --- | --- |
| `QScrollArea` | The area, with the card built if it was not yet. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.card_page(
...     "sage"
... ).widget() is dialog.card("sage")
True
```

## AppSettingsDialog.thumb

<div class="api-signature" markdown="1">

```python
def thumb(key: str) -> ThemeThumb
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.thumb" line=1695 %}{% raw %}

</div>

Give the clickable picture that chooses a theme, with the card
it is on built if it was not yet.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The key of the theme, such as "light" or "sage_dark". |

**Returns**

| Type | Description |
| --- | --- |
| `ThemeThumb` | Its picture. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.thumb("sage_dark").isChecked()
False
```

## AppSettingsDialog.choose_theme

<div class="api-signature" markdown="1">

```python
def choose_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="AppSettingsDialog.choose_theme" line=2523 %}{% raw %}

</div>

Switch the color theme, remember it, and note that the window
should be rebuilt in it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | "system", "light" or "dark", or the key of a theme with colors of its own. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.choose_theme("light")
>>> dialog.theme_changed, saved_theme()
(True, 'light')
>>> dialog.choose_theme("system")
```
{% endraw %}
