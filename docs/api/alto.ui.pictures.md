---
title: alto.ui.pictures
parent: api
package: alto.ui
api_components: [{"title": "ClefPictures", "url": "/api/alto.ui.pictures/class-clefpictures/"}, {"title": "KeySignaturePicture", "url": "/api/alto.ui.pictures/class-keysignaturepicture/"}, {"title": "NamePicture", "url": "/api/alto.ui.pictures/class-namepicture/"}, {"title": "RangePictures", "url": "/api/alto.ui.pictures/class-rangepictures/"}, {"title": "ValuePictures", "url": "/api/alto.ui.pictures/class-valuepictures/"}, {"title": "rhythm_picture", "url": "/api/alto.ui.pictures/function-rhythm_picture/"}, {"title": "symbol_icon", "url": "/api/alto.ui.pictures/function-symbol_icon/"}]
permalink: /api/alto.ui.pictures/
---
{% raw %}
Small pictures of musical things (clefs, note values, key signatures,
note ranges ...) for the settings panes.

## Classes

- [`ClefPictures`](class-clefpictures/) — The selected clefs, each on its own five-line staff, and a two-stave picture with a brace for the grand staff.
- [`ValuePictures`](class-valuepictures/) — Note values as engraved symbols (no staff), each with its head on the same baseline so they line up.
- [`KeySignaturePicture`](class-keysignaturepicture/) — A key signature as a plain row of its sharps or flats, with no staff or clef.
- [`RangePictures`](class-rangepictures/) — For each clef, a staff with its lowest and highest note, so the range can be read off at a glance.
- [`NamePicture`](class-namepicture/) — How notes are named: C, D and E on a staff, labeled with letters, solfège syllables or scale degrees.

## Functions

- [`symbol_icon`](function-symbol_icon/) — Draw a clef symbol on its own, without a staff, as an icon.
- [`rhythm_picture`](function-rhythm_picture/) — Render a single note, rest, tied pair, or beamed pair from an equation term.

<details markdown="1">
<summary>Module notes and examples</summary>

Each picture is drawn in fixed units and then scaled, so the same
picture serves as a summary in a menu row and, larger,
as the label of a choice. Colors come from the palette, so they work in
light and dark themes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     CLEF_NAMES["treble"],
...     VALUE_NAMES["sixteenth"],
... )
('Treble', '16th')
>>> ClefPictures(["treble", "bass"]).toolTip()
'Treble, Bass'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"symbol_icon": "function-symbol_icon/", "clefpictures": "class-clefpictures/", "clefpicturesset_clefs": "class-clefpictures/#clefpicturesset_clefs", "clefpicturesicon": "class-clefpictures/#clefpicturesicon", "clefpicturespaintevent": "class-clefpictures/#clefpicturespaintevent", "valuepictures": "class-valuepictures/", "valuepicturesset_values": "class-valuepictures/#valuepicturesset_values", "valuepicturesicon": "class-valuepictures/#valuepicturesicon", "valuepicturespaintevent": "class-valuepictures/#valuepicturespaintevent", "rhythm_picture": "function-rhythm_picture/", "keysignaturepicture": "class-keysignaturepicture/", "keysignaturepictureicon": "class-keysignaturepicture/#keysignaturepictureicon", "keysignaturepicturepaintevent": "class-keysignaturepicture/#keysignaturepicturepaintevent", "rangepictures": "class-rangepictures/", "rangepicturesset_items": "class-rangepictures/#rangepicturesset_items", "rangepicturespaintevent": "class-rangepictures/#rangepicturespaintevent", "namepicture": "class-namepicture/", "namepictureset_naming": "class-namepicture/#namepictureset_naming", "namepictureicon": "class-namepicture/#namepictureicon", "namepicturepaintevent": "class-namepicture/#namepicturepaintevent"}</script>
{% include api-fragments.html %}
