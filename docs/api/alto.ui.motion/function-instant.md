---
title: instant
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-instant/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def instant() -> bool
```

{% endraw %}{% include api-source.html name="instant" line=192 %}{% raw %}

</div>

Say whether motion waits for `settle`, as it does in tests.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if animations and delays hold until a test settles them. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> instant()
False
```
{% endraw %}
