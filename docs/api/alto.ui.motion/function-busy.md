---
title: busy
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-busy/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def busy() -> bool
```

{% endraw %}{% include api-source.html name="busy" line=403 %}{% raw %}

</div>

Say whether any motion is still to come: a delayed step, an active
timer or a running animation.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if `settle` would run something. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> busy()
False
```
{% endraw %}
