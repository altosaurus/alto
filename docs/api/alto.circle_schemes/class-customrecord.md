---
title: CustomRecord
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/class-customrecord/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class CustomRecord(TypedDict)
```

{% endraw %}{% include api-source.html name="CustomRecord" line=103 %}{% raw %}

</div>

A scheme of the user's own, as it is saved.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `str` | Its key, such as "custom-1". |
| `name` | `str` | What the user called it. |
| `mode` | `str` | How its colors are made: a key of `MODES`. |
| `colors` | `list of str` | The colors the mode takes, as "#rrggbb": what a cell looks like when it is lit. |
| `light` | `bool` | Whether the wedges are light, with dark names. |
{% endraw %}
