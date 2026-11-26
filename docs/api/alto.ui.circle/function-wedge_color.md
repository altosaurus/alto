---
title: wedge_color
parent: alto.ui.circle
api_module: alto.ui.circle
package: alto.ui
permalink: /api/alto.ui.circle/function-wedge_color/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def wedge_color(
    index: int,
    *,
    inner: bool,
    lift: float = 0.0,
    scheme: Scheme | None = None,
) -> QColor
```

{% endraw %}{% include api-source.html name="wedge_color" line=230 %}{% raw %}

</div>

Return the color of a wedge in a color scheme: quiet when it is not
being talked about and bright when it is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `index` | `int` | Which wedge, clockwise from the top. |
| `inner` | `bool` | Whether it is in the inner ring. Keyword-only. |
| `lift` | `float, default 0.0` | How bright it is, from 0 (quiet) to 1 (lit). Keyword-only. |
| `scheme` | `Scheme or None, default None` | The color scheme; the one chosen in the circle of fifths settings if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QColor` | The color. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> spectrum = preset("spectrum")
>>> (
...     wedge_color(
...         0,
...         inner=False,
...         lift=1.0,
...         scheme=spectrum,
...     ).hue(),
...     wedge_color(
...         6, inner=False, scheme=spectrum
...     ).hue(),
... )
(0, 180)
>>> lit, quiet = (
...     wedge_color(
...         0,
...         inner=False,
...         lift=amount,
...         scheme=spectrum,
...     )
...     for amount in (1.0, 0.0)
... )
>>> lit.lightness() > quiet.lightness()
True
>>> # no wedge looks too bright for white names
>>> every = [
...     wedge_color(
...         i,
...         inner=False,
...         lift=1.0,
...         scheme=spectrum,
...     )
...     for i in range(12)
... ]
>>> all(
...     0.299 * c.redF()
...     + 0.587 * c.greenF()
...     + 0.114 * c.blueF()
...     <= 0.44
...     for c in every
... )
True
```
{% endraw %}
