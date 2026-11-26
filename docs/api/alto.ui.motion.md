---
title: alto.ui.motion
parent: api
package: alto.ui
api_components: [{"title": "busy", "url": "/api/alto.ui.motion/function-busy/"}, {"title": "instant", "url": "/api/alto.ui.motion/function-instant/"}, {"title": "later", "url": "/api/alto.ui.motion/function-later/"}, {"title": "play", "url": "/api/alto.ui.motion/function-play/"}, {"title": "set_instant", "url": "/api/alto.ui.motion/function-set_instant/"}, {"title": "set_shortcut", "url": "/api/alto.ui.motion/function-set_shortcut/"}, {"title": "settle", "url": "/api/alto.ui.motion/function-settle/"}, {"title": "start_timer", "url": "/api/alto.ui.motion/function-start_timer/"}]
permalink: /api/alto.ui.motion/
---
{% raw %}
Animations and feedback delays, run in one place so that tests decide
when they happen.

## Functions

- [`instant`](function-instant/) — Say whether motion waits for `settle`, as it does in tests.
- [`set_instant`](function-set_instant/) — Make motion wait for `settle`, for tests, or give it back its real time.
- [`later`](function-later/) — Run a step after a delay, such as clearing wrong-answer feedback so the learner can try again.
- [`start_timer`](function-start_timer/) — Start a single-shot timer whose timeout is part of the interface's motion, such as moving on to the next question.
- [`play`](function-play/) — Start an animation. With instant motion it holds still at its start until `settle` moves it to its end.
- [`busy`](function-busy/) — Say whether any motion is still to come: a delayed step, an active timer or a running animation.
- [`settle`](function-settle/) — Let every piece of motion happen: delayed steps run, timers fire and animations reach their end.
- [`set_shortcut`](function-set_shortcut/) — Give a button a key that presses it. In the app Qt handles the key; with instant motion it clicks the button at once.

<details markdown="1">
<summary>Module notes and examples</summary>

The interface moves: pages slide, feedback stays on screen for a moment
and the next question follows. Each of those goes
through this module: `play` starts an animation, `later` runs a step
after a delay and `start_timer` starts a timer that
does. In the app they take their real time. A button is given its key
with `set_shortcut`.

Tests switch to instant motion with `set_instant`. Then nothing moves on
by itself: animations hold still and delayed steps
and timers wait in a queue, however long the test takes, until it calls
`settle`. That runs everything waiting, in the order
it was asked for, at once. So a test can look at the state just after an
action (the feedback showing, a page about to
slide), and the motion happens only when the test says so, never during
some other wait. A button's key clicks it at once,
since its pressed look is all there is to see in the meantime.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_instant(True)
>>> owner = QObject()
>>> done = []
>>> later(
...     900,
...     owner=owner,
...     step=lambda: done.append("cleared"),
... )
>>> QCoreApplication.processEvents()  # nothing happens by itself
>>> done, busy()
([], True)
>>> settle()
>>> done, busy()
(['cleared'], False)
>>> set_instant(False)
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"instant": "function-instant/", "set_instant": "function-set_instant/", "later": "function-later/", "start_timer": "function-start_timer/", "play": "function-play/", "busy": "function-busy/", "settle": "function-settle/", "set_shortcut": "function-set_shortcut/"}</script>
{% include api-fragments.html %}
