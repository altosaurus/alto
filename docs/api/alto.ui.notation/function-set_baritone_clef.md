---
title: set_baritone_clef
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/function-set_baritone_clef/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_baritone_clef(kind: str) -> None
```

{% endraw %}{% include api-source.html name="set_baritone_clef" line=202 %}{% raw %}

</div>

Choose and save how the baritone clef is written, and redraw every
staff already on screen.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `kind` | `str` | "f" or "c"; anything else gives the default (F). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_baritone_clef("c")
>>> baritone_clef()
'c'
>>> set_baritone_clef(
...     "sideways"
... )  # not a choice: the default
>>> baritone_clef()
'f'
```
{% endraw %}
