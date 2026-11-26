---
title: subpage
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-subpage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def subpage(
    title: str,
    *,
    body: QWidget,
    back: Callable[[], object],
    fill: bool = False,
) -> QWidget
```

{% endraw %}{% include api-source.html name="subpage" line=1364 %}{% raw %}

</div>

Build a second-layer page: a Back button and title above a body.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `title` | `str` | The page's title. |
| `body` | `QWidget` | What the page shows. Keyword-only. |
| `back` | `callable` | Called when Back is clicked. Keyword-only. |
| `fill` | `bool, default False` | Let the body take all the room (so a long page can scroll) instead of leaving space below it. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QWidget` | The page. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> calls = []
>>> page_ = subpage(
...     "Clefs",
...     body=QWidget(),
...     back=lambda: calls.append("back"),
... )
>>> next(
...     b
...     for b in page_.findChildren(QToolButton)
...     if b.text() == "‹ Back"
... ).click()
>>> calls
['back']
```
{% endraw %}
