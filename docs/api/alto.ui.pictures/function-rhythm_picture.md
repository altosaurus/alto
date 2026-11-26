---
title: rhythm_picture
parent: alto.ui.pictures
api_module: alto.ui.pictures
package: alto.ui
permalink: /api/alto.ui.pictures/function-rhythm_picture/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def rhythm_picture(term: str) -> ValuePictures | None
```

{% endraw %}{% include api-source.html name="rhythm_picture" line=1033 %}{% raw %}

</div>

Render a single note, rest, tied pair, or beamed pair from an
equation term.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `term` | `str` | The stored term, with a tilde between tied notes or a bar between beamed notes. |

**Returns**

| Type | Description |
| --- | --- |
| `ValuePictures or None` | The engraved term, or None for an operator, numeral, or blank. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> rhythm_picture("eighth|eighth").beam_count
1
```
{% endraw %}
