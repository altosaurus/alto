---
title: category_tree
parent: alto.ui.home
api_module: alto.ui.home
package: alto.ui
permalink: /api/alto.ui.home/function-category_tree/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def category_tree(name: str) -> QTreeWidget
```

{% endraw %}{% include api-source.html name="category_tree" line=168 %}{% raw %}

</div>

Build a navigation tree with themed checkboxes and right-aligned
expansion arrows.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | `str` | Accessible name of the tree. |

**Returns**

| Type | Description |
| --- | --- |
| `QTreeWidget` | Empty tree ready for categories and exercises. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> category_tree("Decks").columnCount()
2
```
{% endraw %}
