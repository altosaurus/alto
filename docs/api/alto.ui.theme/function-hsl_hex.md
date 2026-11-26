---
title: hsl_hex
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-hsl_hex/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def hsl_hex(
    hue: float,
    *,
    saturation: float,
    lightness: float,
) -> str
```

{% endraw %}{% include api-source.html name="hsl_hex" line=201 %}{% raw %}

</div>

Turn a color given as hue, saturation and lightness into "#rrggbb".

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `hue` | `float` | The hue, in degrees. |
| `saturation` | `float` | The saturation, from 0 to 100. Keyword-only. |
| `lightness` | `float` | The lightness, from 0 to 100. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The color in hexadecimal. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     hsl_hex(
...         0, saturation=100, lightness=50
...     ),
...     hsl_hex(
...         210, saturation=0, lightness=100
...     ),
... )
('#ff0000', '#ffffff')
```
{% endraw %}
