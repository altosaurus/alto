---
title: load_key_construction
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_key_construction/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_key_construction() -> None
```

{% endraw %}{% include api-source.html name="load_key_construction" line=914 %}{% raw %}

</div>

Load the saved key signature construction settings into the shared
settings object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "keyConstruction/keys", "-3,4"
... )
>>> load_key_construction()
>>> settings.key_construction.active_keys()
[-3, 4]
>>> settings.key_construction.keys = set(
...     range(-7, 8)
... )
>>> store().remove("keyConstruction")
```
{% endraw %}
