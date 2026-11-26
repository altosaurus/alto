---
title: css
parent: alto.ui.zoom
api_module: alto.ui.zoom
package: alto.ui
permalink: /api/alto.ui.zoom/function-css/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def css(text: str) -> str
```

{% endraw %}{% include api-source.html name="css" line=160 %}{% raw %}

</div>

Scale every pixel and point length in a stylesheet by the zoom.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The stylesheet. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The same stylesheet with each length such as ``12px`` or ``14pt`` multiplied. A length of zero stays zero. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> css(
...     "QLabel { padding: 8px 12px; font-size: 14pt; margin: 0px;"
...     " }"
... )
'QLabel { padding: 8px 12px; font-size: 14pt; margin: 0px; }'
```
{% endraw %}
