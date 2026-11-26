---
title: span
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-span/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def span(
    motion: Motion,
    *,
    count: int,
) -> float
```

{% endraw %}{% include api-source.html name="span" line=833 %}{% raw %}

</div>

Say how long a motion takes for a number of cards, from when it
starts to when the last card has finished.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `motion` | `Motion` | The motion. |
| `count` | `int` | How many cards. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The time in milliseconds. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> span(
...     Motion(
...         length=300.0,
...         per_card=50.0,
...         start=10.0,
...     ),
...     count=4,
... )
460.0
```
{% endraw %}
