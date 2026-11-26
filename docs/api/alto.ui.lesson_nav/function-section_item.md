---
title: section_item
parent: alto.ui.lesson_nav
api_module: alto.ui.lesson_nav
package: alto.ui
permalink: /api/alto.ui.lesson_nav/function-section_item/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def section_item(
    text: str,
    *,
    palette: QPalette,
) -> QListWidgetItem
```

{% endraw %}{% include api-source.html name="section_item" line=43 %}{% raw %}

</div>

Make a section label for a list: small, gray capitals that cannot be
selected.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The heading, which is shown in capitals. |
| `palette` | `QPalette` | The palette to take the gray from. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QListWidgetItem` | The row. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> section_item(
...     "Scales & Keys", palette=QPalette()
... ).text()
'SCALES & KEYS'
```
{% endraw %}
