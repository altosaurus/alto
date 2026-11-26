---
title: load_clef_basics
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_clef_basics/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_clef_basics() -> None
```

{% endraw %}{% include api-source.html name="load_clef_basics" line=1057 %}{% raw %}

</div>

Load the saved clef basics settings into the shared settings object.

Anything in the saved data that is not a clef or a kind of question
is ignored, and a list with no clef in it leaves the
setting as it was.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "clefBasics/clefs", "alto,subbass,flute"
... )
>>> store().setValue(
...     "clefBasics/type", "identification"
... )
>>> load_clef_basics()
>>> (
...     settings.clef_basics.active_clefs(),
...     settings.clef_basics.question_type,
... )
(['alto', 'subbass'], 'identification')
>>> (
...     settings.clef_basics.clefs,
...     settings.clef_basics.question_type,
... ) = (
...     {"treble", "bass"},
...     "construction",
... )
>>> store().remove("clefBasics")
```
{% endraw %}
