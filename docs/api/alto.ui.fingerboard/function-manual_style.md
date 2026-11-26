---
title: manual_style
parent: alto.ui.fingerboard
api_module: alto.ui.fingerboard
package: alto.ui
permalink: /api/alto.ui.fingerboard/function-manual_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def manual_style(model: PackInstrument) -> tuple[KeyboardStyle | None, float]
```

{% endraw %}{% include api-source.html name="manual_style" line=219 %}{% raw %}

</div>

Build the look of an instrument's drawn keyboards from its plugin's
``keyboard_style``.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `model` | `PackInstrument` | The instrument whose keyboards are drawn. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of KeyboardStyle or None and float` | The style, or None to use the learner's own keyboard style, and how long a natural key is, in key widths. |

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
>>> manual_style(bare)
(None, 4.5)
>>> from alto.instrument_packs import (
...     PackKeyboardStyle,
... )
>>> look = PackKeyboardStyle(
...     (("cap", "#eee3c8"),),
...     (("length", 5.0),),
... )
>>> styled = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (10, 10),
...     (),
...     None,
...     keyboard_style=look,
... )
>>> look_style, look_length = manual_style(
...     styled
... )
>>> # noinspection PyUnresolvedReferences
>>> look_style.cap, look_length
('#eee3c8', 5.0)
```
{% endraw %}
