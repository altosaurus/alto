---
title: load_key_signatures
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_key_signatures/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_key_signatures() -> None
```

{% endraw %}{% include api-source.html name="load_key_signatures" line=887 %}{% raw %}

</div>

Load the saved key signature identification settings into the shared
settings object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "keySignatures/clefs", "alto"
... )
>>> load_key_signatures()
>>> settings.key_signatures.clefs
{'alto'}
>>> settings.key_signatures.clefs = {
...     "treble",
...     "bass",
... }
>>> store().setValue(
...     "keySignatures/clefs", "treble,bass"
... )
```
{% endraw %}
