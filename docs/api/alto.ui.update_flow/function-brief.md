---
title: brief
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-brief/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def brief(
    text: str,
    *,
    limit: int = 400,
) -> str
```

{% endraw %}{% include api-source.html name="brief" line=104 %}{% raw %}

</div>

Cut what a program printed down to what is worth showing in a
message: the end of it, without the blank space around it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | What the program printed. |
| `limit` | `int, default 400` | The most characters to keep. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The end of the text, at most `limit` characters long. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> brief("  one\ntwo  \n")
'one\ntwo'
>>> brief("x" * 10, limit=4)
'xxxx'
```
{% endraw %}
