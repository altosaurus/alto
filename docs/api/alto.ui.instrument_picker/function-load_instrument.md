---
title: load_instrument
parent: alto.ui.instrument_picker
api_module: alto.ui.instrument_picker
package: alto.ui
permalink: /api/alto.ui.instrument_picker/function-load_instrument/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_instrument() -> None
```

{% endraw %}{% include api-source.html name="load_instrument" line=97 %}{% raw %}

</div>

Apply the saved instrument.

The piano is used if nothing is saved or the saved key is not an
instrument.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "audio/instrument", "flute"
... )
>>> load_instrument()
>>> sounds.instrument
'flute'
>>> store().setValue(
...     "audio/instrument", "not an instrument"
... )
>>> load_instrument()
>>> sounds.instrument
'piano'
```
{% endraw %}
