---
title: Motion
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/class-motion/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Motion(
    length: float = 320.0,
    per_card: float = 0.0,
    start: float = 0.0,
    after: bool = False,
    order: str = 'index',
    ease: str = 'out',
    dx: float = 0.0,
    dy: float = 0.0,
    scale: float = 1.0,
    sx: float = 1.0,
    sy: float = 1.0,
    angle: float = 0.0,
    blur: float = 0.0,
    fade: bool = True,
    reveal: str = '',
)
```

{% endraw %}{% include api-source.html name="Motion" line=642 %}{% raw %}

</div>

How one set of cards moves in a transition built from parts: when
each card starts, how long it takes, and what it does.

Every card goes between its resting look and a look given here, so
the same description serves for cards arriving (from that
look to rest) and leaving (from rest to that look).

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `length` | `float` | How long each card takes, in milliseconds. |
| `per_card` | `float` | How much later each card starts than the one before it. |
| `start` | `float` | When the first card starts. |
| `after` | `bool` | True to wait until the cards that are leaving have all finished before starting; only for cards that are arriving. |
| `order` | `str` | The order the cards start in: one of `ORDERS`. |
| `ease` | `str` | How the motion is timed: one of `EASES`. |
| `dx` | `float` | How far to the right the card is at the far look, in pixels; it follows the direction of the switch. |
| `dy` | `float` | How far down the card is at the far look. |
| `scale` | `float` | How big the card is at the far look, as a fraction of its size. |
| `sx` | `float` | As well as `scale`, how wide, for a card that turns on its edge. |
| `sy` | `float` | As well as `scale`, how tall. |
| `angle` | `float` | How far the card is turned at the far look, in degrees; it follows the direction of the switch. |
| `blur` | `float` | How blurred it is at the far look, from 0 to 1. |
| `fade` | `bool` | True to fade between solid and clear; False to keep it solid, and hide it only once it is out of the way. |
| `reveal` | `str` | "" for none, or "side" or "center" to uncover it from one side or from the middle. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Motion().order, Motion().ease
('index', 'out')
```
{% endraw %}
