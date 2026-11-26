---
title: dump_customs
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-dump_customs/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def dump_customs(records: list[CustomRecord]) -> str
```

{% endraw %}{% include api-source.html name="dump_customs" line=991 %}{% raw %}

</div>

Write the user's own schemes as text to save.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `records` | `list of CustomRecord` | The schemes. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | JSON. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dump_customs([])
'[]'
```
{% endraw %}
