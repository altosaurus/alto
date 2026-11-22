---
title: alto.ui.motion
parent: api
package: alto.ui
permalink: /api/alto.ui.motion/
---
{% raw %}
Animations and feedback delays, run in one place so that tests decide when they happen.

The interface moves: pages slide, feedback stays on screen for a moment and the next question follows. Each of those goes
through this module: `play` starts an animation, `later` runs a step after a delay and `start_timer` starts a timer that
does. In the app they take their real time.

Tests switch to instant motion with `set_instant`. Then nothing moves on by itself: animations hold still and delayed steps
and timers wait in a queue, however long the test takes, until it calls `settle`. That runs everything waiting, in the order
it was asked for, at once. So a test can look at the state just after an action (the feedback showing, a page about to
slide), and the motion happens only when the test says so, never during some other wait.

**Examples**

```pycon
>>> set_instant(True)
>>> owner = QObject()
>>> done = []
>>> later(900, owner=owner, step=lambda: done.append("cleared"))
>>> QCoreApplication.processEvents()  # nothing happens by itself
>>> done, busy()
([], True)
>>> settle()
>>> done, busy()
(['cleared'], False)
>>> set_instant(False)
```

## instant

```python
def instant() -> bool
```

Say whether motion waits for `settle`, as it does in tests.

**Returns**

- *bool*: True if animations and delays hold until a test settles them.

**Examples**

```pycon
>>> instant()
False
```

## set_instant

```python
def set_instant(on: bool) -> None
```

Make motion wait for `settle`, for tests, or give it back its real time.

**Parameters**

- `on` (*bool*): True for instant motion.

**Examples**

```pycon
>>> set_instant(True)
>>> instant()
True
>>> set_instant(False)
```

## later

```python
def later(
    delay: int,
    *,
    owner: QObject,
    step: Callable[[], object],
) -> None
```

Run a step after a delay, such as clearing wrong-answer feedback so the learner can try again.

**Parameters**

- `delay` (*int*): How long to wait, in milliseconds. With instant motion the step waits for `settle` instead.
- `owner` (*QObject*): The object the step belongs to. If it is deleted first, the step does not run. Keyword-only.
- `step` (*callable*): What to run. Keyword-only.

**Examples**

```pycon
>>> set_instant(True)
>>> owner = QObject()
>>> done = []
>>> later(450, owner=owner, step=lambda: done.append("retry"))
>>> settle()
>>> done
['retry']
>>> set_instant(False)
```

## start_timer

```python
def start_timer(
    timer: QTimer,
    *,
    delay: int,
) -> None
```

Start a single-shot timer whose timeout is part of the interface's motion, such as moving on to the next question.

The timer can be stopped as usual, and then it does not fire.

**Parameters**

- `timer` (*QTimer*): The timer, which fires once.
- `delay` (*int*): Its interval, in milliseconds. With instant motion it waits for `settle` instead. Keyword-only.

**Examples**

```pycon
>>> set_instant(True)
>>> timer = QTimer()
>>> timer.setSingleShot(True)
>>> fired = []
>>> _ = timer.timeout.connect(lambda: fired.append(1))
>>> start_timer(timer, delay=1200)
>>> timer.isActive(), busy()
(True, True)
>>> settle()
>>> fired, timer.isActive()
([1], False)
>>> start_timer(timer, delay=1200)
>>> timer.stop()  # a stopped timer does not fire
>>> settle()
>>> fired
[1]
>>> set_instant(False)
```

## play

```python
def play(animation: QAbstractAnimation) -> None
```

Start an animation. With instant motion it holds still at its start until `settle` moves it to its end.

**Parameters**

- `animation` (*QAbstractAnimation*): The animation, or a group of them. It finishes as usual, with its `finished` signal.

**Examples**

```pycon
>>> from PySide6.QtCore import QVariantAnimation
>>> set_instant(True)
>>> animation = QVariantAnimation()
>>> animation.setDuration(220)
>>> animation.setStartValue(0.0)
>>> animation.setEndValue(1.0)
>>> play(animation)
>>> animation.state() == QAbstractAnimation.State.Stopped, busy()
(False, True)
>>> settle()
>>> animation.currentValue(), animation.state() == QAbstractAnimation.State.Stopped
(1.0, True)
>>> set_instant(False)
```

## busy

```python
def busy() -> bool
```

Say whether any motion is still to come: a delayed step, an active timer or a running animation.

**Returns**

- *bool*: True if `settle` would run something.

**Examples**

```pycon
>>> busy()
False
```

## settle

```python
def settle(
    *,
    rounds: int = 1000,
) -> None
```

Let every piece of motion happen: delayed steps run, timers fire and animations reach their end.

With instant motion they happen at once, in the order they were asked for, and motion they start (feedback that leads to
the next question, which slides in) happens too. In the app's real time this waits for them instead.

**Parameters**

- `rounds` (*int, default 1000*): The most pieces of motion, or passes of the event loop, to go through. Keyword-only.

**Raises**

- *RuntimeError*: If motion is still going after that many, such as a step that keeps asking for itself again.

**Examples**

```pycon
>>> settle()
>>> busy()
False
```
{% endraw %}
