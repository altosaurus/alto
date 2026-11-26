---
title: hex_of
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-hex_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def hex_of(rgb: tuple[float, float, float]) -> str
```

{% endraw %}{% include api-source.html name="hex_of" line=276 %}{% raw %}

</div>

Write a color as "#rrggbb".

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rgb` | `tuple of float` | Red, green and blue, each from 0 to 1. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The color as hexadecimal. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> hex_of((1.0, 0.5, 0.0))
'#ff8000'
```
{% endraw %}
