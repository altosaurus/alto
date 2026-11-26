---
title: load_scale_construction
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_scale_construction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_scale_construction() -> None
```

{% endraw %}{% include api-source.html name="load_scale_construction" line=972 %}{% raw %}

</div>

Load the saved scale construction settings into the shared settings
object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "scaleConstruction/keys", "1,-1"
... )
>>> store().setValue(
...     "scaleConstruction/steps", "true"
... )
>>> store().setValue(
...     "scaleConstruction/octave", "true"
... )
>>> load_scale_construction()
>>> (
...     settings.scale_construction.active_keys(),
...     settings.scale_construction.steps,
...     settings.scale_construction.octave,
... )
([-1, 1], True, True)
>>> (
...     settings.scale_construction.keys,
...     settings.scale_construction.steps,
... ) = set(range(-7, 8)), False
>>> settings.scale_construction.octave = False
>>> store().remove("scaleConstruction")
```
{% endraw %}
