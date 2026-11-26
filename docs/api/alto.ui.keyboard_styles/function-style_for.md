---
title: style_for
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-style_for/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def style_for(key: str) -> KeyboardStyle
```

{% endraw %}{% include api-source.html name="style_for" line=392 %}{% raw %}

</div>

Return the style with a given key.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | A key of `BY_KEY`, or "custom". |

**Returns**

| Type | Description |
| --- | --- |
| `KeyboardStyle` | That style; the default (Classic) if the key is not known. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> style_for("modern").label
'Modern piano'
>>> style_for("nonsense").label
'Classic'
```
{% endraw %}
