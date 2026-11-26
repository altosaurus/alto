---
title: ruler_base
parent: alto.ui.fingerboard
api_module: alto.ui.fingerboard
package: alto.ui
permalink: /api/alto.ui.fingerboard/function-ruler_base/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ruler_base(
    model: PackInstrument,
    *,
    step: int,
) -> tuple[QPointF, QPointF, float]
```

{% endraw %}{% include api-source.html name="ruler_base" line=97 %}{% raw %}

</div>

Locate where a ruler tick for one half step starts, beside the
fingerboard rather than on it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `model` | `PackInstrument` | The instrument whose string endpoints give the geometry. |
| `step` | `int` | Half steps above the open string. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of QPointF, QPointF and float` | The tick's starting point in image pixels, the unit vector pointing away from the strings, and the local distance between neighboring strings at that step. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> from alto.instrument_packs import PackString
>>> strings = (
...     PackString("C3", (0, 10), (100, 10)),
...     PackString("G3", (0, 0), (100, 0)),
... )
>>> viola = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (100, 10),
...     strings,
...     None,
... )
>>> start, away, apart = ruler_base(
...     viola, step=0
... )
>>> (start.x(), start.y(), away.y(), apart)
(0.0, -18.0, -1.0, 10.0)
```
{% endraw %}
