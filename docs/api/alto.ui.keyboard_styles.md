---
title: alto.ui.keyboard_styles
parent: api
package: alto.ui
api_components: [{"title": "KeyboardStyle", "url": "/api/alto.ui.keyboard_styles/class-keyboardstyle/"}, {"title": "current", "url": "/api/alto.ui.keyboard_styles/function-current/"}, {"title": "custom_colors", "url": "/api/alto.ui.keyboard_styles/function-custom_colors/"}, {"title": "custom_style", "url": "/api/alto.ui.keyboard_styles/function-custom_style/"}, {"title": "edge_color", "url": "/api/alto.ui.keyboard_styles/function-edge_color/"}, {"title": "key_brush", "url": "/api/alto.ui.keyboard_styles/function-key_brush/"}, {"title": "load_style", "url": "/api/alto.ui.keyboard_styles/function-load_style/"}, {"title": "on_redraw", "url": "/api/alto.ui.keyboard_styles/function-on_redraw/"}, {"title": "reversed_key", "url": "/api/alto.ui.keyboard_styles/function-reversed_key/"}, {"title": "set_custom_color", "url": "/api/alto.ui.keyboard_styles/function-set_custom_color/"}, {"title": "set_style", "url": "/api/alto.ui.keyboard_styles/function-set_style/"}, {"title": "style_for", "url": "/api/alto.ui.keyboard_styles/function-style_for/"}]
permalink: /api/alto.ui.keyboard_styles/
---
{% raw %}
Keyboard styles: the colors and materials the on-screen piano keys are
drawn in.

## Classes

- [`KeyboardStyle`](class-keyboardstyle/) — How a keyboard looks: the colors of the keys and the case, and a few details of the drawing.

## Functions

- [`custom_colors`](function-custom_colors/) — Return the color of each part of the custom keyboard.
- [`custom_style`](function-custom_style/) — Build the style from the custom colors.
- [`style_for`](function-style_for/) — Return the style with a given key.
- [`current`](function-current/) — Return the keyboard style in use.
- [`load_style`](function-load_style/) — Apply the saved style (Classic if none is saved or it is unknown), and the saved custom colors.
- [`set_style`](function-set_style/) — Choose and save a style, and redraw every keyboard already on screen.
- [`set_custom_color`](function-set_custom_color/) — Color one part of the custom keyboard and switch to the custom style.
- [`on_redraw`](function-on_redraw/) — Register a function to call whenever the keyboard style changes.
- [`reversed_key`](function-reversed_key/) — Report whether a key has swapped colors, as the low preset keys of an organ do.
- [`key_brush`](function-key_brush/) — Return the fill for a key.
- [`edge_color`](function-edge_color/) — Return the outline color for a key.

<details markdown="1">
<summary>Module notes and examples</summary>

There are ready-made styles (`STYLES`) and a custom one built from
colors chosen part by part.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BY_KEY["classic"].label
'Classic'
>>> style_for("no such style").key == DEFAULT
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"keyboardstyle": "class-keyboardstyle/", "custom_colors": "function-custom_colors/", "custom_style": "function-custom_style/", "style_for": "function-style_for/", "current": "function-current/", "load_style": "function-load_style/", "set_style": "function-set_style/", "set_custom_color": "function-set_custom_color/", "on_redraw": "function-on_redraw/", "reversed_key": "function-reversed_key/", "key_brush": "function-key_brush/", "edge_color": "function-edge_color/"}</script>
{% include api-fragments.html %}
