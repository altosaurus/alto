---
title: alto.ui.lesson
parent: api
package: alto.ui
order: 37
permalink: /api/alto.ui.lesson/
---
{% raw %}
The lesson pages: a page that walks through one lesson step by step.

A step has some words, sometimes a sound to hear, sometimes the circle of fifths to explore, and sometimes a small task. The
tasks cannot be failed and are not recorded.

**Examples**

```pycon
>>> LessonsPage("circle-of-fifths", step=0).view.counter.text()
'Step 1 of 8'
```

## saved_step

```python
def saved_step(lesson: Lesson) -> int
```

Return the step a lesson was left at, from the saved settings.

**Parameters**

- `lesson` (*Lesson*): The lesson.

**Returns**

- *int*: The step number from 0, or 0 if none is saved or it no longer exists.

**Examples**

```pycon
>>> saved_step(LESSONS[0]) in range(len(LESSONS[0].steps))
True
```

## save_step

```python
def save_step(
    lesson: Lesson,
    *,
    step: int,
) -> None
```

Remember the step a lesson is at.

**Parameters**

- `lesson` (*Lesson*): The lesson.
- `step` (*int*): The step number from 0. Keyword-only.

**Examples**

```pycon
>>> save_step(LESSONS[0], step=0)
>>> saved_step(LESSONS[0])
0
```

## StepView

```python
StepView(
    step: Step,
    *,
    rng: random.Random | None = None,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

One step of a lesson: its words, a sound to hear, the circle, and a task.

**Attributes**

- `step` (*Step*): The step.
- `circle` (*ExplorableCircle or None*): The circle, for a step that has one.
- `staves` (*list of StaffWidget*): The staves beside the words, for a step that has them: one for each of its `staves`, or the one that follows the task.
- `left_scroll` (*QScrollArea*): Holds the words and controls on the left, so they scroll if the window is too short for them.
- `task` (*Task or None*): The task now being asked, for a step that has them.
- `feedback` (*QLabel*): What is said about the last answer.
- `info` (*QLabel*): What is said about the key last picked on the circle.
- `again` (*QPushButton*): Asks another task; it appears once the task has been answered.
- `practise` (*Signal*): Emitted by the Practise button on the last step.

**Examples**

```pycon
>>> view = StepView(LESSONS[0].steps[1], rng=random.Random(1))
>>> view.task is not None and len(view.choice_buttons) == 4
True
```

**Constructor**

Build the step and ask its first task.

**Parameters**

- `step` (*Step*): What to show.
- `rng` (*random.Random or None, default None*): Chooses the tasks; None for a new one. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> StepView(LESSONS[0].steps[0]).circle is not None
True
```

### StepView.hear

```python
def hear() -> None
```

Play the step's notes.

**Examples**

```pycon
>>> StepView(LESSONS[0].steps[1]).hear()  # nothing sounds while muted, and nothing breaks
```

### StepView.walk

```python
def walk(step: int) -> None
```

Move the pick one fifth round the outer ring.

**Parameters**

- `step` (*int*): 1 for a fifth up (clockwise), -1 for a fifth down.

**Examples**

```pycon
>>> view = StepView(LESSONS[0].steps[2])
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

### StepView.ask

```python
def ask() -> None
```

Ask a new task, with a fresh circle and clean feedback.

**Examples**

```pycon
>>> view = StepView(LESSONS[0].steps[3], rng=random.Random(1))
>>> first = view.task
>>> view.ask()
>>> view.task is not None and view.again.isHidden()
True
```

## LessonView

```python
LessonView(
    lesson: Lesson,
    *,
    start: int = 0,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

One lesson being taken: the step, a progress bar, and Back and Next.

**Attributes**

- `lesson` (*Lesson*): The lesson.
- `current` (*int*): The step being shown, from 0.
- `heading` (*QLabel*): The step's title.
- `counter` (*QLabel*): "Step 2 of 8".
- `progress` (*QProgressBar*): How far through the lesson.
- `back_button` (*QPushButton*): Goes to the step before, or out to the list from the first step.
- `next_button` (*QPushButton*): Goes to the next step, or finishes on the last one.
- `leave` (*Signal*): Emitted to leave the lesson.
- `stepped` (*Signal*): Emitted with the number of the step each time one is shown.
- `practise` (*Signal*): Emitted when the last step's Practise button is pressed, with the exercise's class name.

**Examples**

```pycon
>>> view = LessonView(LESSONS[0])
>>> view.counter.text()
'Step 1 of 8'
>>> view.go(to=1)
>>> view.heading.text(), view.counter.text()
('A fifth', 'Step 2 of 8')
```

**Constructor**

Build the view at a step.

**Parameters**

- `lesson` (*Lesson*): The lesson to take.
- `start` (*int, default 0*): The step to begin at. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```pycon
>>> LessonView(LESSONS[0], start=3).current
3
```

### LessonView.go

```python
def go(
    *,
    to: int,
) -> None
```

Show a step. Going before the first leaves to the list, and going past the last finishes the lesson.

**Parameters**

- `to` (*int*): The step to show, from 0. Keyword-only.

**Examples**

```pycon
>>> view = LessonView(LESSONS[0])
>>> view.go(to=2)
>>> view.current
2
```

## LessonsPage

```python
LessonsPage(
    key: str,
    *,
    step: int | None = None,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

The page of an open lesson, with a button to leave it.

**Attributes**

- `view` (*LessonView*): The lesson being taken.
- `sidebar_button` (*SidebarToggle*): Shows or hides the list on the left; the main window wires it up.
- `back` (*Signal*): Emitted to leave the lesson, to wherever it was opened from.
- `practise_requested` (*Signal*): Emitted with the class name of an exercise to practise.

**Examples**

```pycon
>>> page = LessonsPage("circle-of-fifths")
>>> page.view.lesson.key
'circle-of-fifths'
```

**Constructor**

Build the page for a lesson, at the step it was left at unless another is asked for.

**Parameters**

- `key` (*str*): The lesson's key.
- `step` (*int or None, default None*): The step to start at; None for where it was left. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Raises**

- *KeyError*: If there is no lesson with that key.

**Constructor examples**

```pycon
>>> LessonsPage("circle-of-fifths", step=2).view.current
2
```
{% endraw %}
