---
title: Lesson
parent: alto.lessons.base
api_module: alto.lessons.base
package: alto.lessons
permalink: /api/alto.lessons.base/class-lesson/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Lesson(
    key: str,
    title: str,
    about: str,
    summary: str,
    category: str,
    steps: tuple[Step, ...],
    exercise: str,
    related_exercises: tuple[str, ...] = (),
    icon: str = '',
)
```

{% endraw %}{% include api-source.html name="Lesson" line=306 %}{% raw %}

</div>

A lesson: a title, a line about it, and its steps.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `key` | `str` | A short name to save progress under. |
| `title` | `str` | The title. |
| `about` | `str` | A line or two saying what the lesson covers. |
| `summary` | `str` | A short line for its card. |
| `category` | `str` | The group it belongs to on the list, such as "Scales & Keys". |
| `steps` | `tuple of Step` | The pages, in order. |
| `exercise` | `str` | The primary exercise offered on the last page and used for the lesson icon. |
| `related_exercises` | `tuple of str` | Additional exercises offered on the last page, in display order. |
| `icon` | `str` | SVG shapes for the lesson's tile, in a 24 by 24 box with COLOR where the theme's ink goes. Empty uses the icon of the primary exercise. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> steps = (Step(title="One", text=""),)
>>> lesson = Lesson(
...     key="demo",
...     title="Demo",
...     about="A demo.",
...     summary="Demo.",
...     category="Demos",
...     steps=steps,
...     exercise="NoteNames",
... )
>>> lesson.steps[0].title
'One'
```
{% endraw %}
