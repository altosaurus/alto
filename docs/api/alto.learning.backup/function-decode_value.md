---
title: decode_value
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/function-decode_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def decode_value(value: object) -> object
```

{% endraw %}{% include api-source.html name="decode_value" line=209 %}{% raw %}

</div>

Undo `encode_value`.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | A value read from a backup. |

**Returns**

| Type | Description |
| --- | --- |
| `object` | The preference's value, with bytes restored. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> decode_value({"bytes": "AAE="})
b'\x00\x01'
>>> decode_value([1, 2])
[1, 2]
```
{% endraw %}
