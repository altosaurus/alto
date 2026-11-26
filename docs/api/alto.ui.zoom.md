---
title: alto.ui.zoom
parent: api
package: alto.ui
api_components: [{"title": "WheelZoom", "url": "/api/alto.ui.zoom/class-wheelzoom/"}, {"title": "apply_font", "url": "/api/alto.ui.zoom/function-apply_font/"}, {"title": "css", "url": "/api/alto.ui.zoom/function-css/"}, {"title": "factor", "url": "/api/alto.ui.zoom/function-factor/"}, {"title": "load", "url": "/api/alto.ui.zoom/function-load/"}, {"title": "percent", "url": "/api/alto.ui.zoom/function-percent/"}, {"title": "px", "url": "/api/alto.ui.zoom/function-px/"}, {"title": "reset", "url": "/api/alto.ui.zoom/function-reset/"}, {"title": "set_percent", "url": "/api/alto.ui.zoom/function-set_percent/"}, {"title": "step", "url": "/api/alto.ui.zoom/function-step/"}]
permalink: /api/alto.ui.zoom/
---
{% raw %}
Zoom: make everything in Alto larger or smaller together.

## Classes

- [`WheelZoom`](class-wheelzoom/) — Zoom when the mouse wheel turns with Ctrl held, wherever the pointer is.

## Functions

- [`percent`](function-percent/) — Give the zoom now in force.
- [`factor`](function-factor/) — Give the zoom as a multiplier.
- [`px`](function-px/) — Scale a length in pixels by the zoom.
- [`css`](function-css/) — Scale every pixel and point length in a stylesheet by the zoom.
- [`apply_font`](function-apply_font/) — Make the application font as large as the zoom says, from the size it had at 100%.
- [`set_percent`](function-set_percent/) — Zoom to the step nearest a percentage, save it and say so.
- [`step`](function-step/) — Zoom in or out by one step.
- [`reset`](function-reset/) — Go back to 100%.
- [`load`](function-load/) — Take the saved zoom into force, without announcing it, ignoring anything that is not a step.

<details markdown="1">
<summary>Module notes and examples</summary>

The zoom is a percentage, 100 by default, that moves through a list of
steps. It scales the application font, every pixel
and point length in the stylesheet, and the sizes the interface fixes in
pixels, which are written with `px` here so that
they follow it. The notation that is drawn by hand takes its size from
the same percentage. Pressing Ctrl and Plus or Ctrl and
Minus, or turning the mouse wheel with Ctrl held, moves one step, and
Ctrl and 0 goes back to 100%. The choice is saved.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_percent(100)
False
>>> px(20), px(0)
(20, 0)
>>> css(
...     "QLabel { font-size: 14pt; border: 1px solid; }"
... )
'QLabel { font-size: 14pt; border: 1px solid; }'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"percent": "function-percent/", "factor": "function-factor/", "px": "function-px/", "css": "function-css/", "apply_font": "function-apply_font/", "set_percent": "function-set_percent/", "step": "function-step/", "reset": "function-reset/", "load": "function-load/", "wheelzoom": "class-wheelzoom/", "wheelzoomfollow": "class-wheelzoom/#wheelzoomfollow", "wheelzoomwatch": "class-wheelzoom/#wheelzoomwatch", "wheelzoomeventfilter": "class-wheelzoom/#wheelzoomeventfilter"}</script>
{% include api-fragments.html %}
