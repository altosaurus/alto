---
title: alto.ui.circle
parent: api
package: alto.ui
api_components: [{"title": "FifthsCircle", "url": "/api/alto.ui.circle/class-fifthscircle/"}, {"title": "question_circle", "url": "/api/alto.ui.circle/function-question_circle/"}, {"title": "wedge_color", "url": "/api/alto.ui.circle/function-wedge_color/"}, {"title": "wedge_middle", "url": "/api/alto.ui.circle/function-wedge_middle/"}, {"title": "wedge_path", "url": "/api/alto.ui.circle/function-wedge_path/"}, {"title": "write_text", "url": "/api/alto.ui.circle/function-write_text/"}]
permalink: /api/alto.ui.circle/
---
{% raw %}
The circle of fifths: twelve wedges, the major keys on the outside and
their relative minors on the inside.

## Classes

- [`FifthsCircle`](class-fifthscircle/) — The circle of fifths, drawn for an exercise.

## Functions

- [`wedge_path`](function-wedge_path/) — Return the outline of one wedge of a ring.
- [`wedge_middle`](function-wedge_middle/) — Return the point in the middle of a wedge, at a given distance from the center.
- [`wedge_color`](function-wedge_color/) — Return the color of a wedge in a color scheme: quiet when it is not being talked about and bright when it is.
- [`write_text`](function-write_text/) — Write a line of text centered on a point, with its sharps and flats drawn as the notation font draws them.
- [`question_circle`](function-question_circle/) — Build a fixed-size circle for a question preview or export.

<details markdown="1">
<summary>Module notes and examples</summary>

C is at the top and each step clockwise is a fifth up, so the keys
gather sharps on the right and flats on the left. The
disc in the middle shows the staff and key signature of the key being
talked about. In an exercise one wedge is the question
and its name (or its Roman numeral) is blank until the answer is right.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> circle = FifthsCircle()
>>> circle.show_question(
...     "major", place=3, title="F♯ minor"
... )
>>> circle.target
('outer', 3)
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"wedge_path": "function-wedge_path/", "wedge_middle": "function-wedge_middle/", "wedge_color": "function-wedge_color/", "write_text": "function-write_text/", "fifthscircle": "class-fifthscircle/", "fifthscirclesizehint": "class-fifthscircle/#fifthscirclesizehint", "fifthscircleset_question": "class-fifthscircle/#fifthscircleset_question", "fifthscircleshow_question": "class-fifthscircle/#fifthscircleshow_question", "fifthscirclereset": "class-fifthscircle/#fifthscirclereset", "fifthscirclereveal": "class-fifthscircle/#fifthscirclereveal", "fifthscircleset_subtitle": "class-fifthscircle/#fifthscircleset_subtitle", "fifthscircleflash_wrong": "class-fifthscircle/#fifthscircleflash_wrong", "fifthscirclelift_of": "class-fifthscircle/#fifthscirclelift_of", "fifthscirclegeometry_of": "class-fifthscircle/#fifthscirclegeometry_of", "fifthscirclepaintevent": "class-fifthscircle/#fifthscirclepaintevent", "question_circle": "function-question_circle/"}</script>
{% include api-fragments.html %}
