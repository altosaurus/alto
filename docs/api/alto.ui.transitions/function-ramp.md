---
title: ramp
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-ramp/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ramp(
    time: float,
    *,
    start: float,
    length: float,
) -> float
```

{% endraw %}{% include api-source.html name="ramp" line=170 %}{% raw %}

</div>

Say how far along a part of a transition is, from 0 before it starts
to 1 once it has finished.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `time` | `float` | The time since the transition began, in milliseconds. |
| `start` | `float` | When the part begins. Keyword-only. |
| `length` | `float` | How long it lasts. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The progress, from 0 to 1. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     ramp(50, start=100, length=200),
...     ramp(200, start=100, length=200),
...     ramp(900, start=100, length=200),
... )
(0.0, 0.5, 1.0)
```
{% endraw %}
