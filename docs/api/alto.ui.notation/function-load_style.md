---
title: load_style
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/function-load_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_style() -> None
```

{% endraw %}{% include api-source.html name="load_style" line=247 %}{% raw %}

</div>

Apply the saved choices: the style (Finale Maestro if none is saved
or it is unknown) and the baritone clef.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue("ui/notation", "bravura")
>>> load_style()
>>> current().key
'bravura'
>>> set_style(DEFAULT)  # back to the default
```
{% endraw %}
