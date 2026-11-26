---
title: set_instant
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-set_instant/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_instant(on: bool) -> None
```

{% endraw %}{% include api-source.html name="set_instant" line=209 %}{% raw %}

</div>

Make motion wait for `settle`, for tests, or give it back its real
time.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `on` | `bool` | True for instant motion. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_instant(True)
>>> instant()
True
>>> set_instant(False)
```
{% endraw %}
