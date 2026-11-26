---
title: format_key_signature
parent: alto.theory.scales
api_module: alto.theory.scales
package: alto.theory
permalink: /api/alto.theory.scales/function-format_key_signature/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def format_key_signature(count: int) -> str
```

{% endraw %}{% include api-source.html name="format_key_signature" line=315 %}{% raw %}

</div>

Describe a key signature in words.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `count` | `int` | Sharps (positive) or flats (negative). |

**Returns**

| Type | Description |
| --- | --- |
| `str` | For example '1 sharp', '3 flats' or 'no sharps or flats'. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> format_key_signature(0)
'no sharps or flats'
>>> format_key_signature(1)
'1 sharp'
>>> format_key_signature(-3)
'3 flats'
```
{% endraw %}
