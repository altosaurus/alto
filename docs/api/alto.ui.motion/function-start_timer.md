---
title: start_timer
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-start_timer/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def start_timer(
    timer: QTimer,
    *,
    delay: int,
) -> None
```

{% endraw %}{% include api-source.html name="start_timer" line=295 %}{% raw %}

</div>

Start a single-shot timer whose timeout is part of the interface's
motion, such as moving on to the next question.

The timer can be stopped as usual, and then it does not fire.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `timer` | `QTimer` | The timer, which fires once. |
| `delay` | `int` | Its interval, in milliseconds. With instant motion it waits for `settle` instead. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_instant(True)
>>> timer = QTimer()
>>> timer.setSingleShot(True)
>>> fired = []
>>> _ = timer.timeout.connect(
...     lambda: fired.append(1)
... )
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
{% endraw %}
