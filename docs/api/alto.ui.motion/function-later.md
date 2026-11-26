---
title: later
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-later/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def later(
    delay: int,
    *,
    owner: QObject,
    step: Callable[[], object],
) -> None
```

{% endraw %}{% include api-source.html name="later" line=253 %}{% raw %}

</div>

Run a step after a delay, such as clearing wrong-answer feedback so
the learner can try again.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `delay` | `int` | How long to wait, in milliseconds. With instant motion the step waits for `settle` instead. |
| `owner` | `QObject` | The object the step belongs to. If it is deleted first, the step does not run. Keyword-only. |
| `step` | `callable` | What to run. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_instant(True)
>>> owner = QObject()
>>> done = []
>>> later(
...     450,
...     owner=owner,
...     step=lambda: done.append("retry"),
... )
>>> settle()
>>> done
['retry']
>>> set_instant(False)
```
{% endraw %}
