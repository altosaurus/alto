---
title: is_newer
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-is_newer/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def is_newer(
    candidate: str,
    *,
    installed: str,
) -> bool
```

{% endraw %}{% include api-source.html name="is_newer" line=674 %}{% raw %}

</div>

Say whether one version is newer than another, comparing numbers and
not text, so 0.10.0 is newer than 0.9.0.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `candidate` | `str` | The version that may be newer. |
| `installed` | `str` | The version to compare it with. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the candidate is newer. False if it is the same or older, or if either is not a plain version. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     is_newer("0.10.0", installed="0.9.0"),
...     is_newer("v0.1.0", installed="0.0.0"),
... )
(True, True)
>>> (
...     is_newer("1.0", installed="1.0.0"),
...     is_newer("0.0.0", installed="0.1.0"),
... )
(False, False)
>>> is_newer("1.0.0", installed="unknown")
False
```
{% endraw %}
