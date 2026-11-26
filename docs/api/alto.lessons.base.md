---
title: alto.lessons.base
parent: api
package: alto.lessons
api_components: [{"title": "Lesson", "url": "/api/alto.lessons.base/class-lesson/"}, {"title": "Staff", "url": "/api/alto.lessons.base/class-staff/"}, {"title": "Step", "url": "/api/alto.lessons.base/class-step/"}, {"title": "Task", "url": "/api/alto.lessons.base/class-task/"}]
permalink: /api/alto.lessons.base/
---
{% raw %}
What a lesson is made of: steps, and the small tasks inside them.

## Classes

- [`Task`](class-task/) — One small question inside a lesson step.
- [`Staff`](class-staff/) — A staff to show beside the words of a step: a clef, and perhaps a note, with a line of words under it.
- [`Step`](class-step/) — One page of a lesson.
- [`Lesson`](class-lesson/) — A lesson: a title, a line about it, and its steps.

<details markdown="1">
<summary>Module notes and examples</summary>

A task is a soft exercise. It cannot be failed: a wrong answer gets a
hint, a second wrong answer gets the answer, and nothing is
scored or recorded.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = Task(
...     prompt="Click the key.",
...     cells=frozenset({("outer", 1)}),
...     hint="Count.",
...     explanation="One step.",
... )
>>> (
...     task.check(("outer", 1)),
...     task.check(("outer", 2)),
... )
(True, False)
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"task": "class-task/", "taskhits": "class-task/#taskhits", "taskcheck": "class-task/#taskcheck", "staff": "class-staff/", "step": "class-step/", "lesson": "class-lesson/"}</script>
{% include api-fragments.html %}
