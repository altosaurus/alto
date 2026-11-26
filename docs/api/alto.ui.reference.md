---
title: alto.ui.reference
parent: api
package: alto.ui
api_components: [{"title": "ClefReferencePanel", "url": "/api/alto.ui.reference/class-clefreferencepanel/"}, {"title": "ExplorableCircle", "url": "/api/alto.ui.reference/class-explorablecircle/"}, {"title": "NoteReferencePanel", "url": "/api/alto.ui.reference/class-notereferencepanel/"}, {"title": "PluginReferencePanel", "url": "/api/alto.ui.reference/class-pluginreferencepanel/"}, {"title": "ReferencePanel", "url": "/api/alto.ui.reference/class-referencepanel/"}, {"title": "ScaleReferencePanel", "url": "/api/alto.ui.reference/class-scalereferencepanel/"}, {"title": "reference_panel_for", "url": "/api/alto.ui.reference/function-reference_panel_for/"}]
permalink: /api/alto.ui.reference/
---
{% raw %}
The reference pane: an interactive circle of fifths to look things up
on, with an explanation under it.

## Classes

- [`ExplorableCircle`](class-explorablecircle/) — A circle of fifths that shows every key and lets you pick one.
- [`ReferencePanel`](class-referencepanel/) — The reference for the circle of fifths: a short description, the circle to explore, and what the picked key means.
- [`ClefReferencePanel`](class-clefreferencepanel/) — The reference for the clefs: how they are made, and a picture of each with where its symbol goes.
- [`ScaleReferencePanel`](class-scalereferencepanel/) — Scale identification hints and a link to the guided lesson.
- [`NoteReferencePanel`](class-notereferencepanel/) — Hints for reading notes or intervals and a link to the associated lesson.
- [`PluginReferencePanel`](class-pluginreferencepanel/) — What a plugin's exercise offers to look up: what it asks, and a button for each lesson that teaches it.

## Functions

- [`reference_panel_for`](function-reference_panel_for/) — Return the reference pane for an exercise.

<details markdown="1">
<summary>Module notes and examples</summary>

Click a key on either ring, or move with the arrow keys, and the circle
lights that key's chords, shows its key signature in
the middle, and the text underneath explains it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = ExplorableCircle()
>>> circle.select("outer", place=2)
>>> circle.title, circle.signature
('D major', 2)
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"explorablecircle": "class-explorablecircle/", "explorablecircleset_interactive": "class-explorablecircle/#explorablecircleset_interactive", "explorablecircleclear": "class-explorablecircle/#explorablecircleclear", "explorablecircleselect": "class-explorablecircle/#explorablecircleselect", "explorablecirclecell_at": "class-explorablecircle/#explorablecirclecell_at", "explorablecirclelift_of": "class-explorablecircle/#explorablecirclelift_of", "explorablecirclemousepressevent": "class-explorablecircle/#explorablecirclemousepressevent", "explorablecirclemousemoveevent": "class-explorablecircle/#explorablecirclemousemoveevent", "explorablecircleleaveevent": "class-explorablecircle/#explorablecircleleaveevent", "explorablecirclekeypressevent": "class-explorablecircle/#explorablecirclekeypressevent", "referencepanel": "class-referencepanel/", "clefreferencepanel": "class-clefreferencepanel/", "scalereferencepanel": "class-scalereferencepanel/", "notereferencepanel": "class-notereferencepanel/", "pluginreferencepanel": "class-pluginreferencepanel/", "reference_panel_for": "function-reference_panel_for/"}</script>
{% include api-fragments.html %}
