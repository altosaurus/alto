---
title: load_pack_options
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_pack_options/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_pack_options() -> None
```

{% endraw %}{% include api-source.html name="load_pack_options" line=1207 %}{% raw %}

</div>

Restore the options learners chose for each plugin exercise that
offers settings.

Anything in the saved data that is not valid is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_pack_options()
```
{% endraw %}
