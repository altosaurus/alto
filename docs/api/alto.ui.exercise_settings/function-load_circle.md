---
title: load_circle
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_circle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_circle() -> None
```

{% endraw %}{% include api-source.html name="load_circle" line=1128 %}{% raw %}

</div>

Load the saved circle of fifths settings into the shared settings
object.

Anything in the saved data that is not valid is ignored, and a list
with nothing valid in it leaves the setting as it was. A
saved color scheme that no longer exists (it was deleted, or comes
from a newer Alto) leaves the default.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "circle/questions", "numeral,nonsense"
... )
>>> store().setValue(
...     "circle/scheme", "midnight"
... )
>>> load_circle()
>>> (
...     settings.circle.questions,
...     settings.circle.scheme,
... )
({'numeral'}, 'midnight')
>>> settings.circle.questions = set(
...     settings.CIRCLE_QUESTIONS
... )
>>> settings.circle.scheme = DEFAULT_SCHEME
>>> store().remove("circle")
```
{% endraw %}
