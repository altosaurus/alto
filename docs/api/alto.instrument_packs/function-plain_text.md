---
title: plain_text
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-plain_text/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def plain_text(
    value: object,
    *,
    limit: int,
) -> bool
```

{% endraw %}{% include api-source.html name="plain_text" line=805 %}{% raw %}

</div>

Check that a manifest entry is nonblank plain text of a reasonable
length.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The manifest entry. |
| `limit` | `int` | The most characters allowed. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True for a nonblank string with no markup characters and at most ``limit`` characters. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     plain_text("Name the note.", limit=40),
...     plain_text("<b>Name</b>", limit=40),
...     plain_text(None, limit=40),
... )
(True, False, False)
```
{% endraw %}
