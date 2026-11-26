---
title: load_notation_terms
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_notation_terms/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_notation_terms() -> None
```

{% endraw %}{% include api-source.html name="load_notation_terms" line=1030 %}{% raw %}

</div>

Restore the question type and term selection, defaulting to Answer
Button and all terms.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_notation_terms()
>>> bool(settings.notation.terms)
True
```
{% endraw %}
