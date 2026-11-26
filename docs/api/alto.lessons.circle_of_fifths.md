---
title: alto.lessons.circle_of_fifths
parent: api
package: alto.lessons
api_components: [{"title": "fifth_task", "url": "/api/alto.lessons.circle_of_fifths/function-fifth_task/"}, {"title": "flats_task", "url": "/api/alto.lessons.circle_of_fifths/function-flats_task/"}, {"title": "key_name", "url": "/api/alto.lessons.circle_of_fifths/function-key_name/"}, {"title": "neighbor_task", "url": "/api/alto.lessons.circle_of_fifths/function-neighbor_task/"}, {"title": "relative_task", "url": "/api/alto.lessons.circle_of_fifths/function-relative_task/"}, {"title": "sharps_task", "url": "/api/alto.lessons.circle_of_fifths/function-sharps_task/"}, {"title": "summary", "url": "/api/alto.lessons.circle_of_fifths/function-summary/"}]
permalink: /api/alto.lessons.circle_of_fifths/
---
{% raw %}
The lesson on the circle of fifths, taught from nothing.

## Functions

- [`key_name`](function-key_name/) — Return the first name of the key in a cell, written out.
- [`summary`](function-summary/) — Say a key and its key signature in one line.
- [`fifth_task`](function-fifth_task/) — Ask for the letter a fifth above a random letter, answered with buttons.
- [`sharps_task`](function-sharps_task/) — Ask for the major key with a given number of sharps, answered on the circle.
- [`flats_task`](function-flats_task/) — Ask for the major key with a given number of flats, answered on the circle.
- [`relative_task`](function-relative_task/) — Ask for the relative minor of a major key, answered on the circle.
- [`neighbor_task`](function-neighbor_task/) — Ask for the key a fifth above or below a random key, answered on the circle.

<details markdown="1">
<summary>Module notes and examples</summary>

It covers what a key is, what a fifth is, how the circle counts sharps
and flats, and what the inner ring and the neighbors of a
key mean.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(CIRCLE_OF_FIFTHS.steps)
8
>>> summary("outer", place=2)
'<b>D major</b>: 2 sharps (F♯, C♯)'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"key_name": "function-key_name/", "summary": "function-summary/", "fifth_task": "function-fifth_task/", "sharps_task": "function-sharps_task/", "flats_task": "function-flats_task/", "relative_task": "function-relative_task/", "neighbor_task": "function-neighbor_task/"}</script>
{% include api-fragments.html %}
