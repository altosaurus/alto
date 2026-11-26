---
title: degree_tooltip
parent: alto.ui.degree_text
api_module: alto.ui.degree_text
package: alto.ui
permalink: /api/alto.ui.degree_text/function-degree_tooltip/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def degree_tooltip(text: str) -> str
```

{% endraw %}{% include api-source.html name="degree_tooltip" line=123 %}{% raw %}

</div>

Render caret examples as an inline image for Qt's rich-text tooltip.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The tooltip text. Text without combining carets is returned unchanged. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Plain text or HTML containing the explicitly centered carets. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> degree_tooltip("Letters")
'Letters'
>>> "data:image/png;base64," in degree_tooltip(
...     "Caret (1̂ 2̂ 3̂)"
... )
True
```
{% endraw %}
