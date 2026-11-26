---
title: Sprite
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/class-sprite/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Sprite(
    pixmap: QPixmap,
    rect: QRectF,
    opacity: float = 1.0,
    dx: float = 0.0,
    dy: float = 0.0,
    sx: float = 1.0,
    sy: float = 1.0,
    blur: float = 0.0,
    angle: float = 0.0,
    reveal: float = 1.0,
    reveal_from: int = 1,
)
```

{% endraw %}{% include api-source.html name="Sprite" line=61 %}{% raw %}

</div>

A photograph of one card, and how it is drawn at this moment.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `pixmap` | `QPixmap` | The photograph. |
| `rect` | `QRectF` | Where the card is, in the canvas. |
| `opacity` | `float` | 0 for invisible to 1 for solid. |
| `dx` | `float` | How far it is moved right, in pixels. |
| `dy` | `float` | How far it is moved down, in pixels. |
| `sx` | `float` | How much it is stretched across, about its middle; 1 is as it was. |
| `sy` | `float` | How much it is stretched down, about its middle. |
| `blur` | `float` | 0 for sharp to 1 for fully blurred. |
| `angle` | `float` | How far it is turned about its middle, in degrees, clockwise. |
| `reveal` | `float` | How much of it shows, from 0 to 1. |
| `reveal_from` | `int` | 1 to uncover it from the left, -1 from the right, 0 from the middle outwards. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sprite = Sprite(
...     pixmap=QPixmap(),
...     rect=QRectF(0, 0, 10, 10),
... )
>>> sprite.opacity, sprite.reveal
(1.0, 1.0)
```
{% endraw %}
