---
title: draw_signature_sign
parent: alto.ui.staff
api_module: alto.ui.staff
package: alto.ui
permalink: /api/alto.ui.staff/function-draw_signature_sign/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def draw_signature_sign(
    p: QPainter,
    *,
    sign: int,
    x: float,
    y: float,
    gap: float,
    color: QColor,
    step: float = KEY_STEP,
    size: float = 2.0,
    font: str | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="draw_signature_sign" line=313 %}{% raw %}

</div>

Draw one sharp or flat at its written position in a key signature.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `p` | `QPainter` | Active staff painter. |
| `sign` | `int` | Sharp (1) or flat (-1). |
| `x, y` | `float` | Left edge and staff pitch position in pixels. |
| `gap` | `float` | Distance between staff lines. |
| `color` | `QColor` | Ink for this sign. |
| `step, size` | `float` | Slot width in pixels and built-in glyph size in staff gaps. |
| `font` | `str or None` | SMuFL font, or None for the built-in notation. |

**Examples**

```text
Both the printed signature and signs placed by the learner use this
drawing.
```
{% endraw %}
