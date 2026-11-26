---
title: fetch_text
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-fetch_text/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def fetch_text(
    url: str,
    *,
    seconds: int,
) -> tuple[int, str]
```

{% endraw %}{% include api-source.html name="fetch_text" line=863 %}{% raw %}

</div>

Fetch a web address, waiting at most a number of seconds. It blocks,
so the interface runs it on another thread.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `url` | `str` | The address. |
| `seconds` | `int` | How long to wait for the server. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of int and str` | The HTTP status and the body. If the server was not reached, 0 and the reason. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fetch_text(
...     "http://127.0.0.1:9/", seconds=2
... )[0]  # nothing listens there
0
```
{% endraw %}
