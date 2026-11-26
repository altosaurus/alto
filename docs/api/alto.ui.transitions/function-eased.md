---
title: eased
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-eased/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def eased(
    progress: float,
    *,
    how: str,
) -> float
```

{% endraw %}{% include api-source.html name="eased" line=712 %}{% raw %}

</div>

Time a progress from 0 to 1 in one of the ways a motion can be
eased.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `progress` | `float` | How far along, from 0 to 1. |
| `how` | `str` | One of `EASES`: "out" slows to a stop, "in" speeds up, "back" overshoots a little and settles, "linear" does neither. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The timed progress, which "back" takes a little past 1 on the way. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     eased(0.5, how="linear"),
...     eased(1.0, how="back"),
...     eased(0.5, how="in"),
... )
(0.5, 1.0, 0.25)
>>> eased(0.8, how="back") > 1.0
True
```
{% endraw %}
