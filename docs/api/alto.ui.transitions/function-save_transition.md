---
title: save_transition
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-save_transition/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_transition(key: str) -> None
```

{% endraw %}{% include api-source.html name="save_transition" line=1541 %}{% raw %}

</div>

Remember which transition to use.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_transition("flip")
>>> saved_transition()
'flip'
>>> store().remove("ui/homeTransition")
```
{% endraw %}
