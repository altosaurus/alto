---
title: load
parent: alto.ui.zoom
api_module: alto.ui.zoom
package: alto.ui
permalink: /api/alto.ui.zoom/function-load/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load() -> None
```

{% endraw %}{% include api-source.html name="load" line=340 %}{% raw %}

</div>

Take the saved zoom into force, without announcing it, ignoring
anything that is not a step.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(SETTING, 150)
>>> load()
>>> percent()
150
>>> store().setValue(SETTING, "wide")
>>> load()
>>> percent()
100
```
{% endraw %}
