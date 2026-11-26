---
title: saved_transition
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-saved_transition/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def saved_transition() -> str
```

{% endraw %}{% include api-source.html name="saved_transition" line=1516 %}{% raw %}

</div>

Return the key of the transition that is chosen in the settings.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The key; the default if none is saved or the saved one no longer exists. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/homeTransition")
>>> saved_transition()
'cascade'
```
{% endraw %}
