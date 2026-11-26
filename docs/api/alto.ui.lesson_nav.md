---
title: alto.ui.lesson_nav
parent: api
package: alto.ui
api_components: [{"title": "LessonNav", "url": "/api/alto.ui.lesson_nav/class-lessonnav/"}, {"title": "section_item", "url": "/api/alto.ui.lesson_nav/function-section_item/"}]
permalink: /api/alto.ui.lesson_nav/
---
{% raw %}
The list on the left in lesson mode: the lessons, and the steps of the
one that is open.

## Classes

- [`LessonNav`](class-lessonnav/) — A flat list of the lessons by category, with the steps of the open lesson listed under it.

## Functions

- [`section_item`](function-section_item/) — Make a section label for a list: small, gray capitals that cannot be selected.

<details markdown="1">
<summary>Module notes and examples</summary>

It is the lessons' counterpart of the exercise list, and looks the same.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> nav = LessonNav()
>>> nav.show_lesson("circle-of-fifths")
>>> nav.count() > len(LESSONS)
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"section_item": "function-section_item/", "lessonnav": "class-lessonnav/", "lessonnavshow_lesson": "class-lessonnav/#lessonnavshow_lesson", "lessonnavselect_step": "class-lessonnav/#lessonnavselect_step"}</script>
{% include api-fragments.html %}
