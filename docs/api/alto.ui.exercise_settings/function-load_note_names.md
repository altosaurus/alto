---
title: load_note_names
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_note_names/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_note_names() -> None
```

{% endraw %}{% include api-source.html name="load_note_names" line=52 %}{% raw %}

</div>

Load the saved note identification settings into the shared settings
object.

Settings saved by an older version, which had a switch between the
grand staff and single clefs, are converted. Anything
in the saved data that is not valid is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg_ = settings.note_names
>>> cfg_.clefs = {"alto"}
>>> save_note_names()
>>> cfg_.clefs = {"treble"}
>>> load_note_names()
>>> cfg_.clefs
{'alto'}
>>> cfg_.clefs = {"treble", "bass"}
>>> save_note_names()
```
{% endraw %}
