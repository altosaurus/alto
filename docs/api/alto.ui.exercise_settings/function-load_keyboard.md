---
title: load_keyboard
parent: alto.ui.exercise_settings
api_module: alto.ui.exercise_settings
package: alto.ui
permalink: /api/alto.ui.exercise_settings/function-load_keyboard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_keyboard() -> None
```

{% endraw %}{% include api-source.html name="load_keyboard" line=163 %}{% raw %}

</div>

Load the saved keyboard exercise settings into the shared settings
object.

A saved range that is not a valid span of keys, or a key list with
nothing usable in it, is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg_ = settings.keyboard
>>> cfg_.require_octave = True
>>> save_keyboard()
>>> cfg_.require_octave = False
>>> load_keyboard()
>>> cfg_.require_octave
True
>>> cfg_.require_octave = False
>>> save_keyboard()
```
{% endraw %}
