---
title: baritone_clef
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/function-baritone_clef/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def baritone_clef() -> str
```

{% endraw %}{% include api-source.html name="baritone_clef" line=153 %}{% raw %}

</div>

Return which way the baritone clef is written.

**Returns**

| Type | Description |
| --- | --- |
| `str` | "f" for an F clef on the middle line, or "c" for a C clef on the top line. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> baritone_clef() in BARITONE_CLEFS
True
```
{% endraw %}
