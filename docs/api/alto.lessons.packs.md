---
title: alto.lessons.packs
parent: api
package: alto.lessons
api_components: [{"title": "inline", "url": "/api/alto.lessons.packs/function-inline/"}, {"title": "read_lessons", "url": "/api/alto.lessons.packs/function-read_lessons/"}, {"title": "read_picture", "url": "/api/alto.lessons.packs/function-read_picture/"}]
permalink: /api/alto.lessons.packs/
---
{% raw %}
Turn the lessons that an instrument plugin declares into `Lesson`s that
Alto lists and shows.

## Functions

- [`inline`](function-inline/) — Escape plain text for a lesson page, turning ``**word**`` into bold type for a term being defined.
- [`read_lessons`](function-read_lessons/) — Validate the optional ``lessons`` list of a plugin manifest and build its lessons.
- [`read_picture`](function-read_picture/) — Build a step's instrument picture: a note on a string, or a marked place on the picture.

<details markdown="1">
<summary>Module notes and examples</summary>

A plugin describes each lesson in its manifest as plain text and small
objects: paragraphs, an optional picture of its own
instrument, notes to hear, and a question with buttons. This module
checks all of that and builds the same `Lesson` and `Step`
objects the built-in lessons use, so the lesson pages need to know
nothing about any particular plugin or instrument.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> inline("A **scroll** is the carved end.")
'A <b>scroll</b> is the carved end.'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"inline": "function-inline/", "read_lessons": "function-read_lessons/", "read_picture": "function-read_picture/"}</script>
{% include api-fragments.html %}
