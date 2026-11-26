---
title: alto.ui.fingerboard
parent: api
package: alto.ui
api_components: [{"title": "FingerboardWidget", "url": "/api/alto.ui.fingerboard/class-fingerboardwidget/"}, {"title": "manual_style", "url": "/api/alto.ui.fingerboard/function-manual_style/"}, {"title": "neck_view", "url": "/api/alto.ui.fingerboard/function-neck_view/"}, {"title": "ruler_base", "url": "/api/alto.ui.fingerboard/function-ruler_base/"}, {"title": "ruler_reach", "url": "/api/alto.ui.fingerboard/function-ruler_reach/"}]
permalink: /api/alto.ui.fingerboard/
---
{% raw %}
Render a pack's instrument portrait using its calibrated string
endpoints.

## Classes

- [`FingerboardWidget`](class-fingerboardwidget/) — Draw the instrument and keep the teaching overlays on the same scale.

## Functions

- [`ruler_reach`](function-ruler_reach/) — Find how many half steps the ruler covers: an octave, or further if the pack names a position beyond it.
- [`ruler_base`](function-ruler_base/) — Locate where a ruler tick for one half step starts, beside the fingerboard rather than on it.
- [`neck_view`](function-neck_view/) — Choose the part of the picture a note question needs: the nut, the neck with its ruler, and the bridge.
- [`manual_style`](function-manual_style/) — Build the look of an instrument's drawn keyboards from its plugin's ``keyboard_style``.
{% endraw %}

<script type="application/json" id="api-fragments">{"ruler_reach": "function-ruler_reach/", "ruler_base": "function-ruler_base/", "neck_view": "function-neck_view/", "manual_style": "function-manual_style/", "fingerboardwidget": "class-fingerboardwidget/", "fingerboardwidgetsizehint": "class-fingerboardwidget/#fingerboardwidgetsizehint", "fingerboardwidgetshow_position": "class-fingerboardwidget/#fingerboardwidgetshow_position", "fingerboardwidgetresizeevent": "class-fingerboardwidget/#fingerboardwidgetresizeevent", "fingerboardwidgetset_pickable": "class-fingerboardwidget/#fingerboardwidgetset_pickable", "fingerboardwidgetshow_target": "class-fingerboardwidget/#fingerboardwidgetshow_target", "fingerboardwidgetmousepressevent": "class-fingerboardwidget/#fingerboardwidgetmousepressevent", "fingerboardwidgetset_sounding": "class-fingerboardwidget/#fingerboardwidgetset_sounding", "fingerboardwidgetfeedback_gap_ms": "class-fingerboardwidget/#fingerboardwidgetfeedback_gap_ms", "fingerboardwidgetanimate_silent_answer": "class-fingerboardwidget/#fingerboardwidgetanimate_silent_answer", "fingerboardwidgethideevent": "class-fingerboardwidget/#fingerboardwidgethideevent", "fingerboardwidgetpaintevent": "class-fingerboardwidget/#fingerboardwidgetpaintevent"}</script>
{% include api-fragments.html %}
