---
title: current
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/function-current/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def current() -> NotationStyle
```

{% endraw %}{% include api-source.html name="current" line=229 %}{% raw %}

</div>

Return the notation style in use.

**Returns**

| Type | Description |
| --- | --- |
| `NotationStyle` | The style chosen in the settings (Finale Maestro until another is chosen). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> current().key in BY_KEY
True
```
{% endraw %}
