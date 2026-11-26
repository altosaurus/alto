---
title: alto.lessons.clef_basics
parent: api
package: alto.lessons
api_components: [{"title": "identify_task", "url": "/api/alto.lessons.clef_basics/function-identify_task/"}, {"title": "line_task", "url": "/api/alto.lessons.clef_basics/function-line_task/"}, {"title": "symbol_task", "url": "/api/alto.lessons.clef_basics/function-symbol_task/"}]
permalink: /api/alto.lessons.clef_basics/
---
{% raw %}
The lesson on clefs, taught from nothing.

## Functions

- [`symbol_task`](function-symbol_task/) — Ask which of the three symbols a clef is made with.
- [`identify_task`](function-identify_task/) — Ask which clef is drawn on a staff.
- [`line_task`](function-line_task/) — Ask which line of a blank staff a named clef is written on.

<details markdown="1">
<summary>Module notes and examples</summary>

It covers what a clef does, the three symbols (the G, C and F clef) and
the line each clef puts them on, the way every C clef
points at middle C, and the rarer clefs.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(CLEF_BASICS.steps)
10
>>> symbol_task(random.Random(1)).choices
('G clef', 'C clef', 'F clef')
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"symbol_task": "function-symbol_task/", "identify_task": "function-identify_task/", "line_task": "function-line_task/"}</script>
{% include api-fragments.html %}
