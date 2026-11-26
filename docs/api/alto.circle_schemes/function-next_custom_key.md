---
title: next_custom_key
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-next_custom_key/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def next_custom_key(customs: list[CustomRecord]) -> str
```

{% endraw %}{% include api-source.html name="next_custom_key" line=1109 %}{% raw %}

</div>

Return a key that none of the user's schemes has.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `customs` | `list of CustomRecord` | The user's own schemes. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | "custom-" and the smallest number that is free. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> taken = [
...     record_of(
...         "custom-1",
...         name="",
...         mode="single",
...         colors=[],
...     )
... ]
>>> next_custom_key([]), next_custom_key(taken)
('custom-1', 'custom-2')
```
{% endraw %}
