---
title: identifier
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-identifier/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def identifier(value: object) -> str
```

{% endraw %}{% include api-source.html name="identifier" line=481 %}{% raw %}

</div>

Validate one component of a pack-qualified id.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The validated id. |

**Raises**

- *ValueError*: If the id includes an unsupported character.
{% endraw %}
