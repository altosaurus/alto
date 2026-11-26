---
title: save_keyboard
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-save_keyboard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_keyboard() -> None
```

{% endraw %}{% include api-source.html name="save_keyboard" line=216 %}{% raw %}

</div>

Save the keyboard exercise settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg_ = settings.keyboard
>>> save_keyboard()
>>> int(
...     store().value("keyboard/low")
... ) == cfg_.low
True
```
{% endraw %}
