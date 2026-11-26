---
title: load_customs
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-load_customs/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def load_customs(text: str) -> list[CustomRecord]
```

{% endraw %}{% include api-source.html name="load_customs" line=1013 %}{% raw %}

</div>

Read the user's own schemes back, leaving out any that are not valid
and any beyond the limit.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | What `dump_customs` wrote. |

**Returns**

| Type | Description |
| --- | --- |
| `list of CustomRecord` | The valid schemes, each with its own key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     load_customs("not json"),
...     load_customs("[1, 2]"),
... )
([], [])
>>> one = record_of(
...     "custom-1",
...     name="A",
...     mode="single",
...     colors=["#2f6bd0"],
... )
>>> [
...     r["id"]
...     for r in load_customs(
...         dump_customs([one, one])
...     )
... ]  # a repeated key is dropped
['custom-1']
```
{% endraw %}
