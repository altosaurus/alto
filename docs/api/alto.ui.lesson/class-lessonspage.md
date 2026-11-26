---
title: LessonsPage
parent: alto.ui.lesson
api_module: alto.ui.lesson
package: alto.ui
permalink: /api/alto.ui.lesson/class-lessonspage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
LessonsPage(
    key: str,
    *,
    step: int | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="LessonsPage" line=1308 %}{% raw %}

</div>

Bases: `QWidget`

The page of an open lesson, with a button to leave it.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `view` | `LessonView` | The lesson being taken. |
| `back` | `Signal` | Emitted to leave the lesson, to wherever it was opened from. |
| `practice_requested` | `Signal` | Emitted with the class name of an exercise to practice. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = LessonsPage("circle-of-fifths")
>>> page.view.lesson.key
'circle-of-fifths'
```

**Constructor**

Build the page for a lesson, at the step it was left at unless
another is asked for.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The lesson's key. |
| `step` | `int or None, default None` | The step to start at; None for where it was left. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Raises**

- *KeyError*: If there is no lesson with that key.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> LessonsPage(
...     "circle-of-fifths", step=2
... ).view.current
2
```
{% endraw %}
