---
title: hsl_of
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-hsl_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def hsl_of(text: str) -> Hsl
```

{% endraw %}{% include api-source.html name="hsl_of" line=300 %}{% raw %}

</div>

Read a color written as "#rrggbb".

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The color. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of float` | Its hue (0 to 360), saturation and lightness. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> hsl_of("#ff0000")
(0.0, 1.0, 0.5)
```
{% endraw %}
