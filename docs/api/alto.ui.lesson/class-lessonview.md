---
title: LessonView
parent: alto.ui.lesson
api_module: alto.ui.lesson
package: alto.ui
permalink: /api/alto.ui.lesson/class-lessonview/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
LessonView(
    lesson: Lesson,
    *,
    start: int = 0,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="LessonView" line=1148 %}{% raw %}

</div>

Bases: `QWidget`

One lesson being taken: the step, a progress bar, and Back and Next.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `lesson` | `Lesson` | The lesson. |
| `current` | `int` | The step being shown, from 0. |
| `heading` | `QLabel` | The step's title. |
| `counter` | `QLabel` | "Step 2 of 8". |
| `progress` | `QProgressBar` | How far through the lesson. |
| `back_button` | `QPushButton` | Goes to the step before, or out to the list from the first step. |
| `next_button` | `QPushButton` | Goes to the next step, or finishes on the last one. |
| `leave` | `Signal` | Emitted to leave the lesson. |
| `stepped` | `Signal` | Emitted with the number of the step each time one is shown. |
| `practice` | `Signal` | Emitted when the last step's Practice button is pressed, with the exercise's class name. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.lessons.circle_of_fifths import (
...     CIRCLE_OF_FIFTHS,
... )
>>> view = LessonView(CIRCLE_OF_FIFTHS)
>>> view.counter.text()
'Step 1 of 8'
>>> view.go(to=1)
>>> view.heading.text(), view.counter.text()
('A fifth', 'Step 2 of 8')
```

**Constructor**

Build the view at a step.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `lesson` | `Lesson` | The lesson to take. |
| `start` | `int, default 0` | The step to begin at. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> LessonView(LESSONS[0], start=3).current
3
```

## LessonView.go

<div class="api-signature" markdown="1">

```python
def go(
    *,
    to: int,
) -> None
```

{% endraw %}{% include api-source.html name="LessonView.go" line=1249 %}{% raw %}

</div>

Show a step. Going before the first leaves to the list, and
going past the last finishes the lesson.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `to` | `int` | The step to show, from 0. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> view = LessonView(LESSONS[0])
>>> view.go(to=2)
>>> view.current
2
```
{% endraw %}
