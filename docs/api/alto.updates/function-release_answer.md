---
title: release_answer
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-release_answer/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def release_answer(
    status: int,
    *,
    text: str,
) -> Release | str
```

{% endraw %}{% include api-source.html name="release_answer" line=810 %}{% raw %}

</div>

Make sense of what came back when the latest release was asked for.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `status` | `int` | The HTTP status, or 0 if no answer came at all. |
| `text` | `str` | The body of the answer, or the reason there was none. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Release or str` | The release, or a sentence that says why there is none to offer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> release_answer(404, text="") == NO_RELEASE
True
>>> release_answer(
...     0, text="Name or service not known"
... )
'Alto could not reach GitHub: Name or service not known'
>>> release_answer(
...     403, text="rate limit exceeded"
... )
'GitHub answered with an error (403): rate limit exceeded'
```
{% endraw %}
