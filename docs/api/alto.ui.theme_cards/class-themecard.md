---
title: ThemeCard
parent: alto.ui.theme_cards
api_module: alto.ui.theme_cards
package: alto.ui
permalink: /api/alto.ui.theme_cards/class-themecard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ThemeCard(
    family: str,
    *,
    scale: float = 1.0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ThemeCard" line=337 %}{% raw %}

</div>

Bases: `QFrame`

The card of one theme: its name, three clickable pictures one above
another, and with each the squares of its colors.

The pictures are Light, Dark and System. The System one is cut
through on a slant, light on one side and dark on the other,
because that version is light or dark as the desktop is.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `family` | `str` | The key of the theme's family: "default" for System, Light and Dark. |
| `thumbs` | `dict of str to ThemeThumb` | The three pictures, by the key of the theme each chooses. |
| `change_button` | `QPushButton or None` | Opens the editor; only a theme the user made has one. |
| `chosen` | `Signal` | Emitted with the key of the theme when one of the pictures is clicked. |
| `edit_requested` | `Signal` | Emitted with the key of the theme when its Change colors button is pressed; only a theme the user made has one. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = ThemeCard("default")
>>> list(card.thumbs)
['light', 'dark', 'system']
```

**Constructor**

Build the card of a family.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `family` | `str` | The key of the family: "default", "studio" or one of the generated themes. |
| `scale` | `float, default 1.0` | How many times bigger than the smallest size to draw the pictures. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ThemeCard("studio").family
'studio'
```

## ThemeCard.show_current

<div class="api-signature" markdown="1">

```python
def show_current(key: str) -> None
```

{% endraw %}{% include api-source.html name="ThemeCard.show_current" line=549 %}{% raw %}

</div>

Mark the picture of the theme that is in use, and outline the
card that has it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The key of the theme in use. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = ThemeCard("sage")
>>> card.show_current("sage_dark")
>>> [
...     k
...     for k, picture in card.thumbs.items()
...     if picture.isChecked()
... ]
['sage_dark']
```
{% endraw %}
