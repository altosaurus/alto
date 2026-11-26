---
title: passages_by_term
parent: alto.notation_excerpts
api_module: alto.notation_excerpts
package: alto
permalink: /api/alto.notation_excerpts/function-passages_by_term/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
@cache
def passages_by_term() -> dict[str, dict[str, list[int]]]
```

{% endraw %}{% include api-source.html name="passages_by_term" line=55 %}{% raw %}

</div>

Group score locations by term and passage so dense passages do not
dominate the selection.

**Returns**

| Type | Description |
| --- | --- |
| `dict` | Matching marker indices for each term in each passage. |
{% endraw %}
