---
title: alto.ui.lesson
parent: api
package: alto.ui
api_components: [{"title": "LessonView", "url": "/api/alto.ui.lesson/class-lessonview/"}, {"title": "LessonsPage", "url": "/api/alto.ui.lesson/class-lessonspage/"}, {"title": "StepView", "url": "/api/alto.ui.lesson/class-stepview/"}, {"title": "save_step", "url": "/api/alto.ui.lesson/function-save_step/"}, {"title": "saved_step", "url": "/api/alto.ui.lesson/function-saved_step/"}]
permalink: /api/alto.ui.lesson/
---
{% raw %}
The lesson pages: a page that walks through one lesson step by step.

## Classes

- [`StepView`](class-stepview/) — One step of a lesson: its words, a sound to hear, the circle, and a task.
- [`LessonView`](class-lessonview/) — One lesson being taken: the step, a progress bar, and Back and Next.
- [`LessonsPage`](class-lessonspage/) — The page of an open lesson, with a button to leave it.

## Functions

- [`saved_step`](function-saved_step/) — Return the step a lesson was left at, from the saved settings.
- [`save_step`](function-save_step/) — Remember the step a lesson is at.

<details markdown="1">
<summary>Module notes and examples</summary>

A step has some words, sometimes a sound to hear, sometimes the circle
of fifths to explore, and sometimes a small task. The
tasks cannot be failed and are not recorded.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> LessonsPage(
...     "circle-of-fifths", step=0
... ).view.counter.text()
'Step 1 of 8'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"saved_step": "function-saved_step/", "save_step": "function-save_step/", "stepview": "class-stepview/", "stepviewhear": "class-stepview/#stepviewhear", "stepviewwalk": "class-stepview/#stepviewwalk", "stepviewask": "class-stepview/#stepviewask", "lessonview": "class-lessonview/", "lessonviewgo": "class-lessonview/#lessonviewgo", "lessonspage": "class-lessonspage/"}</script>
{% include api-fragments.html %}
