---
title: alto.instrument_packs
parent: api
package: alto
api_components: [{"title": "AnswerAnimation", "url": "/api/alto.instrument_packs/class-answeranimation/"}, {"title": "PackFiles", "url": "/api/alto.instrument_packs/class-packfiles/"}, {"title": "PackInstrument", "url": "/api/alto.instrument_packs/class-packinstrument/"}, {"title": "PackKeyboard", "url": "/api/alto.instrument_packs/class-packkeyboard/"}, {"title": "PackKeyboardStyle", "url": "/api/alto.instrument_packs/class-packkeyboardstyle/"}, {"title": "PackString", "url": "/api/alto.instrument_packs/class-packstring/"}, {"title": "PackView", "url": "/api/alto.instrument_packs/class-packview/"}, {"title": "identifier", "url": "/api/alto.instrument_packs/function-identifier/"}, {"title": "image_point", "url": "/api/alto.instrument_packs/function-image_point/"}, {"title": "pitch", "url": "/api/alto.instrument_packs/function-pitch/"}, {"title": "plain_text", "url": "/api/alto.instrument_packs/function-plain_text/"}, {"title": "read_focus", "url": "/api/alto.instrument_packs/function-read_focus/"}, {"title": "read_icon", "url": "/api/alto.instrument_packs/function-read_icon/"}, {"title": "read_instrument", "url": "/api/alto.instrument_packs/function-read_instrument/"}, {"title": "read_keyboard_style", "url": "/api/alto.instrument_packs/function-read_keyboard_style/"}, {"title": "read_keyboards", "url": "/api/alto.instrument_packs/function-read_keyboards/"}, {"title": "read_marker_size", "url": "/api/alto.instrument_packs/function-read_marker_size/"}, {"title": "read_picture_file", "url": "/api/alto.instrument_packs/function-read_picture_file/"}, {"title": "read_positions", "url": "/api/alto.instrument_packs/function-read_positions/"}, {"title": "read_sound_info", "url": "/api/alto.instrument_packs/function-read_sound_info/"}, {"title": "read_text", "url": "/api/alto.instrument_packs/function-read_text/"}, {"title": "read_views", "url": "/api/alto.instrument_packs/function-read_views/"}]
permalink: /api/alto.instrument_packs/
---
{% raw %}
Media and fingerboard geometry supplied by third-party instrument packs.

## Classes

- [`PackString`](class-packstring/) — One open pitch with its nut and bridge locations in the original image pixels.
- [`AnswerAnimation`](class-answeranimation/) — An author-supplied animated overlay and its alignment on the instrument.
- [`PackView`](class-packview/) — Another picture of an instrument, such as its back, with its own pixel size.
- [`PackKeyboard`](class-packkeyboard/) — One keyboard of an instrument, drawn by Alto from the range of keys the plugin gives it.
- [`PackKeyboardStyle`](class-packkeyboardstyle/) — How a plugin's keyboards look: the colors of the keys and case, and the proportions of the keys.
- [`PackInstrument`](class-packinstrument/) — A pack-qualified identity and the resources shared by its exercises.
- [`PackFiles`](class-packfiles/) — Resolve only manifest-declared assets, from a folder or the root of a ZIP.

## Functions

- [`read_keyboard_style`](function-read_keyboard_style/) — Validate the optional look of an instrument's keyboards.
- [`identifier`](function-identifier/) — Validate one component of a pack-qualified id.
- [`pitch`](function-pitch/) — Read a pitch spelled with an octave.
- [`image_point`](function-image_point/) — Validate a marker or string endpoint against the image dimensions.
- [`read_sound_info`](function-read_sound_info/) — Validate the optional facts a pack gives about where its recordings came from.
- [`plain_text`](function-plain_text/) — Check that a manifest entry is nonblank plain text of a reasonable length.
- [`read_text`](function-read_text/) — Check one piece of plain text and return it trimmed.
- [`read_focus`](function-read_focus/) — Validate a picture question's region to show.
- [`read_marker_size`](function-read_marker_size/) — Validate a picture's marker size.
- [`read_icon`](function-read_icon/) — Read a plugin's tile icon: a plain SVG of simple shapes, redrawn in the theme's ink.
- [`read_picture_file`](function-read_picture_file/) — Find and check a picture in the pack.
- [`read_views`](function-read_views/) — Validate the optional extra pictures of an instrument, such as a view of its back.
- [`read_keyboards`](function-read_keyboards/) — Validate the optional keyboards of an instrument, which Alto draws from their ranges.
- [`read_positions`](function-read_positions/) — Validate the optional named positions along a string, which label the ruler beside the fingerboard.
- [`read_instrument`](function-read_instrument/) — Validate one declared instrument against its own artwork and recordings.
{% endraw %}

<script type="application/json" id="api-fragments">{"packstring": "class-packstring/", "packstringpoint": "class-packstring/#packstringpoint", "answeranimation": "class-answeranimation/", "packview": "class-packview/", "packkeyboard": "class-packkeyboard/", "packkeyboardnaturals": "class-packkeyboard/#packkeyboardnaturals", "packkeyboardhas": "class-packkeyboard/#packkeyboardhas", "packkeyboardstyle": "class-packkeyboardstyle/", "read_keyboard_style": "function-read_keyboard_style/", "packinstrument": "class-packinstrument/", "packinstrumentkeyboard": "class-packinstrument/#packinstrumentkeyboard", "packinstrumentpicture": "class-packinstrument/#packinstrumentpicture", "identifier": "function-identifier/", "pitch": "function-pitch/", "packfiles": "class-packfiles/", "packfilesasset": "class-packfiles/#packfilesasset", "packfilesmanifest": "class-packfiles/#packfilesmanifest", "image_point": "function-image_point/", "read_sound_info": "function-read_sound_info/", "plain_text": "function-plain_text/", "read_text": "function-read_text/", "read_focus": "function-read_focus/", "read_marker_size": "function-read_marker_size/", "read_icon": "function-read_icon/", "read_picture_file": "function-read_picture_file/", "read_views": "function-read_views/", "read_keyboards": "function-read_keyboards/", "read_positions": "function-read_positions/", "read_instrument": "function-read_instrument/"}</script>
{% include api-fragments.html %}
