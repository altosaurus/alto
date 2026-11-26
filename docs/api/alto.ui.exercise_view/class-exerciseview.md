---
title: ExerciseView
parent: alto.ui.exercise_view
api_module: alto.ui.exercise_view
package: alto.ui
permalink: /api/alto.ui.exercise_view/class-exerciseview/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ExerciseView(
    exercise: Exercise,
    *,
    rng: random.Random | None = None,
    parent: QWidget | None = None,
    learner: Learner | None = None,
)
```

{% endraw %}{% include api-source.html name="ExerciseView" line=431 %}{% raw %}

</div>

Bases: `QWidget`

The screen for practicing one exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `PANE_WIDTH` | `int` | The width of the settings pane when it is open, in pixels. |
| `REFERENCE_WIDTH` | `int` | The width of the reference pane when it is open, in pixels. |
| `exercise` | `Exercise` | The exercise being practiced. |
| `learner` | `Learner or None` | Records every answer and chooses what to ask next; None asks at random. |
| `rng` | `random.Random` | The random number generator for new questions. |
| `correct` | `int` | Questions answered right on the first try. |
| `total` | `int` | Questions answered. |
| `streak` | `int` | Right answers in a row. |
| `question` | `Question or None` | The question on screen. |
| `answered` | `bool` | True once this showing is finished, including a miss in SM-2 or FSRS. |
| `missed` | `bool` | True once the question has been answered wrong, so it no longer counts toward the score. |
| `buttons` | `list of QPushButton` | The answer buttons on screen. |
| `settings_panel` | `ExerciseSettingsPanel` | The exercise's settings, including how to advance after a correct answer. |
| `staff` | `StaffWidget` | Shows the notes of a question. |
| `keyboard` | `KeyboardWidget` | Shows the key of a keyboard question. |
| `input_staff` | `StaffInput` | The staff to click, for "place this note" questions. |
| `clef_input` | `ClefInput` | The blank staff a clef is put on, for "place this clef" questions. |
| `scale_input` | `ScaleInput` | The staff to click, for "place the notes of this scale" questions. |
| `fork` | `KeyFork` | The fork to pick a key signature on, for "build this key signature" questions. |
| `answer_button` | `QPushButton` | Hands in what was built with the fork or placed on the scale staff. |
| `book_btn` | `QToolButton or None` | Opens the exercise's reference in a pane on the right; None for an exercise that has none. |
| `reference_pane` | `QFrame or None` | The pane that holds the reference. |
| `lesson_requested` | `Signal` | Emitted with a lesson's key when the reference pane's lesson button is pressed. |
| `shuffle_requested` | `Signal` | Emitted when answer feedback ends or Next is clicked during shuffled practice. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(
...     NoteNames(), rng=random.Random(1)
... )
>>> view.score.text()
'0/0 (–)   streak 0'
```

**Constructor**

Build the screen and show the first question.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `exercise` | `Exercise` | The exercise to practice. |
| `rng` | `random.Random or None, default None` | The random number generator; a fresh one if None. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the screen. Keyword-only. |
| `learner` | `Learner or None, default None` | Where to record answers and what to ask next; None asks at random and records nothing. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     KeySignatures,
... )
>>> view = ExerciseView(
...     KeySignatures(), rng=random.Random(2)
... )
>>> # the exercise has settings behind the gear button
>>> view.settings_panel is not None
True
```

## ExerciseView.hideEvent

<div class="api-signature" markdown="1">

```python
def hideEvent(event: QHideEvent) -> None
```

{% endraw %}{% include api-source.html name="ExerciseView.hideEvent" line=1195 %}{% raw %}

</div>

Pause automatic advancement and answer timing while browsing
another page.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QHideEvent` | The notification that the exercise is being hidden. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(NoteNames())
>>> view.show()
>>> view.hide()
>>> view._advance.isActive()
False
```

## ExerciseView.showEvent

<div class="api-signature" markdown="1">

```python
def showEvent(event: QShowEvent) -> None
```

{% endraw %}{% include api-source.html name="ExerciseView.showEvent" line=1224 %}{% raw %}

</div>

Resume the exercise's answer clock and pending advance when it
reappears.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QShowEvent` | The notification that the exercise is visible again. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(NoteNames())
>>> view.show()
>>> view.hide()
>>> view.show()
>>> view._hidden_at is None
True
```

## ExerciseView.settings_state

<div class="api-signature" markdown="1">

```python
def settings_state() -> tuple[bool, int, int] | None
```

{% endraw %}{% include api-source.html name="ExerciseView.settings_state" line=1358 %}{% raw %}

</div>

Remember the exercise settings pane, selected page, and scroll
position before a theme rebuild.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (bool, int, int) or None` | Whether the pane is open, its page index, and its vertical scroll position; None without settings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> ExerciseView(
...     NoteNames(), rng=random.Random(1)
... ).settings_state()
(False, 0, 0)
```

## ExerciseView.restore_settings_state

<div class="api-signature" markdown="1">

```python
def restore_settings_state(state: tuple[bool, int, int]) -> None
```

{% endraw %}{% include api-source.html name="ExerciseView.restore_settings_state" line=1389 %}{% raw %}

</div>

Restore exercise settings navigation immediately after
rebuilding the view.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `state` | `tuple of (bool, int, int)` | Whether the pane was open, the selected page, and its vertical scroll position. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(
...     NoteNames(), rng=random.Random(1)
... )
>>> view.restore_settings_state((True, 0, 0))
>>> view.settings_state()
(True, 0, 0)
```

## ExerciseView.scheduling_changed

<div class="api-signature" markdown="1">

```python
def scheduling_changed() -> None
```

{% endraw %}{% include api-source.html name="ExerciseView.scheduling_changed" line=1561 %}{% raw %}

</div>

Refresh the visible exercise or invalidate its queue until it is
reopened.

**Examples**

```text
Lowering the daily allowance on the home page also applies to a
previously opened exercise.
```

## ExerciseView.next_question

<div class="api-signature" markdown="1">

```python
def next_question() -> None
```

{% endraw %}{% include api-source.html name="ExerciseView.next_question" line=1626 %}{% raw %}

</div>

Show the next question: its staff, keyboard or text, and a fresh
set of answer buttons.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(
...     NoteNames(), rng=random.Random(1)
... )
>>> view.next_question()
>>> # noinspection PyUnresolvedReferences
>>> (
...     view.answered,
...     len(view.buttons)
...     == len(view.question.choices),
... )
(False, True)
```

## ExerciseView.eventFilter

<div class="api-signature" markdown="1">

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

{% endraw %}{% include api-source.html name="ExerciseView.eventFilter" line=3352 %}{% raw %}

</div>

Handle staff clicks in notation questions and forward wheel
turns to the fork or clef staff.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `watched` | `QObject` | The staff or the Answer button. |
| `event` | `QEvent` | The incoming pointer or widget event. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True when the exercise handles the event. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QPoint, QPointF
>>> from PySide6.QtGui import QWheelEvent
>>> from alto.exercises.library import (
...     KeySignatureConstruction,
... )
>>> view = ExerciseView(
...     KeySignatureConstruction(),
...     rng=random.Random(1),
... )
>>> view.show()
>>> here = QPointF(5, 5)
>>> turn = QWheelEvent(
...     here,
...     here,
...     QPoint(0, 0),
...     QPoint(0, 120),
...     Qt.MouseButton.NoButton,
...     Qt.KeyboardModifier.NoModifier,
...     Qt.ScrollPhase.NoScrollPhase,
...     False,
... )
>>> view.eventFilter(view.answer_button, turn)
True
>>> view.fork.value
1
```

## ExerciseView.submit

<div class="api-signature" markdown="1">

```python
def submit(
    choice: str,
    *,
    button: QPushButton | None,
) -> None
```

{% endraw %}{% include api-source.html name="ExerciseView.submit" line=3903 %}{% raw %}

</div>

Check an answer chosen with a button or by clicking the
notation.

A correct answer uses the selected Next Question setting. An
incorrect button flashes red.
In SM-2 and FSRS the card returns at its scheduled retry time.
ASRS and ARTS allow another answer on the same showing.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `choice` | `str` | The text of the button that was pressed. |
| `button` | `QPushButton or None` | The pressed button, or None for a staff click. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> sounds.enabled = False
>>> view = ExerciseView(
...     NoteNames(), rng=random.Random(1)
... )
>>> question = view.question
>>> # noinspection PyUnresolvedReferences
>>> wrong = next(
...     b
...     for b in view.buttons
...     if b.text() != question.answer
... )
>>> view.submit(wrong.text(), button=wrong)
>>> view.missed, wrong.isEnabled()
(True, False)
>>> # noinspection PyUnresolvedReferences
>>> right = next(
...     b
...     for b in view.buttons
...     if b.text() == question.answer
... )
>>> # noinspection PyUnresolvedReferences
>>> view.submit(question.answer, button=right)
>>> view.answered
True
>>> view._advance.stop()
>>> sounds.enabled = True
```
{% endraw %}
