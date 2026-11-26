---
title: read_marker_size
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_marker_size/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_marker_size(value: object) -> float
```

{% endraw %}{% include api-source.html name="read_marker_size" line=948 %}{% raw %}

</div>

Validate a picture's marker size.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The manifest entry: a diameter in picture pixels, or 0 for the default size. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | The diameter. |

**Raises**

- *ValueError*: If the entry is not 0 or a number from 6 to 200.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_marker_size(0), read_marker_size(24)
(0.0, 24.0)
```
{% endraw %}
