---
title: settle
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-settle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def settle(
    *,
    rounds: int = 1000,
) -> None
```

{% endraw %}{% include api-source.html name="settle" line=421 %}{% raw %}

</div>

Let every piece of motion happen: delayed steps run, timers fire and
animations reach their end.

With instant motion they happen at once, in the order they were
asked for, and motion they start (feedback that leads to
the next question, which slides in) happens too. In the app's real
time this waits for them instead.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rounds` | `int, default 1000` | The most pieces of motion to go through or, in real time, about how many milliseconds to wait. Keyword-only. |

**Raises**

- *RuntimeError*: If motion is still going after that many, such as a step that keeps asking for itself again.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settle()
>>> busy()
False

A step that always asks for itself again never settles:

>>> set_instant(True)
>>> owner = QObject()
>>> def again():
...     later(10, owner=owner, step=again)
>>> later(10, owner=owner, step=again)
>>> settle(rounds=3)
Traceback (most recent call last):
    ...
RuntimeError: Motion is still going after 3 rounds.
>>> set_instant(False)
```
{% endraw %}
