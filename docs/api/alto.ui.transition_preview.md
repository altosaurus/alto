---
title: alto.ui.transition_preview
parent: api
package: alto.ui
api_components: [{"title": "Stage", "url": "/api/alto.ui.transition_preview/class-stage/"}, {"title": "TransitionPreview", "url": "/api/alto.ui.transition_preview/class-transitionpreview/"}, {"title": "make_sides", "url": "/api/alto.ui.transition_preview/function-make_sides/"}]
permalink: /api/alto.ui.transition_preview/
---
{% raw %}
A preview of a transition for the settings.

## Classes

- [`Stage`](class-stage/) — The page of the mock window: it draws the cards that are resting, and the transition plays on a canvas over it.
- [`TransitionPreview`](class-transitionpreview/) — A mock home page that plays a transition between two sets of the app's cards, once.

## Functions

- [`make_sides`](function-make_sides/) — Make the cards for the two sides of the preview: the app's own exercise cards, and its lesson cards.

<details markdown="1">
<summary>Module notes and examples</summary>

It is a mock of the home page, with the app's own cards, that switches
from the exercises to the lessons once.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> preview = TransitionPreview()
>>> preview.show_transition("cascade")
>>> preview.transition.key
'cascade'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"make_sides": "function-make_sides/", "stage": "class-stage/", "stageresizeevent": "class-stage/#stageresizeevent", "stagepaintevent": "class-stage/#stagepaintevent", "transitionpreview": "class-transitionpreview/", "transitionpreviewshow_transition": "class-transitionpreview/#transitionpreviewshow_transition", "transitionpreviewreplay": "class-transitionpreview/#transitionpreviewreplay", "transitionpreviewgo_to": "class-transitionpreview/#transitionpreviewgo_to", "transitionpreviewresizeevent": "class-transitionpreview/#transitionpreviewresizeevent"}</script>
{% include api-fragments.html %}
