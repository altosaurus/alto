---
title: NotationSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-notationsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NotationSettings(
    terms: set[str] = field(default_factory=lambda: set(NOTATION_TERMS)),
    question_type: str = 'button',
)
```

{% endraw %}{% include api-source.html name="NotationSettings" line=1809 %}{% raw %}

</div>

Terms eligible to be highlighted in Notation Identification.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> "Notehead" in NotationSettings().terms
True
```
{% endraw %}
