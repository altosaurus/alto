---
title: open_preview
parent: alto.ui.database_page
api_module: alto.ui.database_page
package: alto.ui
permalink: /api/alto.ui.database_page/function-open_preview/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def open_preview(
    index: QModelIndex,
    *,
    names: dict[str, str],
    parent: QWidget,
    learner: Learner | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="open_preview" line=734 %}{% raw %}

</div>

Show the question behind a row of an answers table, if its record is
still stored.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `index` | `QModelIndex` | A cell of the row, in a model whose rows carry `ROW_ROLE` details. |
| `names` | `dict of str to str` | The title of each exercise, by class name. Keyword-only. |
| `parent` | `QWidget` | The widget the popup belongs to. Keyword-only. |
| `learner` | `Learner or None, default None` | The active profile, used to open this question's statistics. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> model = RowsModel(
...     ["Name"], rows=[[("Ada", "Ada")]]
... )
>>> open_preview(
...     model.index(0, 0),
...     names={},
...     parent=QWidget(),
... )  # a row with no stored question shows nothing
```
{% endraw %}
