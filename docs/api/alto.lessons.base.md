---
title: alto.lessons.base
parent: api
package: alto.lessons
order: 12
permalink: /api/alto.lessons.base/
---
{% raw %}
What a lesson is made of: steps, and the small tasks inside them.

A task is a soft exercise. It cannot be failed: a wrong answer gets a hint, a second wrong answer gets the answer, and nothing is
scored or recorded.

**Examples**

```pycon
>>> task = Task(prompt="Click the key.", cells=frozenset({("outer", 1)}), hint="Count.", explanation="One step.")
>>> task.check(("outer", 1)), task.check(("outer", 2))
(True, False)
```

## Task

```python
Task(
    prompt: str,
    hint: str,
    explanation: str,
    cells: frozenset[tuple[str, int]] = frozenset(),
    choices: tuple[str, ...] = (),
    correct: str = '',
)
```

One small question inside a lesson step.

It is answered either by clicking a cell of the circle (`cells`) or by pressing one of `choices`.

**Attributes**

- `prompt` (*str*): The question, as simple HTML.
- `hint` (*str*): What to say after a wrong answer.
- `explanation` (*str*): What to say after the right answer, or once the answer has been given away.
- `cells` (*frozenset of tuple of (str, int)*): The cells that are right, each a ring ("outer" or "inner") and a place clockwise from the top.
- `choices` (*tuple of str*): The buttons to choose from, for a question that is not answered on the circle.
- `correct` (*str*): The right button, if there are choices.

**Examples**

```pycon
>>> Task(prompt="Which?", hint="Count.", explanation="Five.", choices=("A", "B"), correct="B").check("B")
True
```

### Task.check

```python
def check(answer: tuple[str, int] | str) -> bool
```

Say whether an answer is right.

**Parameters**

- `answer` (*tuple of (str, int) or str*): A cell that was clicked, or the text of a button that was pressed.

**Returns**

- *bool*: True for a right answer.

**Examples**

```pycon
>>> Task(prompt="?", hint="", explanation="", cells=frozenset({("inner", 0)})).check(("inner", 0))
True
>>> Task(prompt="?", hint="", explanation="", choices=("A", "B"), correct="A").check(("outer", 0))
False
```

## Step

```python
Step(
    title: str,
    text: str,
    circle: str = 'none',
    hear: tuple[tuple[str, ...], ...] = (),
    hear_label: str = 'Hear it',
    make_task: Callable[[random.Random], Task] | None = field(default=None, compare=False),
    closing: bool = False,
)
```

One page of a lesson.

**Attributes**

- `title` (*str*): The heading.
- `text` (*str*): What to read, as simple HTML.
- `circle` (*str*): How the circle of fifths is shown: "none" for no circle, "rest" for a picture that does not respond, "explore" for one that can be clicked, or "walk" for one that can also be walked round with two buttons.
- `hear` (*tuple of tuple of str*): Notes to play from a Hear it button, as columns of note names such as "C4"; empty for no button.
- `hear_label` (*str*): What the Hear it button says.
- `make_task` (*callable or None*): Makes a fresh task from a random generator each time one is wanted; None for a step with no task.
- `closing` (*bool*): True for the last step, which offers to practise.

**Examples**

```pycon
>>> Step(title="Hello", text="<p>Hi.</p>").circle
'none'
```

## Lesson

```python
Lesson(
    key: str,
    title: str,
    about: str,
    summary: str,
    category: str,
    steps: tuple[Step, ...],
    exercise: str,
)
```

A lesson: a title, a line about it, and its steps.

**Attributes**

- `key` (*str*): A short name to save progress under.
- `title` (*str*): The title.
- `about` (*str*): A line or two saying what the lesson covers.
- `summary` (*str*): A short line for its card.
- `category` (*str*): The group it belongs to on the list, such as "Scales & Keys".
- `steps` (*tuple of Step*): The pages, in order.
- `exercise` (*str*): The class name of the exercise that practises it, which the last page offers.

**Examples**

```pycon
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
