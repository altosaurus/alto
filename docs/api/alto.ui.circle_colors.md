---
title: alto.ui.circle_colors
parent: api
package: alto.ui
api_components: [{"title": "SchemeEditor", "url": "/api/alto.ui.circle_colors/class-schemeeditor/"}, {"title": "SchemePage", "url": "/api/alto.ui.circle_colors/class-schemepage/"}, {"title": "SchemeThumb", "url": "/api/alto.ui.circle_colors/class-schemethumb/"}, {"title": "blank", "url": "/api/alto.ui.circle_colors/function-blank/"}]
permalink: /api/alto.ui.circle_colors/
---
{% raw %}
The pages of the circle of fifths settings that choose its colors: a
grid of schemes to pick from, and an editor to make one.

## Classes

- [`SchemeThumb`](class-schemethumb/) — A small picture of the circle in a color scheme, to click to choose the scheme.
- [`SchemePage`](class-schemepage/) — The page that lists the color schemes: the presets, the user's own, and a button to make another.
- [`SchemeEditor`](class-schemeeditor/) — The editor for a color scheme of the user's own: a name, how its colors are made, and the colors.

## Functions

- [`blank`](function-blank/) — Make the scheme a new one starts as: colors by key signature, from cyan through blue to indigo, on dark wedges.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(preset("midnight")).scheme.name
'Midnight'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"blank": "function-blank/", "schemethumb": "class-schemethumb/", "schemethumbsizehint": "class-schemethumb/#schemethumbsizehint", "schemethumbpaintevent": "class-schemethumb/#schemethumbpaintevent", "schemepage": "class-schemepage/", "schemepageload": "class-schemepage/#schemepageload", "schemeeditor": "class-schemeeditor/", "schemeeditorload": "class-schemeeditor/#schemeeditorload", "schemeeditorrecord": "class-schemeeditor/#schemeeditorrecord", "schemeeditorset_color": "class-schemeeditor/#schemeeditorset_color"}</script>
{% include api-fragments.html %}
