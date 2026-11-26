---
title: Task
parent: alto.lessons.base
api_module: alto.lessons.base
package: alto.lessons
permalink: /api/alto.lessons.base/class-task/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Task(
    prompt: str,
    hint: str,
    explanation: str,
    cells: frozenset[tuple[str, int]] = frozenset(),
    choices: tuple[str, ...] = (),
    correct: str = '',
    clef: str = '',
    key: int = 0,
    targets: tuple[tuple[float, float, float], ...] = (),
)
```

{% endraw %}{% include api-source.html name="Task" line=40 %}{% raw %}

</div>

One small question inside a lesson step.

It is answered either by clicking a cell of the circle (`cells`) or
by pressing one of `choices`.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `prompt` | `str` | The question, as simple HTML. |
| `hint` | `str` | What to say after a wrong answer. |
| `explanation` | `str` | What to say after the right answer, or once the answer has been given away. |
| `cells` | `frozenset of tuple of (str, int)` | The cells that are right, each a ring ("outer" or "inner") and a place clockwise from the top. |
| `choices` | `tuple of str` | The buttons to choose from, for a question that is not answered on the circle. |
| `correct` | `str` | The right button, if there are choices. |
| `clef` | `str` | For a step that shows a staff beside a task, the clef to draw on it; empty for a blank staff. |
| `key` | `int` | Sharps (positive) or flats (negative) on the task staff. |
| `targets` | `tuple of tuple of (float, float, float)` | For a question answered by clicking the step's instrument picture: each right place as the x and y of its centre and its radius, in the picture's own pixels. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Task(
...     prompt="Which?",
...     hint="Count.",
...     explanation="Five.",
...     choices=("A", "B"),
...     correct="B",
... ).check("B")
True
>>> Task(
...     prompt="Click it.",
...     hint="",
...     explanation="",
...     targets=((10.0, 10.0, 5.0),),
... ).hits(12.0, y=11.0)
True
```

## Task.hits

<div class="api-signature" markdown="1">

```python
def hits(
    x: float,
    *,
    y: float,
) -> bool
```

{% endraw %}{% include api-source.html name="Task.hits" line=103 %}{% raw %}

</div>

Say whether a click on the instrument picture is on one of the
right places.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `x` | `float` | The click's x in the picture's pixels. |
| `y` | `float` | The click's y in the picture's pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the click is within the radius of a target. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Task(
...     prompt="?",
...     hint="",
...     explanation="",
...     targets=((10.0, 10.0, 5.0),),
... ).hits(30.0, y=10.0)
False
```

## Task.check

<div class="api-signature" markdown="1">

```python
def check(answer: tuple[str, int] | str) -> bool
```

{% endraw %}{% include api-source.html name="Task.check" line=135 %}{% raw %}

</div>

Say whether an answer is right.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `answer` | `tuple of (str, int) or str` | A cell that was clicked, or the text of a button that was pressed. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True for a right answer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Task(
...     prompt="?",
...     hint="",
...     explanation="",
...     cells=frozenset({("inner", 0)}),
... ).check(("inner", 0))
True
>>> Task(
...     prompt="?",
...     hint="",
...     explanation="",
...     choices=("A", "B"),
...     correct="A",
... ).check(("outer", 0))
False
```
{% endraw %}
