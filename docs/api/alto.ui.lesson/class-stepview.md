---
title: StepView
parent: alto.ui.lesson
api_module: alto.ui.lesson
package: alto.ui
permalink: /api/alto.ui.lesson/class-stepview/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
StepView(
    step: Step,
    *,
    rng: random.Random | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="StepView" line=363 %}{% raw %}

</div>

Bases: `QWidget`

One step of a lesson: its words, a sound to hear, the circle, and a
task.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `step` | `Step` | The step. |
| `circle` | `ExplorableCircle or None` | The circle, for a step that has one. |
| `staves` | `list of StaffWidget` | The staves beside the words, for a step that has them: one for each of its `staves`, or the one that follows the task. |
| `left_scroll` | `QScrollArea` | Holds the words and controls on the left, so they scroll if the window is too short for them. |
| `task` | `Task or None` | The task now being asked, for a step that has them. |
| `feedback` | `QLabel` | What is said about the last answer. |
| `info` | `QLabel` | What is said about the key last picked on the circle. |
| `again` | `QPushButton` | Repeats a fixed question or draws another question after the answer is explained. |
| `practice` | `Signal` | Emitted by the Practice button on the last step. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.lessons.circle_of_fifths import (
...     CIRCLE_OF_FIFTHS,
... )
>>> view = StepView(
...     CIRCLE_OF_FIFTHS.steps[1],
...     rng=random.Random(1),
... )
>>> view.task is not None and len(
...     view.choice_buttons
... ) == 4
True
```

**Constructor**

Build the step and ask its first task.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `step` | `Step` | What to show. |
| `rng` | `random.Random or None, default None` | Chooses the tasks; None for a new one. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.lessons.circle_of_fifths import (
...     CIRCLE_OF_FIFTHS,
... )
>>> StepView(
...     CIRCLE_OF_FIFTHS.steps[0]
... ).circle is not None
True
```

## StepView.hear

<div class="api-signature" markdown="1">

```python
def hear() -> None
```

{% endraw %}{% include api-source.html name="StepView.hear" line=711 %}{% raw %}

</div>

Play the step's notes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.lessons.circle_of_fifths import (
...     CIRCLE_OF_FIFTHS,
... )
>>> from unittest.mock import patch
>>> with patch.object(sounds, "enabled", False):
...     StepView(
...         CIRCLE_OF_FIFTHS.steps[1]
...     ).hear()
```

## StepView.walk

<div class="api-signature" markdown="1">

```python
def walk(step: int) -> None
```

{% endraw %}{% include api-source.html name="StepView.walk" line=791 %}{% raw %}

</div>

Move the pick one fifth around the outer ring.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `step` | `int` | 1 for a fifth up (clockwise), -1 for a fifth down. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.lessons.circle_of_fifths import (
...     CIRCLE_OF_FIFTHS,
... )
>>> view = StepView(CIRCLE_OF_FIFTHS.steps[2])
>>> view.walk(1)
>>> # noinspection PyUnresolvedReferences
>>> view.circle.cell
('outer', 1)
>>> view.walk(-1)
>>> view.walk(-1)
>>> # noinspection PyUnresolvedReferences
>>> view.circle.cell
('outer', 11)
```

## StepView.ask

<div class="api-signature" markdown="1">

```python
def ask() -> None
```

{% endraw %}{% include api-source.html name="StepView.ask" line=864 %}{% raw %}

</div>

Ask a new task, with a fresh circle and clean feedback.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.lessons.circle_of_fifths import (
...     CIRCLE_OF_FIFTHS,
... )
>>> view = StepView(
...     CIRCLE_OF_FIFTHS.steps[3],
...     rng=random.Random(1),
... )
>>> first = view.task
>>> view.ask()
>>> view.task is not None and view.again.isHidden()
True
```
{% endraw %}
