---
title: inline
parent: alto.lessons.packs
api_module: alto.lessons.packs
package: alto.lessons
permalink: /api/alto.lessons.packs/function-inline/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def inline(text: str) -> str
```

{% endraw %}{% include api-source.html name="inline" line=87 %}{% raw %}

</div>

Escape plain text for a lesson page, turning ``**word**`` into bold
type for a term being defined.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | Plain text from a manifest. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | Simple HTML. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> inline("The **nut** & the bridge.")
'The <b>nut</b> &amp; the bridge.'
```
{% endraw %}
