---
title: alto.ui.keyboard
parent: api
package: alto.ui
api_components: [{"title": "KeyboardSpan", "url": "/api/alto.ui.keyboard/class-keyboardspan/"}, {"title": "KeyboardWidget", "url": "/api/alto.ui.keyboard/class-keyboardwidget/"}]
permalink: /api/alto.ui.keyboard/
---
{% raw %}
The on-screen piano keyboard, drawn to real proportions, and a miniature
of the whole piano for choosing a span of keys.

## Classes

- [`KeyboardWidget`](class-keyboardwidget/) — A piano keyboard drawn to real proportions that can highlight one or more keys.
- [`KeyboardSpan`](class-keyboardspan/) — The whole 88-key piano in miniature, with the keys that will be asked shaded.

<details markdown="1">
<summary>Module notes and examples</summary>

`KeyboardWidget` shows a range of keys and can highlight one.
`KeyboardSpan` shows all 88 keys in miniature, shades the
range that will be asked, and can be dragged to change it. Colors and
materials come from `keyboard_styles`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.show_key(60)
>>> keyboard.highlight
60
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"keyboardwidget": "class-keyboardwidget/", "keyboardwidgetstyle": "class-keyboardwidget/#keyboardwidgetstyle", "keyboardwidgetrefit": "class-keyboardwidget/#keyboardwidgetrefit", "keyboardwidgetfull_width": "class-keyboardwidget/#keyboardwidgetfull_width", "keyboardwidgetresizeevent": "class-keyboardwidget/#keyboardwidgetresizeevent", "keyboardwidgetshow_key": "class-keyboardwidget/#keyboardwidgetshow_key", "keyboardwidgetshow_keys": "class-keyboardwidget/#keyboardwidgetshow_keys", "keyboardwidgetset_highlight_color": "class-keyboardwidget/#keyboardwidgetset_highlight_color", "keyboardwidgetpaintevent": "class-keyboardwidget/#keyboardwidgetpaintevent", "keyboardspan": "class-keyboardspan/", "keyboardspankey_at": "class-keyboardspan/#keyboardspankey_at", "keyboardspanmousepressevent": "class-keyboardspan/#keyboardspanmousepressevent", "keyboardspanmousemoveevent": "class-keyboardspan/#keyboardspanmousemoveevent", "keyboardspanmousereleaseevent": "class-keyboardspan/#keyboardspanmousereleaseevent", "keyboardspanset_span": "class-keyboardspan/#keyboardspanset_span", "keyboardspanpaintevent": "class-keyboardspan/#keyboardspanpaintevent"}</script>
{% include api-fragments.html %}
