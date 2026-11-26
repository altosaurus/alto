---
title: read_text
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_text/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_text(
    value: object,
    *,
    limit: int,
    what: str,
    where: str,
) -> str
```

{% endraw %}{% include api-source.html name="read_text" line=841 %}{% raw %}

</div>

Check one piece of plain text and return it trimmed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The manifest entry. |
| `limit` | `int` | The most characters allowed. Keyword-only. |
| `what` | `str` | What the entry is, for the message. Keyword-only. |
| `where` | `str` | Which lesson or step it belongs to, for the message. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The entry without surrounding space. |

**Raises**

- *ValueError*: If it is not nonblank plain text within the limit.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_text(
...     "  Hello ",
...     limit=10,
...     what="title",
...     where="lesson demo",
... )
'Hello'
```
{% endraw %}
