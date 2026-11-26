---
title: version_key
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-version_key/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def version_key(text: str) -> tuple[int, ...] | None
```

{% endraw %}{% include api-source.html name="version_key" line=639 %}{% raw %}

</div>

Turn a version, with or without the "v" of a tag, into numbers that
can be compared.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The version, such as "0.10.2" or "v1.0". |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of int or None` | Its numbers; None if it is not made only of numbers and dots, as a pre-release such as "1.0.0rc1" is not. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> version_key("v0.10.2"), version_key("1.0")
((0, 10, 2), (1, 0))
>>> (
...     version_key("1.0.0rc1") is None,
...     version_key("") is None,
...     version_key("unknown") is None,
... )
(True, True, True)
```
{% endraw %}
