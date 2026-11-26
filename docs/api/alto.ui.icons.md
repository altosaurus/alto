---
title: alto.ui.icons
parent: api
package: alto.ui
api_components: [{"title": "set_item_icons", "url": "/api/alto.ui.icons/function-set_item_icons/"}, {"title": "set_palette_icon", "url": "/api/alto.ui.icons/function-set_palette_icon/"}, {"title": "set_svg_icon", "url": "/api/alto.ui.icons/function-set_svg_icon/"}, {"title": "svg_icon", "url": "/api/alto.ui.icons/function-svg_icon/"}]
permalink: /api/alto.ui.icons/
---
{% raw %}
Small monochrome icons drawn from SVG, tinted with the current theme's
text color.

## Functions

- [`set_palette_icon`](function-set_palette_icon/) — Assign a native Qt icon and refresh it whenever the application palette changes.
- [`set_svg_icon`](function-set_svg_icon/) — Tint an SVG icon with the control's current foreground or accent color.
- [`set_item_icons`](function-set_item_icons/) — Recolor the current rows of a navigation list or tree without rebuilding it.
- [`svg_icon`](function-svg_icon/) — Render 24 by 24 SVG shapes into a crisp icon.

<details markdown="1">
<summary>Module notes and examples</summary>

Each icon is the inside of a 24 by 24 SVG, written with the word COLOR
where the theme color goes. `svg_icon` turns one
into a `QIcon`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> svg_icon(
...     HELP, color=QColor("black")
... ).isNull()
False
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"set_palette_icon": "function-set_palette_icon/", "set_svg_icon": "function-set_svg_icon/", "set_item_icons": "function-set_item_icons/", "svg_icon": "function-svg_icon/"}</script>
{% include api-fragments.html %}
