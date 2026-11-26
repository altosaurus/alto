---
title: load_construction
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_construction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_construction() -> None
```

{% endraw %}{% include api-source.html name="load_construction" line=353 %}{% raw %}

</div>

Load the saved note construction settings into the shared settings
object.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "construction/accidentals", "true"
... )
>>> load_construction()
>>> settings.construction.accidentals
False
```
{% endraw %}
