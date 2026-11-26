---
title: alto.ui.notes
parent: api
package: alto.ui
api_components: [{"title": "draw_note", "url": "/api/alto.ui.notes/function-draw_note/"}, {"title": "note_shape", "url": "/api/alto.ui.notes/function-note_shape/"}]
permalink: /api/alto.ui.notes/
---
{% raw %}
Engraved notes built from the Noto Music font's glyphs, the way notation
software draws them.

## Functions

- [`note_shape`](function-note_shape/) — Return the outline of a note of a value, with the stem up or down.
- [`draw_note`](function-draw_note/) — Draw a note with its head centered on a point, in Noto Music.

<details markdown="1">
<summary>Module notes and examples</summary>

The font only has stem-up notes. A stem-down note is made from the same
glyph turned half a turn (which puts the stem on
the left of the head and keeps the head's tilt), with the flags cut from
the stem-up glyph and mirrored so they sweep up
from the stem's end, as an engraver would write them.

All numbers are in glyph units at a font size of 100, where one staff
space is `STAFF_SPACE` units.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> note_shape("quarter").isEmpty()
False
>>> note_shape(
...     "whole", stem_down=True
... ) is note_shape(
...     "whole"
... )  # a whole note has no stem to turn
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"note_shape": "function-note_shape/", "draw_note": "function-draw_note/"}</script>
{% include api-fragments.html %}
