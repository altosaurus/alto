---
title: load_arpeggio
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_arpeggio/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_arpeggio() -> None
```

{% endraw %}{% include api-source.html name="load_arpeggio" line=470 %}{% raw %}

</div>

Load the saved arpeggio settings into the shared settings object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue("arpeggio/types", "major")
>>> load_arpeggio()
>>> settings.arpeggio.types
{'major'}
>>> settings.arpeggio.types = {
...     "major",
...     "minor",
...     "dominant 7th",
...     "diminished 7th",
... }
>>> store().setValue(
...     "arpeggio/types",
...     ",".join(
...         settings.arpeggio.active_types()
...     ),
... )
```
{% endraw %}
