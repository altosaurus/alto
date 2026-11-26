---
title: play
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-play/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def play(animation: QAbstractAnimation) -> None
```

{% endraw %}{% include api-source.html name="play" line=357 %}{% raw %}

</div>

Start an animation. With instant motion it holds still at its start
until `settle` moves it to its end.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `animation` | `QAbstractAnimation` | The animation, or a group of them. It finishes as usual, with its `finished` signal. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtCore import QVariantAnimation
>>> set_instant(True)
>>> animation = QVariantAnimation()
>>> animation.setDuration(220)
>>> animation.setStartValue(0.0)
>>> animation.setEndValue(1.0)
>>> play(animation)
>>> (
...     animation.state()
...     == QAbstractAnimation.State.Stopped,
...     busy(),
... )
(False, True)
>>> settle()
>>> (
...     animation.currentValue(),
...     animation.state()
...     == QAbstractAnimation.State.Stopped,
... )
(1.0, True)
>>> set_instant(False)
```
{% endraw %}
