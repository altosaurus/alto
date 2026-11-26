---
title: encode_value
parent: alto.learning.backup
api_module: alto.learning.backup
package: alto.learning
permalink: /api/alto.learning.backup/function-encode_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def encode_value(value: object) -> object
```

{% endraw %}{% include api-source.html name="encode_value" line=172 %}{% raw %}

</div>

Turn a saved preference into something JSON can hold.

Text, numbers, true and false and lists of them are kept as they
are. Bytes, which Qt settings can hold, become a small
dictionary with the bytes in base64, so `decode_value` can bring
them back.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The value of a preference. |

**Returns**

| Type | Description |
| --- | --- |
| `object` | The same value, or its encoded form. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     encode_value("dark"),
...     encode_value(5),
...     encode_value(["a", "b"]),
... )
('dark', 5, ['a', 'b'])
>>> encode_value(b"\x00\x01")
{'bytes': 'AAE='}
```
{% endraw %}
