---
title: ruler_reach
parent: alto.ui.fingerboard
api_module: alto.ui.fingerboard
package: alto.ui
permalink: /api/alto.ui.fingerboard/function-ruler_reach/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ruler_reach(model: PackInstrument) -> int
```

{% endraw %}{% include api-source.html name="ruler_reach" line=55 %}{% raw %}

</div>

Find how many half steps the ruler covers: an octave, or further if
the pack names a position beyond it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `model` | `PackInstrument` | The instrument whose positions, if any, the ruler labels. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The highest half step with a tick. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> bare = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (10, 10),
...     (),
...     None,
... )
>>> ruler_reach(bare)
12
>>> ruler_reach(
...     PackInstrument(
...         "pack.x.y",
...         Path("a.png"),
...         (10, 10),
...         (),
...         None,
...         positions=((14, "9th"),),
...     )
... )
14
```
{% endraw %}
