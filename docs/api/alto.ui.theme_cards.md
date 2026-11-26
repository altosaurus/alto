---
title: alto.ui.theme_cards
parent: api
package: alto.ui
api_components: [{"title": "ThemeCard", "url": "/api/alto.ui.theme_cards/class-themecard/"}, {"title": "ThemeThumb", "url": "/api/alto.ui.theme_cards/class-themethumb/"}, {"title": "colors_of", "url": "/api/alto.ui.theme_cards/function-colors_of/"}]
permalink: /api/alto.ui.theme_cards/
---
{% raw %}
The card of a theme in the settings.

## Classes

- [`ThemeThumb`](class-themethumb/) — A small picture of the window in a theme, to click to choose the theme.
- [`ThemeCard`](class-themecard/) — The card of one theme: its name, three clickable pictures one above another, and with each the squares of its colors.

## Functions

- [`colors_of`](function-colors_of/) — Give the colors of a theme's picture.

<details markdown="1">
<summary>Module notes and examples</summary>

A card is one theme: its name, three pictures of the window one above
another that can be clicked (light, dark, and System,
which is cut through on a slant to show it is light or dark as the
desktop is) and the squares of its colors.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = ThemeCard("sage")
>>> sorted(card.thumbs)
['sage', 'sage_auto', 'sage_dark']
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"colors_of": "function-colors_of/", "themethumb": "class-themethumb/", "themethumbpaintevent": "class-themethumb/#themethumbpaintevent", "themecard": "class-themecard/", "themecardshow_current": "class-themecard/#themecardshow_current"}</script>
{% include api-fragments.html %}
