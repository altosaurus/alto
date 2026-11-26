---
title: save_instrument
parent: alto.ui.instrument_picker
api_module: alto.ui.instrument_picker
package: alto.ui
permalink: /api/alto.ui.instrument_picker/function-save_instrument/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_instrument() -> None
```

{% endraw %}{% include api-source.html name="save_instrument" line=123 %}{% raw %}

</div>

Remember the instrument in use.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.instrument = "marimba"
>>> save_instrument()
>>> str(store().value("audio/instrument"))
'marimba'
>>> sounds.instrument = "piano"
>>> save_instrument()
```
{% endraw %}
