---
title: alto.ui.notation
parent: api
package: alto.ui
api_components: [{"title": "NotationStyle", "url": "/api/alto.ui.notation/class-notationstyle/"}, {"title": "baritone_clef", "url": "/api/alto.ui.notation/function-baritone_clef/"}, {"title": "clef_shape", "url": "/api/alto.ui.notation/function-clef_shape/"}, {"title": "current", "url": "/api/alto.ui.notation/function-current/"}, {"title": "load_style", "url": "/api/alto.ui.notation/function-load_style/"}, {"title": "on_redraw", "url": "/api/alto.ui.notation/function-on_redraw/"}, {"title": "set_baritone_clef", "url": "/api/alto.ui.notation/function-set_baritone_clef/"}, {"title": "set_style", "url": "/api/alto.ui.notation/function-set_style/"}]
permalink: /api/alto.ui.notation/
---
{% raw %}
Notation styles: which music font the staff, clefs, notes and
accidentals are engraved in.

## Classes

- [`NotationStyle`](class-notationstyle/) — One look for the music: a font and how heavy the staff lines are.

## Functions

- [`baritone_clef`](function-baritone_clef/) — Return which way the baritone clef is written.
- [`clef_shape`](function-clef_shape/) — Return the clef as it is drawn.
- [`set_baritone_clef`](function-set_baritone_clef/) — Choose and save how the baritone clef is written, and redraw every staff already on screen.
- [`current`](function-current/) — Return the notation style in use.
- [`load_style`](function-load_style/) — Apply the saved choices: the style (Finale Maestro if none is saved or it is unknown) and the baritone clef.
- [`set_style`](function-set_style/) — Choose and save a style, and redraw every staff already on screen.
- [`on_redraw`](function-on_redraw/) — Register a function to call whenever the notation style changes.

<details markdown="1">
<summary>Module notes and examples</summary>

Also holds the choice of how the baritone clef is written (an F clef or
a C clef).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BY_KEY["leland"].label
'Leland'
>>> clef_shape("treble")
'treble'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"notationstyle": "class-notationstyle/", "baritone_clef": "function-baritone_clef/", "clef_shape": "function-clef_shape/", "set_baritone_clef": "function-set_baritone_clef/", "current": "function-current/", "load_style": "function-load_style/", "set_style": "function-set_style/", "on_redraw": "function-on_redraw/"}</script>
{% include api-fragments.html %}
